import { useNavigate } from "react-router";
import { useCreateGenreEmbeddings } from "../hooks/useCreateGenreEmbedding";
import { useSignUpUserAccount } from "../hooks/useSignUpUserAccount";
import { toast } from "sonner";


interface SignUpConfirmButtonProps {
    selectedGenres: string[]
    canSignup: boolean
    username: string
    email: string
    password: string
}

export const SignUpConfirmButton = ({ selectedGenres, canSignup, username, email, password }: SignUpConfirmButtonProps) => {
    const test_user_id = "4"
    const createGenreEmbeddings = useCreateGenreEmbeddings();
    const { signup, isLoading, isError, } = useSignUpUserAccount()
    const navigate = useNavigate()

    async function handleCompleteSignUp() {
        let userId: string
        try {
            const response = await signup(username, email, password);
            if (!response?.user_id) {
                toast.error("Signup Failed, no user_id returned")
                return
            }
            userId = response.user_id

        } catch (error: any) {
            toast.error("Sign up failed")
            return 
        }

        try {
            await createGenreEmbeddings(userId, selectedGenres)
            navigate("/login")
        } catch (error) {
            toast.error("Account created but failed to set preferences, try selecting your genres again")
            return;
        }
    }


    return (
        <button
            disabled={!canSignup}
            className={`${canSignup ? "bg-teal-600 hover:bg-teal-700" : "bg-gray-700"} w-28 px-4 py-2 rounded-md transition-colors duration-250`}
            onClick={handleCompleteSignUp}
        >
            Sign-up
        </button>
    )
}