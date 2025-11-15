import torch
import torch.nn as nn
import torch.nn.functional as f
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import joblib
import os

# Dynamically generate new embeddings for unseen movies
class MovieTower:
    def __init__(self, embedding_dim: int = 512, device="cuda", large_dataset: bool = False) -> None:
        self.embedding_dim = embedding_dim
        self.device = device
        current_dir = os.path.dirname(__file__)

        if large_dataset:
            model_dir = os.path.join(current_dir, "..", "files")
        else:
            model_dir = os.path.join(current_dir, "..", "files_small")

        # Load trained movie tower state dict
        tower_path = os.path.join(model_dir, "movie_tower.pth")
        state_dict = torch.load(tower_path, weights_only=True, map_location=device)

        # Extract shapes from saved weights
        title_in_features = state_dict['title_linear.weight'].shape[1]  # Should be 384
        genre_in_features = state_dict['genre_linear.weight'].shape[1]  # Number of genres

        # Create linear layers with correct dimensions
        self.title_linear = nn.Linear(title_in_features, embedding_dim, device=device)
        self.genre_linear = nn.Linear(genre_in_features, embedding_dim, device=device)
        self.projector = nn.Linear(embedding_dim * 2, embedding_dim, device=device)

        # Load trained weights
        self.title_linear.load_state_dict({
            'weight': state_dict['title_linear.weight'],
            'bias': state_dict['title_linear.bias']
        })
        self.genre_linear.load_state_dict({
            'weight': state_dict['genre_linear.weight'],
            'bias': state_dict['genre_linear.bias']
        })
        self.projector.load_state_dict({
            'weight': state_dict['projector.weight'],
            'bias': state_dict['projector.bias']
        })

        # Set to eval mode
        self.title_linear.eval()
        self.genre_linear.eval()
        self.projector.eval()

        self.relu = nn.ReLU()

        # Load preprocessing tools
        self.title_encoder = SentenceTransformer("all-MiniLM-L6-v2")

        # Load the same MultiLabelBinarizer used for training
        genre_mlb_path = os.path.join(model_dir, "genre_mlb.joblib")
        self.genre_mlb = joblib.load(genre_mlb_path)

    # generate embeddings for a new unseen movie using trained movie tower
    def generate_new_movie_embedding(self, title: str, genres: List[str]) -> List[np.ndarray]:
        with torch.no_grad():
            # Encode title with sentence transformer
            title_features = self.title_encoder.encode([title], convert_to_numpy=True)
            title_tensor = torch.tensor(title_features, dtype=torch.float32, device=self.device)

            # Encode genres with mlb
            genre_features = self.genre_mlb.transform([genres])
            genre_tensor = torch.tensor(genre_features, dtype=torch.float32, device=self.device)

            # Pass through trained linear layers
            title_emb = self.relu(self.title_linear(title_tensor))
            genre_emb = self.relu(self.genre_linear(genre_tensor))

            # Normalize embeddings
            title_emb = f.normalize(title_emb, p=2, dim=1)
            genre_emb = f.normalize(genre_emb, p=2, dim=1)

            # Concatenate and project to final embedding
            combined_emb = torch.cat([title_emb, genre_emb], dim=1)
            final_emb = self.projector(combined_emb)
            final_emb = f.normalize(final_emb, p=2, dim=1)

            return final_emb.cpu().numpy()[0].tolist()
