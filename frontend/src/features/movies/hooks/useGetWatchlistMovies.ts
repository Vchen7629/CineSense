import { MovieService } from "@/api/services/movie";
import { useQuery } from "@tanstack/react-query";

// custom hook for getting user watchlist movies
export function useGetWatchlistMovies(user_id: string) {
    const { data, isLoading, isError, error, refetch } = useQuery({
        queryKey: ['watchlist_movies', user_id],
        queryFn: async () => {
            const rated_movies = await MovieService.getWatchlistMovie({ user_id })

            return rated_movies
        },
        enabled: !!user_id,
        retry: 1,
        staleTime: 10 * 60 * 1000, // data is fresh for 10 mins
        refetchOnWindowFocus: false, 
        refetchOnReconnect: false,
    })
    return {
        data,
        isLoading,
        isError,
        error,
        refetch
    }
}