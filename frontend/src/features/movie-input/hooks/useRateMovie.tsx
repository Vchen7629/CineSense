import type { DummyItem } from "../types/data";
import { RateMovie } from "@/app/utils/movie";

// function for sending the movie metadata to the backend api
export function useRateMovie() {
    const rateMovieMutation = RateMovie();

    const rateMovie = (item: DummyItem, rating: number) => {
        rateMovieMutation.mutate({
            movie_id: item.id,          
            user_id: "1",              
            name: item.name,
            genres: item.genres,
            release_date: item.release_date,
            summary: item.desc,         
            actors: item.actors,
            director: item.director || [], 
            poster_path: item.poster_path || "",
            rating: rating
        });
    };

    return rateMovie;
}