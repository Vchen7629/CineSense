import os
import torch
from model.cold_start_user_tower import ColdStartUserTower
from model.movie_tower import MovieTower
from info_nce import InfoNCE
from torch.utils.data import DataLoader
from utils.train_test_split import TrainTest
from post_training.cold_start_evaluation import ColdStartEval
from post_training.save_model import SaveModel
import polars as pl
import numpy as np
import time

# for the "not enough SMs to use max_autotune_gemm mode" error
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch._inductor')

# enable fastest backend
#torch.backends.cudnn.benchmark = True

current_dir = os.path.dirname(__file__)

class TrainColdStartModel():
    def __init__(self, large_dataset: bool = False):
        # embeddings config
        embedding_dim = 512 # size of embedding vector

        if large_dataset:
            # config
            self.num_movies = 64543
            self.batch_size = 4096

            pos_ratings_path = os.path.join(current_dir, "datasets", "output", "user-positive-ratings.csv")
            neg_ratings_path = os.path.join(current_dir, "datasets", "output", "user-cold-start-negatives.csv")
            self.user_genres_path = os.path.join(current_dir, "datasets", "output", "user-top3-genres.csv")
            self.movie_metadata_path = os.path.join(current_dir, "datasets", "output", "movie-metadata.csv")

            self.neg_df = pl.read_csv(neg_ratings_path)
        else:
            # config
            self.num_movies = 9632
            self.batch_size = 256

            pos_ratings_path = os.path.join(current_dir, "datasets", "output-small", "user-positive-ratings.csv")
            neg_ratings_path = os.path.join(current_dir, "datasets", "output-small", "user-cold-start-negatives.csv")
            self.user_genres_path = os.path.join(current_dir, "datasets", "output-small", "user-top3-genres.csv")
            self.movie_metadata_path = os.path.join(current_dir, "datasets", "output-small", "movie-metadata.csv")

            self.neg_df = pl.read_csv(neg_ratings_path)

        self.traintest = TrainTest(pos_ratings_path, mode='coldstart')

        self.user_tower = ColdStartUserTower(
            user_csv_path=pos_ratings_path,
            embedding_dim=embedding_dim, 
            device="cuda",
            large_dataset=large_dataset
        )
        self.movie_tower = MovieTower(
            embedding_dim=embedding_dim,
            device="cuda",
            large_dataset=large_dataset
        )

        # Compile models for faster execution
        if large_dataset:
            self.user_tower = torch.compile(self.user_tower, mode='max-autotune')
            self.movie_tower = torch.compile(self.movie_tower, mode='max-autotune')
        else: 
            self.user_tower = torch.compile(self.user_tower, mode='reduce-overhead')
            self.movie_tower = torch.compile(self.movie_tower, mode='reduce-overhead')

        # loss function, higher temperature means it generalizes better but might train slower
        # plus loss will be lower. Lower temperature means it will train better to my dataset
        # but risk overfitting.
        self.loss_fn = InfoNCE(temperature=0.07, negative_mode='paired')

        # backpropagation optimizer with fused implementation for faster updates
        self.optimizer = torch.optim.Adam(
            list(self.user_tower.parameters()) + list(self.movie_tower.parameters()),
            lr=0.001,
            fused=True  # Use fused kernel for faster parameter updates
        )

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
            for batch_idx, (user_tensor, pos_movie_tensor, neg_movie_tensor) in enumerate(dataloader):
                # reset gradients from previous batch
                self.optimizer.zero_grad(set_to_none=True)

                user_tensor = user_tensor.to("cuda", non_blocking=True)
                pos_movie_tensor = pos_movie_tensor.to("cuda", non_blocking=True)
                neg_movie_tensor = neg_movie_tensor.to("cuda", non_blocking=True)

                with torch.amp.autocast(device_type="cuda", dtype=torch.bfloat16):
                    # Combine positive + negatives into one batch
                    # pos_movie_tensor returns (batch_size, ) -> unsqueeze(1) -> (batch_size, 1)
                    # This is because each sample is 1 positive, 64 negatives
                    movie_batch = torch.cat([pos_movie_tensor.unsqueeze(1), neg_movie_tensor], dim=1)
                    B, N = movie_batch.shape  # batch_size, 1+num_negatives

                    # compute embeddings for all movies in the batch
                    # movie_batch is (256, 65) and .view flattens it to 1D (256 * 65, ) -> (16,640,)
                    # We need to do this because we need to normalize across embedding vector not indices
                    movie_emb = self.movie_tower(movie_batch.view(-1))
                    #u_emb = self.user_tower(user_tensor)
                    u_emb = self.user_tower(user_tensor)

                    # reshape back to (B, N, D) to extract positive and negatives
                    movie_emb = movie_emb.view(B, N, -1)

                    # our positive embedding is always the first value so [:, 0, :] works
                    pos_emb = movie_emb[:, 0, :]
                    # negative embeddings are values at index 1 - 65 so we do [:, 1:, :]
                    neg_emb = movie_emb[:, 1:, :]

                    loss = self.loss_fn(u_emb, pos_emb, neg_emb)

                    # Debug: Check for NaN/Inf
                    if torch.isnan(loss) or torch.isinf(loss):
                        print(f"\nNaN/Inf detected in batch {num_batches}!")
                        print(f"u_emb - min: {u_emb.min().item():.4f}, max: {u_emb.max().item():.4f}, has_nan: {torch.isnan(u_emb).any()}, has_inf: {torch.isinf(u_emb).any()}")
                        print(f"pos_emb - min: {pos_emb.min().item():.4f}, max: {pos_emb.max().item():.4f}, has_nan: {torch.isnan(pos_emb).any()}, has_inf: {torch.isinf(pos_emb).any()}")
                        print(f"neg_emb - min: {neg_emb.min().item():.4f}, max: {neg_emb.max().item():.4f}, has_nan: {torch.isnan(neg_emb).any()}, has_inf: {torch.isinf(neg_emb).any()}")
                        print(f"loss: {loss.item()}")

                        # Check norms
                        u_norms = torch.linalg.norm(u_emb, dim=1)
                        pos_norms = torch.linalg.norm(pos_emb, dim=1)
                        neg_norms = torch.linalg.norm(neg_emb, dim=2)
                        print(f"u_emb norms - min: {u_norms.min().item():.4f}, max: {u_norms.max().item():.4f}")
                        print(f"pos_emb norms - min: {pos_norms.min().item():.4f}, max: {pos_norms.max().item():.4f}")
                        print(f"neg_emb norms - min: {neg_norms.min().item():.4f}, max: {neg_norms.max().item():.4f}")
                        raise RuntimeError("NaN/Inf in loss!")

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

    train = TrainColdStartModel(large_dataset=False)
    print("TrainModel initialized successfully")

    # loading train test split datasets
    train_loader = train.data_loader()

    # training model using train dataset
    train.train_model(train_loader, num_epochs=25)

    end_time = time.perf_counter()
    print(f"Elapsed time: {time.perf_counter() - train_start_time:.4f} seconds")

    eval_start_time = time.perf_counter()

    eval = ColdStartEval(
        train.test_dataset,
        device="cuda",
        movie_tower=train.movie_tower,
        user_tower=train.user_tower,
        num_eval_neg=99,
        k=10,
        user_genres_path=train.user_genres_path,
        movie_metadata_path=train.movie_metadata_path,
    )

    # Production evaluation: 80% from user's top-3 genres, 20% random
    hitrate = eval.hitrate(cold_start=True, genre_ratio=0.8)
    print(f"hitrate: {hitrate}")
    print(f"Eval took: {time.perf_counter() - eval_start_time:.4f} seconds")

    # save models after training

    config = {
        "dbname": "example_db",
        "user": "postgres",
        "password": "password",
        "host": "localhost",
        "port": 5432
    }
    
    SaveModel(
        user_tower=train.user_tower, 
        movie_tower=train.movie_tower,
        num_movies=train.num_movies,
        personalized=False
    ).save_all(save_to_db=True, db_config=config)


    