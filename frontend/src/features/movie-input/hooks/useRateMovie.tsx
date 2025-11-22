import type { RateMovieApi } from "@/app/types/movie";
import { RateMovie } from "@/app/utils/movie";

// function for sending the movie metadata to the backend api
export function useRateMovie() {
    const rateMovieMutation = RateMovie();

    const rateMovie = (item: RateMovieApi, rating: number) => {
        rateMovieMutation.mutate({
            movie_id: item.movie_id,          
            user_id: "50",              
            title: item.title,
            genres: item.genres,
            release_date: item.release_date,
            summary: item.summary,         
            actors: item.actors,
            director: item.director || [], 
            poster_path: item.poster_path || "",
            rating: rating,
            tmdb_vote_avg: item.tmdb_vote_avg,
            tmdb_vote_count: item.tmdb_vote_count,
            tmdb_popularity: item.tmdb_popularity
        });
    };

    return rateMovie;
}