// Code for http requests involving movies
import type { RateMovieApi } from '../types/movie';
import { api } from '../lib/basePath';
import { AxiosError } from 'axios';

export const MovieService = {
    // rate a move
    rate: async({movie_id, user_id, name, genres, release_date, summary, actors, director, poster_path, rating}: RateMovieApi) => {
        try {
            const response = await api.post(`movie/rate/${movie_id}`, {
                user_id: user_id,
                title: name,
                genres: genres,
                release_date: release_date,
                summary: summary,
                actors: actors,
                director: director,
                poster_path: poster_path,
                rating: rating
            })
            console.log(response)
            return response.data;
        } catch (error: unknown) {
            if (error instanceof AxiosError) {
                console.error(error.response?.data || error.message);
                throw error;
            } else if (error instanceof Error) {
                console.error(error.message);
                throw error;
            } else {
                console.error(error);
                throw error;
            }
        }
    }
}
