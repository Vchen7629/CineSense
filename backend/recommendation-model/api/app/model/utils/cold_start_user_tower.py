
import torch.nn.functional as f
import torch
import joblib
from typing import List
from middleware.config import settings
import numpy as np

# User tower for cold start users - users who just signed up and only have selected 3 genres -
# uses a mlb to encode the genres and create an embedding for the user to find recommendations
class ColdStartUserTower:
    def __init__(self, device: str ="cpu") -> None:
        self.device = device

        # settings loaded from config.py in middleware folder
        self.embedding_dim = settings.embedding_dim

        self._load_model_files()

        num_genres = len(self.genre_mlb.classes_)
        self.projector = torch.nn.Linear(num_genres, self.embedding_dim, device=device)
        self.relu = torch.nn.ReLU()

        # load model - trained weights
        state_dict = torch.load(self.user_tower_path, weights_only=True)
        self.projector.load_state_dict({'weight': state_dict['projector.weight'], 'bias': state_dict['projector.bias']})
        self.projector.eval()

    def _load_model_files(self):
        user_tower_path = settings.user_tower_model_path
        genre_mlb_path = settings.genre_mlb_path

        # Download from S3 if needed
        if user_tower_path.startswith("s3://"):
            pass
            #user_tower_path = s3_loader.download_model(user_tower_path)
        if genre_mlb_path.startswith("s3://"):
            #genre_mlb_path = s3_loader.download_model(genre_mlb_path)
            pass

        self.genre_mlb = joblib.load(genre_mlb_path)
        self.user_tower_path = user_tower_path

    def embedding(self, genres: List[str]) -> List[np.ndarray]:
        genre_onehot = self.genre_mlb.transform([genres])
        genre_tensor = torch.tensor(genre_onehot, dtype=torch.float32, device=self.device)        
        
        # generate embedding using trained model
        with torch.no_grad():
            user_emb = self.relu(self.projector(genre_tensor))
            user_emb = f.normalize(user_emb, p=2, dim=1)

        user_emb = user_emb.cpu().numpy()[0]

        user_emb_list = str(user_emb.tolist())

        return user_emb_list
    
