import { MovieService } from "@/api/services/movie";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";

export function useRemoveFromWatchlist() {
    const mutation = useMutation({
        mutationFn: MovieService.removeFromWatchlist,
        retry: 1,
        onSuccess: () => {
            console.log('Movie removed From WatchList successfully:')
        },
        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error removing from watchlist:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error removing from watchlist:', error.message);
            } else {
                console.error('Error removing from watchlist:', error);
            }
        }
    });

    const removeFromWatchlist = async (user_id: string, movie_id: string) => {
        try {
            await mutation.mutateAsync({
                movie_id: movie_id,
                user_id: user_id,
            });
        } catch (error) {
            console.error("Failed to remove from watchlist:", error);
        }
    };

    return {
        removeFromWatchlist,
        isLoading: mutation.isPending,
        isError: mutation.isError,
        isSuccess: mutation.isSuccess,
        error: mutation.error
    };
}