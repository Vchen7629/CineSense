import torch.nn as nn
import torch
import numpy as np
import os

# Collaborative filtering user tower using movie embedding averaging
# no learned params, just create user embedddings on the fly by averaging their rated movies
class PersonalizedUserTower(nn.Module):
    def __init__(self, embedding_dim: int, device: str ="cuda") -> None:
        super().__init__()

        self.device = device
        self.embedding_dim = embedding_dim
                             
    def forward(self, user_batch: torch.Tensor, pos_movie_batch: torch.Tensor, dataset, movie_tower) -> torch.Tensor:
        batch_size = len(user_batch)

        all_user_movies = []
        split_sizes = [] # track how many movies per user

        for i in range(batch_size):
            user_id = user_batch[i].item()
            pos_movie = pos_movie_batch[i].item()

            # get user's other rated movies (excluding current pos)
            other_movies = dataset.get_user_movies_except(user_id, pos_movie)
            all_user_movies.extend(other_movies.tolist())
            split_sizes.append(len(other_movies))
        
        # edge case: if all users have only 1 movie
        if len(all_user_movies) == 0:
            return torch.zeros(batch_size, self.embedding_dim, device=self.device)
        
        # create embedding for all movies from all movies
        all_movies_tensor = torch.tensor(all_user_movies, device=self.device, dtype=torch.long)
        all_movie_embs = movie_tower(all_movies_tensor)

        # split embeddings back per user and average
        user_embeddings = []
        start_idx = 0

        for size in split_sizes:
            if size == 0:
                user_embeddings.append(torch.zeros(self.embedding_dim, device=self.device))
            else:
                # average the users movie embs
                user_movie_embs = all_movie_embs[start_idx:start_idx + size]
                user_emb = user_movie_embs.mean(dim=0)
                user_embeddings.append(user_emb)
            
            start_idx += size
        
        # stack into batch tesnor
        return torch.stack(user_embeddings)
