import { useNavigate } from "react-router";
import { useCreateGenreEmbeddings } from "../hooks/useCreateGenreEmbedding";
import { useSignUpUserAccount } from "../hooks/useSignup";
import { toast } from "sonner";
import { Loader, X } from "lucide-react";


interface SignUpConfirmButtonProps {
    selectedGenres: string[]
    canSignup: boolean
    username: string
    email: string
    password: string
}

export const SignUpConfirmButton = ({ selectedGenres, canSignup, username, email, password }: SignUpConfirmButtonProps) => {
    const createGenreEmbeddings = useCreateGenreEmbeddings();
    const { signup, isLoading, isError} = useSignUpUserAccount()
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
            className={`${canSignup ? "bg-teal-600 hover:bg-teal-700" : "bg-gray-700"} w-fit rounded-md`}
            onClick={handleCompleteSignUp}
        >
            {isLoading ? (
                <div className="flex items-center space-x-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 rounded-md transition-colors duration-250">  
                    <Loader className="animate-spin"/>
                    <span>Signing up...</span>
                </div>
            ) : isError ? (
                <div className="flex items-center space-x-2 px-4 py-2 bg-red-700 hover:bg-red-800 rounded-md transition-colors duration-250">  
                    <X />
                    <span>Error</span>
                </div>
            ) : (
                <div className="flex items-center space-x-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 rounded-md transition-colors duration-250">
                    <span>Sign-up</span>
                </div>
            )}  
        </button>
    )
}