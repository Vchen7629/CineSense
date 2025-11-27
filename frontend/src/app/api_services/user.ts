// Code for http requests involving users
import { AxiosError } from 'axios';
import { backend_api } from '../lib/basePath';
import type { createGenreEmbProps } from '../types/user';

export const UserService = {
    // create embeddings for selected genres during signup
    create_genre_embeddings: async({user_id, genres}: createGenreEmbProps) => {
        try {
            const response = await backend_api.post(`user/genre_embedding/${user_id}`, {
                genres: genres
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
    },

    signup: async({username, email, password}: any) => {
        try {
            const response = await backend_api.post('/auth/signup', {
                username: username,
                email: email,
                password: password
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
