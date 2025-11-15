// Code for http requests involving users
import { api } from '../lib/basePath';

export const UserService = {
    // create embeddings for selected genres during signup
    create_genre_embeddings: async({user_id, genres}: any) => {
        try {
            const response = await api.post(`user/genre_embedding/${user_id}`, {
                genres: genres
            })

            return response.data
        } catch (error: any) {
            console.error(error.response?.data || error.message);
            throw error;
        }
    }
}
