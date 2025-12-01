import { MovieService } from "@/api/services/movie";
import { TMDBServices } from "@/api/services/tmdb";
import type { Movie } from "@/shared/types/tmdb";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { getGenreNames } from "../utils/genreMap";

export function useAddToWatchlist() {
    const mutation = useMutation({
        mutationFn: MovieService.addToWatchlist,
        retry: 1,
        onSuccess: () => {
            console.log('Movie added to WatchList successfully:')
        },
        onError: (error: unknown) => {
            if (error instanceof AxiosError) {
                console.error('Error adding to watchlist:', error.response?.data || error.message);
            } else if (error instanceof Error) {
                console.error('Error adding to watchlist:', error.message);
            } else {
                console.error('Error adding to watchlist:', error);
            }
        }
    });

    const addWatchlist = async (user_id: string, item: Movie) => {
        try {
            const credits = await TMDBServices.fetchMovieCredits({ id: item.id });
            
            // Extract top 50 actors
            const actors = credits.cast
                .slice(0, 50)
                .map((person: { name: string }) => person.name);

            // Extract directors from crew
            const directors = credits.crew
                .filter((person: { job: string }) => person.job === "Director")
                .slice(0, 10)
                .map((person: { name: string }) => person.name);

            await mutation.mutateAsync({
                movie_id: String(item.id),
                user_id: user_id,
                title: item.title,
                genres: getGenreNames(item.genre_ids),
                release_date: item.release_date.split('-')[0],
                summary: item.overview,
                actors: actors,
                director: directors,
                poster_path: item.poster_path || "",
                rating: 0,
            });
        } catch (error) {
            console.error("Failed to fetch credits:", error);
            // Fallback: submit without credits if fetch fails
            await mutation.mutateAsync({
                movie_id: String(item.id),
                user_id: user_id,
                title: item.title,
                genres: getGenreNames(item.genre_ids),
                release_date: "2000",
                summary: item.overview,
                actors: [],
                director: [],
                poster_path: item.poster_path || "",
                rating: 0,
            });
        }
    };

    return {
        addWatchlist,
        isLoading: mutation.isPending,
        isError: mutation.isError,
        isSuccess: mutation.isSuccess,
        error: mutation.error
    };
}