// Wrapper Functions for axios calls to handle success/error with React Query
import { useMutation } from '@tanstack/react-query';
import { MovieService } from '../api_services/movie';
import { AxiosError } from 'axios';

export const RateMovie = () => {
    return useMutation({
        mutationFn: MovieService.rate,
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