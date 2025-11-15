import { useMutation } from '@tanstack/react-query';
import { UserService } from '../services/user';

export const CreateGenreEmbeddings = () => {
    return useMutation({
        mutationFn: UserService.create_genre_embeddings,
        retry: 3,

        onSuccess: (data) => {
            console.log('Movie rated successfully:', data);
        },

        onError: (error: any) => {
            console.error('Error rating movie:', error.response?.data || error.message);
        }
    })
}