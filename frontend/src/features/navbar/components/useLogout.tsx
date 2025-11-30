import { UserService } from '../../../api/services/auth';
import { AxiosError } from 'axios';
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from 'react-router';

// custom hook for logging out of the user account
export function useLogout() {
    const queryClient = useQueryClient()
    const navigate = useNavigate()

    const mutation = useMutation({
        mutationFn: UserService.logout,
        retry: false,
        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error logging out:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error logging out:', error.message);
            } else {
                console.error('Error logging out:', error);
            }
        }
    })

    const userLogout = async () => {
        // Call logout API
        await mutation.mutateAsync();

        // Remove ALL queries including auth
        queryClient.removeQueries()

        // Set auth to undefined immediately after removal
        // This creates a new query with dataUpdateCount = 1 and data = undefined
        queryClient.setQueryData(['auth'], undefined)

        // Navigate to login
        navigate('/login')
    };

    return userLogout
}