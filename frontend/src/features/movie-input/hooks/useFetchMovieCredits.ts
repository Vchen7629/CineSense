import { useQuery } from '@tanstack/react-query';
import { TMDBServices } from '@/app/api_services/tmdb';

interface MovieCredits {
    actors: string[];
    directors: string[];
}

export function useFetchMovieCredits({ id, enabled = false }: { id: number; enabled?: boolean }) {
    return useQuery<MovieCredits>({
        queryKey: ['credits', id],
        queryFn: async () => {
            const credits = await TMDBServices.fetchMovieCredits({ id });

            // Extract top 5 actors
            const actors = credits.cast
                .slice(0, 10)
                .map((person: { name: string }) => person.name);

            // Extract directors from crew
            const directors = credits.crew
                .filter((person: { job: string }) => person.job === "Director")
                .map((person: { name: string }) => person.name);

            return {
                actors,
                directors
            };
        },
        enabled, // Only fetch when explicitly enabled
        staleTime: 30 * 60 * 1000, // Cache for 30 minutes
    });
}