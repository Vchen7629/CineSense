import torch
import torch.nn as nn
import torch.nn.functional as f
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi import HTTPException
from typing import List
from utils.env_config import settings

# Dynamically generate new embeddings for unseen movies
class MovieTower:
    def __init__(
        self, 
        movie_tower_path: str,
        genre_mlb,
        sentence_transformer_model: SentenceTransformer, 
        device="cpu"
    ) -> None:
        self.device = device
        self.embedding_dim = settings.embedding_dim
        self.movie_tower_path = movie_tower_path
        self.genre_mlb = genre_mlb
        self.relu = nn.ReLU()

        # Load preprocessing tools
        self.sentence_transformer_encoder = sentence_transformer_model

        # loading model weights and layers when initialize
        self._extract_feature_dims()
        self._linear_layers()
        self._load_trained_weights()

    def _extract_feature_dims(self) -> None:
        """ Loads trained movie tower state dict """
        self.state_dict = torch.load(self.movie_tower_path, weights_only=True, map_location=self.device)

        # Extract shapes from saved weights
        self.title_in_features = self.state_dict['title_linear.weight'].shape[1]  # Should be 384
        self.genre_in_features = self.state_dict['genre_linear.weight'].shape[1]  # Number of genres
        self.year_in_features = self.state_dict['year_linear.weight'].shape[1]
        self.metadata_sentence_in_features = self.state_dict['metadata_sentence_linear.weight'].shape[1]
    
    def _load_trained_weights(self) -> None:
        """ Load trained weights for movie tower"""
        # Load trained weights
        self.title_linear.load_state_dict({
            'weight': self.state_dict['title_linear.weight'],
            'bias': self.state_dict['title_linear.bias']
        })
        self.genre_linear.load_state_dict({
            'weight': self.state_dict['genre_linear.weight'],
            'bias': self.state_dict['genre_linear.bias']
        })
        self.year_linear.load_state_dict({
            'weight': self.state_dict['year_linear.weight'],
            'bias': self.state_dict['year_linear.bias']
        })
        self.metadata_sentence_linear.load_state_dict({
            'weight': self.state_dict['metadata_sentence_linear.weight'],
            'bias': self.state_dict['metadata_sentence_linear.bias']
        })
        self.projector.load_state_dict({
            'weight': self.state_dict['projector.weight'],
            'bias': self.state_dict['projector.bias']
        })
    
    def _linear_layers(self) -> None:
        # Create linear layers with correct dimensions
        self.title_linear = nn.Linear(self.title_in_features, self.embedding_dim, device=self.device)
        self.genre_linear = nn.Linear(self.genre_in_features, self.embedding_dim, device=self.device)
        self.year_linear = nn.Linear(self.year_in_features, self.embedding_dim, device=self.device)
        self.metadata_sentence_linear = nn.Linear(self.metadata_sentence_in_features, self.embedding_dim, device=self.device)
        self.projector = nn.Linear(self.embedding_dim * 4, self.embedding_dim, device=self.device)

        # Set to eval mode
        self.title_linear.eval()
        self.genre_linear.eval()
        self.year_linear.eval()
        self.metadata_sentence_linear.eval()
        self.projector.eval()

    # generate embeddings for a new unseen movie using trained movie tower
    def generate_new_movie_embedding(
        self, 
        title: str, 
        genres: List[str], 
        year: int, 
        actors: List[str],
        director: List[str],
        overview: str
    ) -> List[np.ndarray]:
        with torch.no_grad():
            # Encode title with sentence transformer
            title_features = self.sentence_transformer_encoder.encode([title], convert_to_numpy=True)
            title_tensor = torch.tensor(title_features, dtype=torch.float32, device=self.device)

            # Encode genres with mlb
            genre_features = self.genre_mlb.transform([genres])
            genre_tensor = torch.tensor(genre_features, dtype=torch.float32, device=self.device)

            # encode movie year with normalized year
            year_normalized = (year - 1900) / 125.0 # normalizes it between [0, 1] in a float
            year_tensor = torch.tensor([[year_normalized]], dtype=torch.float32, device=self.device)

            # Encode actors/director/movie overview into one sentence embedding using sentence transformers
            metadata_parts = []

            if not overview:
                raise HTTPException(status_code=500, detail="missing movie overview")
            if not director:
                raise HTTPException(status_code=500, detail="missing movie director")
            if not actors:
                raise HTTPException(status_code=500, detail="missing movie actors")
            
            # add movie overview
            metadata_parts.append(overview)
            # add movie director with identifying string
            metadata_parts.append(f"Directed by {director}")
            # add movie actors with identifying string
            metadata_parts.append(f"Starring {actors}")

            metadata_sentence = ". ".join(metadata_parts).strip(". ")

            metadata_sentence_features = self.sentence_transformer_encoder.encode([metadata_sentence], convert_to_numpy=True)
            metadata_sentence_tensor = torch.tensor(metadata_sentence_features, dtype=torch.float32, device=self.device)

            # Pass through trained linear layers
            title_emb = self.relu(self.title_linear(title_tensor))
            genre_emb = self.relu(self.genre_linear(genre_tensor))
            year_emb = self.relu(self.year_linear(year_tensor))
            metadata_sentence_emb = self.relu(self.metadata_sentence_linear(metadata_sentence_tensor))

            # Normalize embeddings
            title_emb = f.normalize(title_emb, p=2, dim=1)
            genre_emb = f.normalize(genre_emb, p=2, dim=1)
            year_emb = f.normalize(year_emb, p=2, dim=1)
            metadata_sentence_emb = f.normalize(metadata_sentence_emb, p=2, dim=1)

            # Concatenate and project to final embedding
            combined_emb = torch.cat([title_emb, genre_emb, year_emb, metadata_sentence_emb], dim=1)
            final_emb = self.projector(combined_emb)
            final_emb = f.normalize(final_emb, p=2, dim=1)

            return final_emb.cpu().numpy()[0].tolist()
