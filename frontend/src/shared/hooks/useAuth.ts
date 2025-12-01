import { UserService } from "@/api/services/auth";
import { useQuery } from "@tanstack/react-query";


// Simple Auth Check Hook
export function useAuth(options?: { enabled?: boolean }) {
    const { enabled = true } = options || {}

    const { data, isLoading, isError } = useQuery({
        queryKey: ['auth'],
        queryFn: UserService.auth,
        enabled: (query) => {
            // Allow initial fetch (dataUpdateCount === 0 means never fetched) only if enabled
            if (query.state.dataUpdateCount === 0) return enabled
            // Don't fetch if explicitly logged out (data set to undefined after initial fetch)
            return query.state.data !== undefined
        },
        retry: false,
        staleTime: 5 * 60 * 1000 * 60, // 1 hour
        refetchOnWindowFocus: (query) => enabled && query.state.data !== undefined,
        refetchOnReconnect: (query) => enabled && query.state.data !== undefined,
        refetchOnMount: (query) => enabled && query.state.data !== undefined,
    })

    return {
        user: data,
        isAuthenticated: !!data && !isError,
        isLoading,
    }
}