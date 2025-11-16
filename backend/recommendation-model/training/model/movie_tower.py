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
        else:
            titles = np.load("datasets/output-small/title_embeddings.npy")
            genres = np.load("datasets/output-small/genre_mlb.npy")

        # Store as parameters (trainable) or tensors (fixed)
        self.title_tensor = nn.Parameter(torch.tensor(titles, dtype=torch.float, device=device))
        self.genre_tensor = nn.Parameter(torch.tensor(genres, dtype=torch.float, device=device))

        self.title_linear = self.linear_layer(tensor=self.title_tensor)
        self.genre_linear = self.linear_layer(tensor=self.genre_tensor)

        self.relu = nn.ReLU()

        self.projector = torch.nn.Linear(self.embedding_dim * 2, self.embedding_dim, device="cuda")

    # linear layer to reduce dimensionality by reducing it to embedding_dim
    def linear_layer(self, tensor) -> torch.nn.Linear:
        num_features = tensor.shape[1]
        linear = torch.nn.Linear(num_features, self.embedding_dim, device=self.device)

        return linear
    
    def forward(self, movie_ids) -> torch.Tensor:
        # Index into all precomputed embeddings (fast!)
        title_features = self.title_tensor[movie_ids]  # [batch, 384]
        genre_features = self.genre_tensor[movie_ids]  # [batch, num_genres]

        # Project title/genre to embedding_dim
        title_emb = self.relu(self.title_linear(title_features))
        genre_emb = self.relu(self.genre_linear(genre_features))

        # Normalize all embeddings to prevent title from dominating
        title_emb = torch.nn.functional.normalize(title_emb, p=2, dim=1)
        genre_emb = torch.nn.functional.normalize(genre_emb, p=2, dim=1)

        # combine them along the feature dimension returns shape [batch, embedding_dim * 2]
        # or [title_features | genre_features]
        combined_emb = torch.cat([title_emb, genre_emb], dim=1)

        # Final linear layer to project back down to 512 dimensions since user
        # tower is also 512 dimensions
        movie_emb = self.projector(combined_emb)

        return movie_emb