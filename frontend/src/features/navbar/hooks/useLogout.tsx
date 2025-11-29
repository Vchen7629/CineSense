import { UserService } from '../../../api/services/auth';
import { AxiosError } from 'axios';
import { useMutation } from "@tanstack/react-query";

// custom hook for logging out of the user account
export function useLogout() {
    const mutation = useMutation({
        mutationFn: UserService.logout,
        retry: false,
        onSuccess: (data) => {
            console.log('logout success:', data);
        },
        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error logging in:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error logging in:', error.message);
            } else {
                console.error('Error logging in:', error);
            }
        }
    })

    const userLogout = async () => {
        await mutation.mutateAsync();
    };

    return userLogout
}