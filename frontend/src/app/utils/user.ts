import { useMutation } from '@tanstack/react-query';
import { UserService } from '../api_services/user';
import { AxiosError } from 'axios';

export const CreateGenreEmbeddings = () => {
    return useMutation({
        mutationFn: UserService.create_genre_embeddings,
        retry: 3,

        onSuccess: (data) => {
            console.log('Movie rated successfully:', data);
        },

        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error rating movie:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error rating movie:', error.message);
            } else {
                console.error('Error rating movie:', error);
            }
        }
    })
}

export const CreateNewAccount = () => {
    return useMutation({
        mutationFn: UserService.signup,
        retry: 2,

        onSuccess: (data) => {
            console.log('User Created successfully:', data);
        },

        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error signing up:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error signing up:', error.message);
            } else {
                console.error('Error signing up:', error);
            }
        }
    })
}