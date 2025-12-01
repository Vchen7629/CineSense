import { MovieService } from "@/api/services/movie";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";

export function useAddMovieToNotSeen() {
    const mutation = useMutation({
        mutationFn: MovieService.markMovieAsNotSeen,
        retry: 1,
        onSuccess: () => {
            console.log('Movie marked as not seen successfully:')
        },
        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error marking movie not seen:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error marking movie not seen:', error.message);
            } else {
                console.error('Error marking movie not seen:', error);
            }
        }
    });

    const addToNotSeen = async (user_id: string, movie_id: string) => {
        try {
            await mutation.mutateAsync({
                movie_id: movie_id,
                user_id: user_id,
            });
        } catch (error) {
            console.error("Failed marking movie as not seen:", error);
        }
    };

    return {
        addToNotSeen,
        isLoading: mutation.isPending,
        isError: mutation.isError,
        isSuccess: mutation.isSuccess,
        error: mutation.error
    };
}