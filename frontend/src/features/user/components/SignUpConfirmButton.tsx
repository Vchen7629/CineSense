import { CreateGenreEmbeddings } from "@/app/utils/user";
import { useCreateGenreEmbeddings } from "../hooks/useCreateGenreEmbedding";

interface SignUpConfirmButtonProps {
    selectedGenres: string[]
    canSignup: boolean
}

export const SignUpConfirmButton = ({ selectedGenres, canSignup }: SignUpConfirmButtonProps) => {
    const test_user_id = "11"
    const createGenreEmbeddings = useCreateGenreEmbeddings();
    
    const handleClick = () => {
        createGenreEmbeddings(test_user_id, selectedGenres);
    };

    return (
        <button
            disabled={!canSignup}
            className={`${canSignup ? "bg-teal-600 hover:bg-teal-700" : "bg-gray-700"} w-28 px-4 py-2 rounded-md transition-colors duration-250`}
            onClick={handleClick}
        >
            Sign-up
        </button>
    )
}