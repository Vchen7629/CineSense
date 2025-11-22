import os
import lightgbm as lgb
import polars as pl
import numpy as np
from utils.cross_validation import tune_hyperparamaters_cv
from utils.extract_features import extract_reranker_features_batch
from post_training.reranker_model_evaluation import RerankerModelEval

class Reranker:
    def __init__(self, large_dataset: bool = False) -> None:
        current_dir = os.path.dirname(__file__)

        if large_dataset:
            # embeddings
            self.movie_embedding_path = os.path.join(current_dir, "datasets", "output", "movie_embeddings.npy")
            self.user_embedding_path = os.path.join(current_dir, "datasets", "output", "user-embeddings.npy")

            # precomputed features
            self.user_favorite_genres_path = os.path.join(current_dir, "datasets", "output", "user-top3-genres.csv")
            self.user_favorite_actor_dir_path = os.path.join(current_dir, "datasets", "output", "favorite-actor-directors.csv")
            self.movie_features_path = os.path.join(current_dir, "datasets", "output", "reranker-movie-features.csv")
            self.user_features_path = os.path.join(current_dir, "datasets", "output", "reranker-user-features.csv")

            # training data
            self.pos_ratings_path = os.path.join(current_dir, "datasets", "output", "user-positive-ratings.csv")
            self.neg_ratings_path = os.path.join(current_dir, "datasets", "output", "user-negative-ratings.csv")

            # save model path
            self.save_model_path = os.path.join(current_dir, "..", "api", "app", "model", "files", "reranker-model.txt")
        else:
            # embeddings
            self.movie_embedding_path = os.path.join(current_dir, "datasets", "output-small", "movie_embeddings.npy")
            self.user_embedding_path = os.path.join(current_dir, "datasets", "output-small", "user-embeddings.npy")

            # precomputed features
            self.user_favorite_genres_path = os.path.join(current_dir, "datasets", "output-small", "user-top3-genres.csv")
            self.user_favorite_actor_dir_path = os.path.join(current_dir, "datasets", "output-small", "favorite-actor-directors.csv")
            self.movie_features_path = os.path.join(current_dir, "datasets", "output-small", "reranker-movie-features.csv")
            self.user_features_path = os.path.join(current_dir, "datasets", "output-small", "reranker-user-features.csv")

            # training data
            self.pos_ratings_path = os.path.join(current_dir, "datasets", "output-small", "user-positive-ratings.csv")
            self.neg_ratings_path = os.path.join(current_dir, "datasets", "output-small", "user-negative-ratings.csv")

            # save model path
            self.save_model_path = os.path.join(current_dir, "..", "api", "app", "model", "files_small", "reranker-model.txt")
    
    # load all the necessary data for training
    def load_data(self) -> None:
        # embeddings
        self.movie_embeddings = np.load(self.movie_embedding_path)
        self.user_embeddings = np.load(self.user_embedding_path)

        # precomputed features
        self.movie_features_df = pl.read_csv(self.movie_features_path)
        self.user_features_df = pl.read_csv(self.user_features_path)
        self.user_favorite_genres_df = pl.read_csv(self.user_favorite_genres_path)
        self.user_favorite_actor_director_df = pl.read_csv(self.user_favorite_actor_dir_path)

        # training data
        self.pos_ratings_df = pl.read_csv(self.pos_ratings_path)
        self.neg_ratings_df = pl.read_csv(self.neg_ratings_path)
        self.ratings_df = pl.concat([self.pos_ratings_df, self.neg_ratings_df], how="vertical")

        print(f"loaded {len(self.ratings_df)} ratings")

    # prepare features for each (user, movie) pair
    # returns features, ratings, groups (number of movies per user)
    def prepare_training_data(self) -> None:
        movie_features_subset = self.movie_features_df.drop("movie_idx")
        
        # join ratings with movie user features 
        ratings_with_features_df = (
            self.ratings_df
            .join(movie_features_subset, on="tmdbId", how="left")
            .join(self.user_features_df, on="userId", how="left")
            .join(self.user_favorite_genres_df, on="userId", how="left")
            .join(self.user_favorite_actor_director_df, on="userId", how="left")
            .sort("userId")
        )

        print("Extracting features...")

        self.X = extract_reranker_features_batch(self.user_embeddings, self.movie_embeddings, ratings_with_features_df)

        # extract ratings
        self.y = ratings_with_features_df['rating'].to_numpy().astype(np.int32)

        # compute groups (number of movies per user)
        print("Computing groups...")
        groups_df = ratings_with_features_df.group_by('userId').agg(pl.len().alias('count')).sort('userId')
        self.groups = groups_df['count'].to_numpy().astype(np.int32)

    def train(self, params=None):
        num_users = len(self.groups)
        train_users = int(num_users * 0.8)

        # calculate sample boundaries
        train_samples = sum(self.groups[:train_users])

        # split train validation groups
        X_train = self.X[:train_samples]
        y_train = self.y[:train_samples]
        groups_train = self.groups[:train_users]

        X_val = self.X[train_samples:]
        y_val = self.y[train_samples:]
        groups_val = self.groups[train_users:]

        print(f"Train: {len(X_train)} samples, {len(groups_train)} users")
        print(f"Val: {len(X_val)} samples, {len(groups_val)} users")

        # use provided params or defaults
        if params is None:
            params = {
              'n_estimators': 100,
              'learning_rate': 0.05,
              'num_leaves': 31,
              'max_depth': 6,
              'min_child_samples': 20,
            }

        # Create LightGBM datasets
        train_data = lgb.Dataset(X_train, label=y_train, group=groups_train)
        val_data = lgb.Dataset(X_val, label=y_val, group=groups_val, reference=train_data)

        # Model params - explicitly optimize for NDCG@10
        model_params = {
            'objective': 'lambdarank',
            'metric': 'ndcg',
            'ndcg_eval_at': [10],  # Evaluate at multiple k, optimize for these
            'label_gain': [0, 1, 2, 3, 5, 7, 10, 13, 17, 22, 28],  # label gain to emphasize higher ratings (4, 5) more
            'boosting_type': 'gbdt',
            'random_state': 42,
            'verbosity': 1,
            **params
        }

        # Train using lgb.train for explicit control
        self.model = lgb.train(
            model_params,
            train_data,
            num_boost_round=params['n_estimators'],
            valid_sets=[val_data],
            valid_names=['valid_0'],
            callbacks=[
                lgb.log_evaluation(period=10),
                lgb.early_stopping(stopping_rounds=10)
            ]
        )

        return self.model


if __name__ == "__main__":
    reranker = Reranker(large_dataset=False)

    print("loading data")
    reranker.load_data() # load data

    print("preparing training data")
    reranker.prepare_training_data() # prepare train data

    # hyper param tuning with 5-fold GroupKFold CV
    best_params = tune_hyperparamaters_cv(groups=reranker.groups, X=reranker.X, y=reranker.y, n_splits=5)

    model = reranker.train(params=best_params)
    print("training complete!")

    # evaluation stage
    eval = RerankerModelEval(
        model, 
        reranker.movie_embeddings, 
        reranker.user_embeddings, 
        reranker.movie_features_df,
        reranker.user_features_df,
        reranker.user_favorite_genres_df,
        reranker.user_favorite_actor_director_df,
        reranker.pos_ratings_df,
        reranker.neg_ratings_df
    )

    print("evaluating hitrate")
    # evaluate hit rate with leave one out
    eval.hitrate(k=10, num_negatives=99)

    # save model (txt)
    model.save_model(reranker.save_model_path)

    print("done")