import torch
import torch.nn.functional as f
import numpy as np
from collections import defaultdict
import polars as pl
from shared.load_genres import load_genre_mappings
from shared.split_hard_random_candidates import split_hard_random_candidates

# Model Eval Class for evaluating cold start model performance on test dataset
# using methods like hitrate@k
class ColdStartEval:
    def __init__(
            self, 
            test_dataset, 
            device: str, 
            movie_tower, 
            user_tower, 
            num_eval_neg, 
            k: int = 0,
            user_genres_path: str = None,
            movie_metadata_path: str = None
        ) -> None:
        self.k = k
        self.device = device
        self.user_tower = user_tower
        self.movie_tower = movie_tower
        self.test_dataset = test_dataset
        self.num_eval_negatives = num_eval_neg

        # store all movies
        self.all_movies = self._extract_all_movies(test_dataset)
        # build user positive movie mapping
        self.user_to_movies = self._build_user_to_movies(test_dataset)

        # load genre mappings for cold start eval
        self.user_to_genres = None
        self.movie_to_genres = None
        if user_genres_path and movie_metadata_path:
            self.user_to_genres, self.movie_to_genres = load_genre_mappings(user_genres_path, movie_metadata_path)

    # Collect all unique movie IDs (positive + negatives).
    def _extract_all_movies(self, dataset):
        movies = set()
        for _, pos, neg in dataset:
            movies.add(int(pos))
            movies.update(map(int, neg.tolist()))
        return np.array(list(movies), dtype=np.int64)

    def _build_user_to_movies(self, dataset):
        """Build user -> [positive_movies] mapping from dataset."""
        user_to_movies = defaultdict(list)
        for user, pos, _ in dataset:
            user_to_movies[int(user)].append(int(pos))
        return user_to_movies
    
    def _sample_negatives(self, user_id: int, pos_movie: int, cold_start: bool, genre_ratio: float):
        # get all candidates (exclude positive movie)
        all_candidates = np.setdiff1d(self.all_movies, [pos_movie])

        # personalized evaluation mode
        if not cold_start or self.user_to_genres is None:
            if len(all_candidates) >= self.num_eval_negatives:
                return np.random.choice(all_candidates, self.num_eval_negatives, replace=False)
            else:
                return all_candidates

        # cold start mode: sample genre_ratio from top-3 genres, rest random
        user_genres = self.user_to_genres.get(user_id, set())
        if not user_genres:
            # fallback to random if user has no genre data
            if len(all_candidates) >= self.num_eval_negatives:
                return np.random.choice(all_candidates, self.num_eval_negatives, replace=False)
            else:
                return all_candidates
        
        genre_candidates, num_genre, num_random = split_hard_random_candidates(all_candidates, self.movie_to_genres, user_genres, self.num_eval_negatives, genre_ratio)
        
        # sample genre-matched negatives
        if len(genre_candidates) >= num_genre:
            genre_sample = np.random.choice(genre_candidates, num_genre, replace=False)
        else:
            # not enough genre candidates, use what we have
            genre_sample = genre_candidates
            num_random = self.num_eval_negatives - len(genre_sample)

        # sample random negatives (excluding already sampled genre negatives)
        non_genre_candidates = np.setdiff1d(all_candidates, genre_sample)
        if len(non_genre_candidates) >= num_random:
            random_sample = np.random.choice(non_genre_candidates, num_random, replace=False)
        else:
            random_sample = non_genre_candidates[:num_random]

        # combine and shuffle
        sampled_negatives = np.concatenate([genre_sample, random_sample])
        np.random.shuffle(sampled_negatives)

        return sampled_negatives

    # HitRate@K metric, measures the percentage of time the correct movie appears in the top k
    # recommendations returned by the model.
    @torch.no_grad()
    def hitrate(self, cold_start: bool = True, genre_ratio: float = 0.8):
        hits = 0
        total = 0

        mode = "Cold Start" if cold_start else "Personalized"

        # Iterate over users
        for user, pos_movies in self.user_to_movies.items():
            user_tensor = torch.tensor([user], dtype=torch.long, device=self.device)
            user_emb = f.normalize(self.user_tower(user_tensor), dim=1)

            for pos_movie in pos_movies:
                # sample negatives based on mode
                sampled_negatives = self._sample_negatives(user, pos_movie, cold_start, genre_ratio)

                # create evaluation batch (1 positive + sampled negatives)
                eval_batch = torch.tensor([pos_movie] + sampled_negatives.tolist(), dtype=torch.long, device=self.device)
                movie_embs = self.movie_tower(eval_batch)
                movie_embs = f.normalize(movie_embs, dim=1)

                # compute dot product (similarity) for user's embedding and all movie embeddings
                scores = torch.matmul(user_emb, movie_embs.T).squeeze(0) # (num_movies,)
                # compute top k movies returned 
                topk_indices = torch.topk(input=scores, k=self.k).indices
                topk_movies = eval_batch[topk_indices]

                # Hit if positive movie is in top K
                if pos_movie in topk_movies:
                    hits += 1

                total += 1

        hit_rate = hits / total
        print(f"HitRate@{self.k}: ({mode}) {hit_rate:.4f}")

        return hit_rate