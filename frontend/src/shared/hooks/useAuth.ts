import { UserService } from "@/api/services/auth";
import { useQuery } from "@tanstack/react-query";


// Simple Auth Check Hook
export function useAuth(options?: { enabled?: boolean }) {
    const { enabled = true } = options || {}

    const { data, isLoading, isError } = useQuery({
        queryKey: ['auth'],
        queryFn: UserService.auth,
        enabled, // only run query if enabled is true
        retry: false,
        staleTime: 5 * 60 * 1000 * 60, // 1 hour
        refetchOnWindowFocus: true, // recheck
        refetchOnReconnect: true, // recheck when user reconnects
        refetchOnMount: 'always',
        // show old data while refetching to prevent flickering issue 
        placeholderData: (previousData) => previousData
    })

    return {
        user: data,
        isAuthenticated: !!data && !isError,
        isLoading,
    }
}