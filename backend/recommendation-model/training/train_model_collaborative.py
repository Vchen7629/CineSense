import torch
from model.movie_tower import MovieTower
from info_nce import InfoNCE
from torch.utils.data import DataLoader
from utils.train_test_split import TrainTest
from post_training.candidate_gen_model_evaluation import CandidateGenerationModelEval
from post_training.save_model_files import SaveModel
from post_training.generate_user_embeddings import GenerateUserEmbeddings
import polars as pl
import time
from shared.path_config import path_helper

# for the "not enough SMs to use max_autotune_gemm mode" error
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch._inductor')

# Silence CUDAGraph dynamic shapes warning (expected for collaborative filtering with variable user history lengths)
torch._inductor.config.triton.cudagraph_dynamic_shape_warn_limit = None

# enable fastest backend
#torch.backends.cudnn.benchmark = True

class TrainPersonalizedModel():
    def __init__(self, large_dataset: bool = False):
        # embeddings config
        self.embedding_dim = 512 # size of embedding vector

        if large_dataset:
            # config
            self.num_movies = 64543
            self.batch_size = 4096
            paths = path_helper(large_dataset=large_dataset)

            self.pos_ratings_path = paths.pos_ratings_path
            neg_ratings_path = paths.neg_ratings_path
        else:
            # config
            self.num_movies = 9632
            self.batch_size = 256

            paths = path_helper(large_dataset=large_dataset)

            self.pos_ratings_path = paths.pos_ratings_path
            neg_ratings_path = paths.user_collaborative_negatives_path

        self.neg_df = pl.read_csv(neg_ratings_path)
        self.traintest = TrainTest(self.pos_ratings_path, mode='collaborative')

        self.movie_tower = MovieTower(
            embedding_dim=self.embedding_dim,
            device="cuda",
            large_dataset=large_dataset
        )

        # Compile models for faster execution
        if large_dataset:
            self.movie_tower = torch.compile(self.movie_tower, mode='max-autotune')
        else: 
            self.movie_tower = torch.compile(self.movie_tower, mode='reduce-overhead')

        # loss function, higher temperature means it generalizes better but might train slower
        # plus loss will be lower. Lower temperature means it will train better to my dataset
        # but risk overfitting.
        self.loss_fn = InfoNCE(temperature=0.07, negative_mode='paired')

        # backpropagation optimizer with fused implementation for faster updates
        self.optimizer = torch.optim.Adam(
            self.movie_tower.parameters(),
            lr=0.001,
            fused=True  # Use fused kernel for faster parameter updates
        )

        #self.optimizer = torch.optim.Adam(
        #    list(self.user_tower.parameters()) + list(self.movie_tower.parameters()),
        #    lr=1e-3,
        #    fused=True  # Use fused kernel for faster parameter updates
        #)

    def data_loader(self):
        # Build train/test datasets
        print("Building train/test datasets")
        self.train_dataset, self.test_dataset = self.traintest.split(self.neg_df)

        # 4096 batch size seems to be the limit on my rtx 5070 with 12 gb vram
        # note: higher batches means less training time but less performance
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.batch_size, 
            shuffle=True,
            num_workers=4,
            pin_memory=True,
            prefetch_factor=2
        )
        return train_loader
    
    # train the model with loss function
    def train_model(self, dataloader, num_epochs):
        epoch_losses = []
        scaler = torch.amp.GradScaler()

        for epoch in range(num_epochs):
            start_time = time.perf_counter()
            # Rotate to the next negative set (0-9)
            neg_set_id = epoch % 10
            if epoch > 0:
                print(f"\nRotating to negative set {neg_set_id} for epoch {epoch}...")
                self.train_dataset.reload_negatives(self.traintest.negatives_df, neg_set_id)

            epoch_loss_sum = 0.0
            num_batches = 0

            #print(f"got dataloader for for epoch {epoch}...")
            for user_tensor, pos_movie_tensor, neg_movie_tensor in dataloader:
                # reset gradients from previous batch
                self.optimizer.zero_grad(set_to_none=True)

                user_tensor = user_tensor.to("cuda", non_blocking=True)
                pos_movie_tensor = pos_movie_tensor.to("cuda", non_blocking=True)
                neg_movie_tensor = neg_movie_tensor.to("cuda", non_blocking=True)

                with torch.amp.autocast(device_type="cuda", dtype=torch.bfloat16):
                    batch_size = len(user_tensor)

                    all_user_movies = []
                    split_sizes = []  # Track how many movies per user

                    for i in range(batch_size):
                        user_id = user_tensor[i].item()
                        pos_movie = pos_movie_tensor[i].item()

                        # Get user's rated movies (excluding current positive)
                        other_movies = self.train_dataset.get_user_movies_except(user_id, pos_movie)

                        if len(other_movies) > 50:
                            other_movies = other_movies[-50:]

                        all_user_movies.extend(other_movies.tolist())
                        split_sizes.append(len(other_movies))
                
                    # Combine: user_movies + pos + neg
                    num_user_movies = len(all_user_movies)
                    pos_neg_batch = torch.cat([pos_movie_tensor.unsqueeze(1), neg_movie_tensor], dim=1)  # (B, 65)

                    if num_user_movies > 0:
                        user_movies_tensor = torch.tensor(all_user_movies, device="cuda", dtype=torch.long)
                        all_movie_ids = torch.cat([user_movies_tensor, pos_neg_batch.view(-1)])
                    else:
                        all_movie_ids = pos_neg_batch.view(-1)

                    all_movie_embs = self.movie_tower(all_movie_ids)

                    # Split embeddings back
                    if num_user_movies > 0:
                        user_movie_embs = all_movie_embs[:num_user_movies]  # User's rated movies
                        pos_neg_embs = all_movie_embs[num_user_movies:]     # Pos + neg
                    else:
                        pos_neg_embs = all_movie_embs

                    # Create user embeddings by averaging
                    user_embeddings = []
                    start_idx = 0

                    for size in split_sizes:
                        if size == 0:
                            # User only has 1 rating (use zero embedding)
                            user_embeddings.append(torch.zeros(self.embedding_dim, device="cuda"))
                        else:
                            # Average this user's movie embeddings
                            user_emb = user_movie_embs[start_idx:start_idx + size].mean(dim=0)
                            user_embeddings.append(user_emb)
                        start_idx += size

                    u_emb = torch.stack(user_embeddings)  # (batch_size, embedding_dim)

                    # Step 5: Extract pos and neg embeddings
                    pos_neg_embs = pos_neg_embs.view(batch_size, 65, -1)
                    pos_emb = pos_neg_embs[:, 0, :]   # (batch_size, embedding_dim)
                    neg_emb = pos_neg_embs[:, 1:, :]  # (batch_size, 64, embedding_dim)

                    loss = self.loss_fn(u_emb, pos_emb, neg_emb)

                scaler.scale(loss).backward()
                scaler.step(self.optimizer)
                scaler.update()

                epoch_loss_sum += loss.detach()
                num_batches += 1


            avg_loss = (epoch_loss_sum / num_batches).item()
            epoch_losses.append(avg_loss)

            print(f"Epoch took: {time.perf_counter() - start_time:.4f} seconds")
            print(f"Epoch {epoch+1}/{num_epochs}: loss={avg_loss:.4f}")
            

        #plt.figure(figsize=(8, 5))
        #plt.plot(range(1, num_epochs + 1), epoch_losses, marker='o')
        #plt.xlabel("Epoch")
        #plt.ylabel("Loss")
        #plt.title("Training Loss vs. Epochs")
        #plt.grid(True)
        #plt.show()

if __name__ == "__main__":
    train_start_time = time.perf_counter()

    train = TrainPersonalizedModel(large_dataset=False)
    print("TrainModel initialized successfully")

    # loading train test split datasets
    train_loader = train.data_loader()

    # training model using train dataset
    train.train_model(train_loader, num_epochs=25)

    end_time = time.perf_counter()
    print(f"Elapsed time: {time.perf_counter() - train_start_time:.4f} seconds")
    
    SaveModel(
        user_tower=None, 
        movie_tower=train.movie_tower,
        num_movies=train.num_movies,
        personalized=True
    ).save_all(save_to_local_db=True)

    # create user embedding file for model evaluation
    user_embeddings = GenerateUserEmbeddings(movie_tower=train.movie_tower)
    user_embeddings.generate_all_user_embeddings()

    # Run evaluations (movie_tower no longer needed, uses pre-computed embeddings)
    evaluator = CandidateGenerationModelEval(large_dataset=False)

    testing_configs = [
        {'num_similar_users': 30, 'candidate_pool': 300},
        {'num_similar_users': 50, 'candidate_pool': 200},
        {'num_similar_users': 50, 'candidate_pool': 300},
        {'num_similar_users': 50, 'candidate_pool': 400},
        {'num_similar_users': 100, 'candidate_pool': 300},
        {'num_similar_users': 200, 'candidate_pool': 500},
    ]

    for config in testing_configs:
        hitrate_user_user = evaluator.leave_one_out_evaluation_with_user_similarity(
            k=300,
            num_similar_users=config['num_similar_users'],
            candidate_pool_size=config['candidate_pool']
        )

        print(f"User-user approach: {hitrate_user_user:.4f} ({hitrate_user_user*100:.2f}%)")



    