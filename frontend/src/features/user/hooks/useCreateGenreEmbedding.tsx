import { CreateGenreEmbeddings } from "@/app/utils/user";

// custom hook for sending selected genres to backend
export function useCreateGenreEmbeddings() {
    const createMutation = CreateGenreEmbeddings(); // your useMutation hook

    const createGenreEmbeddings = async (user_id: string, genres: string[]) => {
        createMutation.mutateAsync({
            user_id,
            genres,
        });
    };

    return createGenreEmbeddings;
}