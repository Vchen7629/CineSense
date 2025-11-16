import numpy as np

def split_hard_random_candidates(all_candidates, movies_to_genres, user_genres, num_negatives, genre_ratio=0.8):
    # Split into hard and random candidates
    hard_candidates = []  # Movies matching user's top-3 genres
    for movie_idx in all_candidates:
        movie_genres = movies_to_genres.get(movie_idx, set())
        if len(user_genres.intersection(movie_genres)) > 0:
            hard_candidates.append(movie_idx)

    hard_candidates = np.array(hard_candidates)

    # Mixed negative sampling: genre_ratio% hard (same genre) + (1-genre_ratio)% random (any genre)
    num_hard = int(num_negatives * genre_ratio)
    num_random = num_negatives - num_hard

    return hard_candidates, num_hard, num_random
