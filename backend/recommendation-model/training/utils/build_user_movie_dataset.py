import polars as pl
import torch
import numpy as np
import os
import time

current_dir = os.path.dirname(__file__)

# pytorch dataset for user,movie pairs with negative samping, negatives
# are looked up on the fly based on current neg set
# returns (user_id, pos_movie, negatives)
# two modes
#   - Coldstart: User Embedding from cold start tower
#   - Collaborative: User embedding from averaging movie embeddings 
class BuildUserMovieDataset(torch.utils.data.Dataset):
    def __init__(self, data_list, negatives_dict_or_df, mode: str, current_neg_set: int = 0, is_train: bool = True, num_negatives: int = 64) -> None:
        self.data = data_list  # List of (user_id, pos_movies_array) tuples
        self.current_neg_set = current_neg_set
        self.is_train = is_train
        self.num_negatives = num_negatives
        self.mode = mode  # 'coldstart' or 'collaborative'

        # Both modes iterate through all user-movie pairs (same structure)
        self.length = sum(len(pos_movies) for _, pos_movies in data_list)

        # Build index mapping: idx -> (user_idx, movie_idx)
        index_pairs = []
        for user_idx, (user_id, pos_movies) in enumerate(data_list):
            for movie_idx in range(len(pos_movies)):
                index_pairs.append((user_idx, movie_idx))
        self.index_map = np.array(index_pairs, dtype=np.int32)

        # For collaborative mode, also build user -> all_movies mapping
        # This allows training loop to look up user's other movies for averaging
        if mode == 'collaborative':
            self.user_to_movies = {}
            for user_id, pos_movies in data_list:
                self.user_to_movies[user_id] = pos_movies

        # Store reference to negatives_dict (shared between train/test)
        # Dict contains 1D arrays: [64 negatives] for current set
        self.negatives_dict = negatives_dict_or_df

    # Rebuild negatives_dict with a specific negative set (called each epoch)
    def reload_negatives(self, negatives_df, neg_set_id: int, num_negatives: int = 64):
        print(f"Loading negative set {neg_set_id}...")
        start_time = time.perf_counter()

        neg_columns = [f"neg_set{neg_set_id}_item{i}" for i in range(num_negatives)]

        for row in negatives_df.select(['userId'] + neg_columns).iter_rows(named=True):
            user_id = row['userId']
            # Store as 1D array: just this set's 64 negatives
            self.negatives_dict[user_id] = np.array(
                [row[col] for col in neg_columns],
                dtype=np.int64
            )

        print(f"Loaded negative set {neg_set_id} in {time.perf_counter() - start_time:.2f}s")
        self.current_neg_set = neg_set_id  # Update current set
        
    # helper function to change which negative set to use, refreshes
    # the negative dataset being seen to reduce overfitting
    def set_negative_set(self, neg_set_id: int) -> None:
        self.current_neg_set = neg_set_id
        print(f"Switched to negative set {neg_set_id}")

    def __len__(self):
        return self.length

    # Get all movies rated by user EXCEPT the specified movie.
    # Used in collaborative mode to get movies for averaging.
    def get_user_movies_except(self, user_id: int, exclude_movie: int) -> np.ndarray:
        if self.mode != 'collaborative':
            raise ValueError("get_user_movies_except only available in collaborative mode")

        all_movies = self.user_to_movies[user_id]
        return np.array([m for m in all_movies if m != exclude_movie], dtype=np.int64)

    def __getitem__(self, idx: int):
        # Both modes use the same structure now
        user_idx, movie_idx = self.index_map[idx]
        user_idx, movie_idx = int(user_idx), int(movie_idx)
        user_id, pos_movies = self.data[user_idx]

        # Look up negatives for this user
        neg_movies = self.negatives_dict[user_id]

        # Convert to tensors
        user_tensor = torch.as_tensor(user_id, dtype=torch.long)
        pos_tensor = torch.as_tensor(pos_movies[movie_idx], dtype=torch.long)
        neg_tensor = torch.from_numpy(neg_movies).long()

        return user_tensor, pos_tensor, neg_tensor

