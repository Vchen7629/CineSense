// Code for http requests involving movies
import type { RateMovieApi } from '../../shared/types/movie';
import { recommendations_api } from '../client/basePath';
import { AxiosError } from 'axios';

export const MovieService = {
    // rate a move
    rate: async({
        movie_id, 
        user_id, 
        title, 
        genres, 
        release_date, 
        summary, 
        actors, 
        director, 
        poster_path, 
        rating,
        tmdb_vote_avg,
        tmdb_vote_count,
        tmdb_popularity
    }: RateMovieApi) => {
        try {
            const response = await recommendations_api.post(`movie/rate/${movie_id}`, {
                user_id: user_id,
                title: title,
                genres: genres,
                release_date: release_date,
                summary: summary,
                actors: actors,
                director: director,
                poster_path: poster_path,
                rating: rating,
                tmdb_vote_avg: tmdb_vote_avg,
                tmdb_vote_count: tmdb_vote_count,
                tmdb_popularity: tmdb_popularity
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
    },

    // get movie recommendations
    getRecommendations: async({ user_id }: { user_id: string }) => {
        try {
            const response = await recommendations_api.get(`recommendations/get/${user_id}`)

            console.log(response)
            return response.data
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
    },

    // get user movie watchlist
    getWatchlist: async({ user_id }: { user_id: string }) => {
        try {
            const response = await recommendations_api.get(`user/watchlist/get/${user_id}`)
            
            return response.data
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
    },

    addToWatchlist: async({ user_id, movie_id, title, genres, release_date, summary, actors, director, poster_path, rating }: any) => {
        try {
            const response = await recommendations_api.post(`user/watchlist/add/${user_id}`, {
                movie_id: movie_id,
                title: title,
                genres: genres,
                release_date: release_date,
                summary: summary,
                actors: actors,
                director: director,
                poster_path: poster_path,
                rating: rating
            })

            return response.data
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
