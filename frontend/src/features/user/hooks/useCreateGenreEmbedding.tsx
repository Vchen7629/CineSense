import { CreateGenreEmbeddings } from "@/app/utils/user";

// custom hook for sending selected genres to backend
export function useCreateGenreEmbeddings() {
    const createMutation = CreateGenreEmbeddings(); // your useMutation hook

    const createGenreEmbeddings = (user_id: string, genres: string[]) => {
        createMutation.mutate({
            user_id,
            genres,
        });
    };

    return createGenreEmbeddings;
}