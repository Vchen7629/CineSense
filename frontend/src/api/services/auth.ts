// Code for http requests involving users
import { AxiosError } from 'axios';
import { recommendations_api } from '../client/basePath';
import { user_auth_api } from '../client/basePath';
import type { createGenreEmbProps } from '../../shared/types/user';

export const UserService = {
    // create embeddings for selected genres during signup
    create_genre_embeddings: async({user_id, genres}: createGenreEmbProps) => {
        try {
            const response = await recommendations_api.post(`user/genre_embedding/${user_id}`, {
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
            const response = await user_auth_api.post('/auth/signup', {
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
    },

    // send the httpOnly cookie to the auth api to get user credentials back
    auth: async() => {
        try {
            const response = await user_auth_api.get('/auth/authenticate')
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
