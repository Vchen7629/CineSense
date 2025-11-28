import { CreateNewAccount } from "@/app/utils/user";

// custom hook for signing up for a new user account
export function useSignUpUserAccount() {
    const createMutation = CreateNewAccount(); 

    const userSignUp = async (username: string, email: string, password: string) => {
        return await createMutation.mutateAsync({
            username,
            email,
            password,
        });
    };

    return {
        signup: userSignUp,
        isLoading: createMutation.isPending,
        isError: createMutation.isError,
        error: createMutation.error,
    };
}