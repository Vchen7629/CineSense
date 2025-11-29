import { MovieService } from "@/api/services/movie";
import { useQuery } from "@tanstack/react-query";

const RECOMMENDATIONS_STORAGE_KEY = 'cached_recommendations'

// custom hook for getting user movie recommendations
export function useGetRecommendations(user_id: string) {
    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ['recommendations', user_id],
        queryFn: async () => {
            const cached = localStorage.getItem(`${RECOMMENDATIONS_STORAGE_KEY}_${user_id}`)
            if (cached) {
                try {
                    const parsedCache = JSON.parse(cached)
                    // return cached data if exists and was fetched in last 24 hours
                    const cacheAge = Date.now() - parsedCache.timestamp
                    if (cacheAge < 24 * 60 * 60 * 1000) {
                        return parsedCache.data
                    }
                } catch (e) {
                    console.warn('Invalid cached recommendations, fetching fresh data');
                    localStorage.removeItem(`${RECOMMENDATIONS_STORAGE_KEY}_${user_id}`)
                }
            }

            // fetch fresh data
            const freshData = await MovieService.getRecommendations({ user_id })

            // store in localStorage
            localStorage.setItem(`${RECOMMENDATIONS_STORAGE_KEY}_${user_id}`, JSON.stringify({
                data: freshData,
                timestamp: Date.now()
            }))

            return freshData
        },
        enabled: !!user_id,
        retry: false,
        staleTime: Infinity, // data is fresh indefinitely, since we manually refetch
        refetchOnWindowFocus: false, 
        refetchOnReconnect: false,
        refetchOnMount: 'always',
        // show old data while refetching to prevent flickering issue
        placeholderData: (previousData) => previousData
    })

    const refetchRecommendations = async () => {
        // Clear localstorage cache to force fresh fetch
        localStorage.removeItem(`${RECOMMENDATIONS_STORAGE_KEY}_${user_id}`)
        return await refetch()
    }

    return {
        recommendations: data,
        isAuthenticated: !!data && !isError,
        isLoading,
        refetchRecommendations: refetchRecommendations
    }
}