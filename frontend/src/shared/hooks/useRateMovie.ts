import type { Movie } from "@/shared/types/tmdb";
import { MovieService } from '../../api/services/movie';
import { TMDBServices } from "@/api/services/tmdb";
import { getGenreNames } from "../../features/movies/utils/genreMap";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";

// function for sending the movie metadata to the backend api
export function useRateMovie() {

    const mutation = useMutation({
        mutationFn: MovieService.rate,
        retry: 1,
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

    const rateMovie = async (user_recommendations: boolean, user_id: string, item: Movie, rating: number) => {
        try {
            let movie_id: string
            let actors: string[]
            let directors: string[]
            let genres: string[]
            let summary: string
            let tmdb_avg_rating: number
            let tmdb_popularity: number
            let tmdb_vote_count: number
            let release_date: string
            let language: string

            // fetch movie credits from tmdb api only from add movie page
            if (!user_recommendations) {
                const credits = await TMDBServices.fetchMovieCredits({ id: item.id });
                
                // Extract top 50 actors
                actors = credits.cast
                    .slice(0, 50)
                    .map((person: { name: string }) => person.name);

                // Extract directors from crew
                directors = credits.crew
                    .filter((person: { job: string }) => person.job === "Director")
                    .slice(0, 10)
                    .map((person: { name: string }) => person.name);

                movie_id = String(item.id)
                genres = getGenreNames(item.genre_ids)
                summary = item.overview
                tmdb_avg_rating = item.vote_average
                tmdb_popularity = item.popularity
                tmdb_vote_count = item.vote_count
                language = item.original_language
                release_date = item.release_date.split('-')[0]
            } else {
                movie_id = item.movie_id || ""
                genres = item.genres || []
                actors = item.actors || []
                directors = item.director || []
                summary = item.summary || ""
                tmdb_avg_rating = item.tmdb_avg_rating || 0.0
                tmdb_popularity = item.tmdb_popularity || 0.0
                tmdb_vote_count = item.tmdb_vote_count || 0.0
                language = item.language || ""
                release_date = String(item.release_date)
            }

            await mutation.mutateAsync({
                movie_id: movie_id,
                user_id: user_id,
                title: item.title,
                genres: genres,
                release_date: release_date,
                summary: summary,
                actors: actors,
                director: directors,
                language: language,
                poster_path: item.poster_path || "",
                rating: rating,
                tmdb_vote_avg: tmdb_avg_rating,
                tmdb_vote_count: tmdb_vote_count,
                tmdb_popularity: tmdb_popularity
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
                language: "",
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
        error: mutation.error,
        reset: mutation.reset
    };
}