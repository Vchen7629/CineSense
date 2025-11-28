import { UserService } from '../../../api/services/auth';
import { AxiosError } from 'axios';
import { useMutation } from "@tanstack/react-query";

// custom hook for logging in to the user account
export function useLogin() {
    const mutation = useMutation({
        mutationFn: UserService.login,
        retry: false,
        onSuccess: (data) => {
            console.log('login success:', data);
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

    const userLogin = async (email: string, password: string) => {
        await mutation.mutateAsync({
            email,
            password,
        });
    };

    return {
        login: userLogin,
        isLoading: mutation.isPending,
        isError: mutation.isError,
        error: mutation.error,
    };
}