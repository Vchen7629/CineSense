import time
import polars as pl
import numpy as np
from .build_user_movie_dataset import BuildUserMovieDataset
from typing import List

class TrainTest:
    def __init__(self, ratings_csv_path: str, mode: str) -> None:
        start = time.perf_counter()
        self.ratings_df = pl.scan_csv(ratings_csv_path)
        self.mode = mode
        print(f"Loaded ratings in {time.perf_counter() - start:.2f}s")

        # pregroup by userId and sort to ensure deterministic ordering
        self.user_groups = (
            self.ratings_df.group_by("userId")
            .agg(pl.col("movie_idx"))
        )

        # negatives diction
        self.negatives_dict = None
    
    # function to process data in batches instead of all at once in memory
    # to avoid OOM
    def _process_batches(
        self,
        test_size: float,
        batch: pl.DataFrame,
        train_data: List,
        test_data: List
    ):
        rng = np.random.RandomState(42)

        for row in batch.iter_rows(named=True):
            user = row['userId']
            pos_movies = row['movie_idx']  # This is a list from the aggregation

            n_movies = len(pos_movies)

            # if user only rated one movie keep it all in train_data
            if n_movies < 2:
                train_data.append((user, np.array(pos_movies, dtype=np.int64)))
                continue

            # calculating the number of items in the test dataset
            n_test = max(1, int(n_movies * test_size))
            # Shuffle indices
            indices = rng.permutation(n_movies)
            test_idx, train_idx = indices[:n_test], indices[n_test:]

            # Build train/test data sets as user groups (one entry per user)
            # Store arrays of movies instead of individual samples
            train_movies = np.array([pos_movies[i] for i in train_idx], dtype=np.int64)
            test_movies = np.array([pos_movies[i] for i in test_idx], dtype=np.int64)

            train_data.append((user, train_movies))
            test_data.append((user, test_movies))

    # split ratings into train/test sets 
    def split(self, negatives_df: pl.DataFrame, num_negatives: int = 64, test_size: float = 0.2):
        train_data, test_data = [], []

        print(f"Building negatives lookup table (set 0) for {len(negatives_df)} users...")
        start_time = time.perf_counter()
        negatives_dict = {}

        # Get only set 0 initially
        neg_columns = [f"neg_set0_item{i}" for i in range(num_negatives)]

        for row in negatives_df.select(['userId'] + neg_columns).iter_rows(named=True):
            user_id = row['userId']
            # Store as 1D array: just 64 negatives for set 0
            negatives_dict[user_id] = np.array(
                [row[col] for col in neg_columns],
                dtype=np.int64
            )

        print(f"Built negatives lookup in {time.perf_counter() - start_time:.2f}s")

        start = time.perf_counter()
        for batch in self.user_groups.collect(streaming=True).iter_slices(n_rows=10000):
            self._process_batches(test_size, batch, train_data, test_data)

        print(f"Build train test split took {time.perf_counter() - start:.4f}s")

        # Store negatives_df for later reloading
        self.negatives_df = negatives_df

        # Pass negatives_dict (shared) to both datasets
        train_dataset = BuildUserMovieDataset(train_data, negatives_dict, current_neg_set=0, is_train=True, mode=self.mode)
        test_dataset = BuildUserMovieDataset(test_data, negatives_dict, current_neg_set=0, is_train=False, mode=self.mode)

        return train_dataset, test_dataset