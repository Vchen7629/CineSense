import { UserService } from "@/api/services/auth";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";

// custom hook for sending selected genres to backend
export function useCreateGenreEmbeddings() {
    const mutation = useMutation({
        mutationFn: UserService.create_genre_embeddings,
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

    const createGenreEmbeddings = async (user_id: string, genres: string[]) => {
        await mutation.mutateAsync({
            user_id,
            genres,
        });
    };

    return createGenreEmbeddings;
}