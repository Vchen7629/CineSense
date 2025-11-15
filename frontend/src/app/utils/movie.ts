// Wrapper Functions for axios calls to handle success/error with React Query
import { useMutation } from '@tanstack/react-query';
import { MovieService } from '../services/movie';

export const RateMovie = () => {
    return useMutation({
        mutationFn: MovieService.rate,
        retry: 3,

        onSuccess: (data) => {
            console.log('Movie rated successfully:', data);
        },

        onError: (error: any) => {
            console.error('Error rating movie:', error.response?.data || error.message);
        }
    })
}