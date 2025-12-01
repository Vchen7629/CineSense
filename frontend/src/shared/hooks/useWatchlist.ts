import { useQuery } from "@tanstack/react-query"
import { useAuth } from "./useAuth"
import { MovieService } from "../../api/services/movie"

// hook for fetching user watchlist
export function useWatchlist() {
    const { user } = useAuth()

    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['watchlist', user?.user_id],
        queryFn: () => MovieService.getWatchlist({ user_id: user.user_id }),
        staleTime: 5 * 60 * 1000, // 5 mins
        gcTime: 30 * 60 * 1000, // 30 mins
        enabled: !!user?.user_id,
        retry: false, // Don't retry if user has no watchlist
    })

    return {
        watchlist: data || [],
        isLoading,
        isError,
        error
    }
}