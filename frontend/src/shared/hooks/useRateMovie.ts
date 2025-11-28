import type { TMDBMovieApiRes } from "@/shared/types/tmdb";
import { MovieService } from '../../api/services/movie';
import { TMDBServices } from "@/api/services/tmdb";
import { getGenreNames } from "../../features/movie-input/utils/genreMap";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";

// function for sending the movie metadata to the backend api
export function useRateMovie() {
    const mutation = useMutation({
        mutationFn: MovieService.rate,
        retry: 3,
        onSuccess: (data) => {
            console.log('Movie rated successfully:', data)
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
    });

    const rateMovie = async (item: TMDBMovieApiRes, rating: number) => {
        try {
            const credits = await TMDBServices.fetchMovieCredits({ id: item.id });
            const movie_year = item.release_date.split('-')[0]

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
                user_id: "cbebfe51-8bf0-4b03-9237-cfd54d1a0b94",
                title: item.title,
                genres: getGenreNames(item.genre_ids),
                release_date: movie_year,
                summary: item.overview,
                actors: actors,
                director: directors,
                poster_path: item.poster_path || "",
                rating: rating,
                tmdb_vote_avg: item.vote_average,
                tmdb_vote_count: item.vote_count,
                tmdb_popularity: item.popularity
            });
        } catch (error) {
            console.error("Failed to fetch credits:", error);
            // Fallback: submit without credits if fetch fails
            await mutation.mutateAsync({
                movie_id: String(item.id),
                user_id: "cbebfe51-8bf0-4b03-9237-cfd54d1a0b94",
                title: item.title,
                genres: getGenreNames(item.genre_ids),
                release_date: item.release_date,
                summary: item.overview,
                actors: [],
                director: [],
                poster_path: item.poster_path || "",
                rating: rating,
                tmdb_vote_avg: item.vote_average,
                tmdb_vote_count: item.vote_count,
                tmdb_popularity: item.popularity
            });
        }
    };

    return {
        rateMovie,
        isLoading: mutation.isPending,
        isError: mutation.isError,
        isSuccess: mutation.isSuccess,
        error: mutation.error
    };
}