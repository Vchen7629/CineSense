import torch.nn as nn
import torch
import numpy as np

# Creating Embeddings for movie tower, includes features such
# as movie title, genre, returns tensor of shape [num_movies, 64]
class MovieTower(nn.Module):
    def __init__(self, embedding_dim: int, device="cuda", large_dataset: bool = False) -> None:
        super().__init__()
        # config
        self.embedding_dim = embedding_dim
        self.device = device

        if large_dataset:
            titles = np.load("datasets/output/title_embeddings.npy")
            genres = np.load("datasets/output/genre_mlb.npy")
            metadata_sentence = np.load("datasets/output/overview_dir_cast_embeddings.npy")
            year = np.load("datasets/output/movie_year.npy").reshape(-1, 1)  # Reshape to [num_movies, 1]
        else:
            titles = np.load("datasets/output-small/title_embeddings.npy")
            genres = np.load("datasets/output-small/genre_mlb.npy")
            metadata_sentence = np.load("datasets/output-small/overview_dir_cast_embeddings.npy")
            year = np.load("datasets/output-small/movie_year.npy").reshape(-1, 1)  # Reshape to [num_movies, 1]

        # Store as parameters (trainable) or tensors (fixed)
        self.title_tensor = nn.Parameter(torch.tensor(titles, dtype=torch.float, device=device))
        self.genre_tensor = nn.Parameter(torch.tensor(genres, dtype=torch.float, device=device))
        self.year_tensor = nn.Parameter(torch.tensor(year, dtype=torch.float, device=device))
        self.metadata_sentence_tensor = nn.Parameter(torch.tensor(metadata_sentence, dtype=torch.float, device=device))

        self.title_linear = self.linear_layer(tensor=self.title_tensor)
        self.genre_linear = self.linear_layer(tensor=self.genre_tensor)
        self.year_linear = self.linear_layer(tensor=self.year_tensor)
        self.metadata_sentence_linear = self.linear_layer(tensor=self.metadata_sentence_tensor)

        self.relu = nn.ReLU()

        self.projector = torch.nn.Linear(self.embedding_dim * 4, self.embedding_dim, device="cuda")

    # linear layer to reduce dimensionality by reducing it to embedding_dim
    def linear_layer(self, tensor) -> torch.nn.Linear:
        num_features = tensor.shape[1]
        linear = torch.nn.Linear(num_features, self.embedding_dim, device=self.device)

        return linear
    
    def forward(self, movie_ids) -> torch.Tensor:
        # Index into all precomputed embeddings (fast!)
        title_features = self.title_tensor[movie_ids]  # [batch, 384]
        genre_features = self.genre_tensor[movie_ids]  # [batch, num_genres]
        year_features = self.year_tensor[movie_ids] 
        metadata_sentence_features = self.metadata_sentence_tensor[movie_ids]

        # Project title/genre to embedding_dim
        title_emb = self.relu(self.title_linear(title_features))
        genre_emb = self.relu(self.genre_linear(genre_features))
        year_emb = self.relu(self.year_linear(year_features))
        metadata_sentence_emb = self.relu(self.metadata_sentence_linear(metadata_sentence_features))

        # Normalize all embeddings to prevent title from dominating
        title_emb = torch.nn.functional.normalize(title_emb, p=2, dim=1)
        genre_emb = torch.nn.functional.normalize(genre_emb, p=2, dim=1)
        year_emb = torch.nn.functional.normalize(year_emb, p=2, dim=1)
        metadata_sentence_emb = torch.nn.functional.normalize(metadata_sentence_emb, p=2, dim=1)

        # combine them along the feature dimension returns shape [batch, embedding_dim * 4]
        # or [title_features | genre_features | year_features | metadata_senetence_features]
        combined_emb = torch.cat([title_emb, genre_emb, year_emb, metadata_sentence_emb], dim=1)

        # Final linear layer to project back down to 512 dimensions since user
        # tower is also 512 dimensions
        movie_emb = self.projector(combined_emb)

        return movie_emb