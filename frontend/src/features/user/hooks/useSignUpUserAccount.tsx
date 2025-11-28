import { UserService } from '../../../api/services/auth';
import { AxiosError } from 'axios';
import { useMutation } from "@tanstack/react-query";

// custom hook for signing up for a new user account
export function useSignUpUserAccount() {
    const mutation = useMutation({
        mutationFn: UserService.signup,
        retry: 2,
        onSuccess: (data) => {
            console.log('Movie rated successfully:', data);
        },
        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error rating movie:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error rating movie:', error.message);
            } else {
                console.error('Error rating movie:', error);
            }
        }
    })

    const userSignUp = async (username: string, email: string, password: string) => {
        return await mutation.mutateAsync({
            username,
            email,
            password,
        });
    };

    return {
        signup: userSignUp,
        isLoading: mutation.isPending,
        isError: mutation.isError,
        error: mutation.error,
    };
}