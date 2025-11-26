import type { TMDBMovieApiRes } from "@/app/types/tmdb";
import { RateMovie } from "@/app/utils/movie";
import { TMDBServices } from "@/app/api_services/tmdb";
import { getGenreNames } from "../utils/genreMap";
import { useQuery } from "@tanstack/react-query";

// function for sending the movie metadata to the backend api
export function useRateMovie() {
    const rateMovieMutation = RateMovie();

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

            rateMovieMutation.mutate({
                movie_id: String(item.id),
                user_id: "1",
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
            rateMovieMutation.mutate({
                movie_id: String(item.id),
                user_id: "1",
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
        isLoading: rateMovieMutation.isPending,
        isError: rateMovieMutation.isError,
        isSuccess: rateMovieMutation.isSuccess,
        error: rateMovieMutation.error
    };
}