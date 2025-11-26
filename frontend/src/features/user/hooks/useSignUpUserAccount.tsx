import { CreateNewAccount } from "@/app/utils/user";

// custom hook for signing up for a new user account
export function useSignUpUserAccount() {
    const createMutation = CreateNewAccount(); 

    const userSignUp = (username: string, email: string, password: string) => {
        createMutation.mutate({
            username,
            email,
            password,
        });
    };

    return {
        signup: userSignUp,
        isLoading: createMutation.isPending,
        isError: createMutation.isError,
        isSuccess: createMutation.isSuccess,
        error: createMutation.error,
    };
}