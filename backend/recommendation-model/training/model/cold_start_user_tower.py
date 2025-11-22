import torch.nn as nn
import torch
import numpy as np
import polars as pl

# Creating Embeddings for cold start user tower, only includes top 3 genres
# returns tensor of shape [num_users, 64]
class ColdStartUserTower(nn.Module):
    def __init__(self, embedding_dim: int, device: str ="cuda", large_dataset: bool = False) -> None:
        super().__init__()

        self.device = device

        # load the numpy file containing mlb matrix for user top 3 preferred genres
        if large_dataset:
            preferred_genres = np.load("datasets/output/genre_embeddings.npy")
        else:
            preferred_genres = np.load("datasets/output-small/preferred-genres.npy")

        self.pref_genre_tensor = torch.tensor(preferred_genres, dtype=torch.float, device=device)

        self.projector = torch.nn.Linear(preferred_genres.shape[1], embedding_dim, device=self.device)
        self.relu = nn.ReLU()
        
    def forward(self, user_batch) -> torch.Tensor:
        # use precomputed embeddings
        pref_genre_features = self.pref_genre_tensor[user_batch]

        # Final linear layer to project back down to 512 dimensions 
        user_embeddings = self.relu(self.projector(pref_genre_features))

        return user_embeddings
    
