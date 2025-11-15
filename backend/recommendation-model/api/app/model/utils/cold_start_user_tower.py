
import torch.nn.functional as f
import torch
import joblib
import os
from typing import List

# User tower for cold start users - users who just signed up and only have selected 3 genres -
# uses a mlb to encode the genres and create an embedding for the user to find recommendations
class ColdStartUserTower:
    def __init__(self, embedding_dim: int, device: str ="cuda", large_dataset: bool = False) -> None:
        current_dir = os.path.dirname(__file__)
        self.device = device
        self.embedding_dim = embedding_dim

        if large_dataset:
            user_tower_path = os.path.join(current_dir, "..", "files", "user_tower.pth")
            genre_mlb_path = os.path.join(current_dir, "..", "files", "genre_mlb.joblib")
        else:
            user_tower_path = os.path.join(current_dir, "..", "files_small", "user_tower.pth")
            genre_mlb_path = os.path.join(current_dir, "..", "files_small", "genre_mlb.joblib")
    
        # load mlb
        self.genre_mlb = joblib.load(genre_mlb_path)
        num_genres = len(self.genre_mlb.classes_)

        self.projector = torch.nn.Linear(num_genres, embedding_dim, device=device)
        self.relu = torch.nn.ReLU()

        # load model - trained weights
        state_dict = torch.load(user_tower_path, weights_only=True)
        self.projector.load_state_dict({'weight': state_dict['projector.weight'], 'bias': state_dict['projector.bias']})
        self.projector.eval()

    def embedding(self, genres: List[str]) -> torch.Tensor:
        genre_onehot = self.genre_mlb.transform([genres])
        genre_tensor = torch.tensor(genre_onehot, dtype=torch.float32, device=self.device)        
        
        # generate embedding using trained model
        with torch.no_grad():
            user_emb = self.relu(self.projector(genre_tensor))
            user_emb = f.normalize(user_emb, p=2, dim=1)

        user_emb = user_emb.cpu().numpy()[0]

        user_emb_list = str(user_emb.tolist())

        return user_emb_list
    
