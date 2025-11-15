
export interface RateMovieApi {
    movie_id: string,
    user_id: string,
    name: string,
    genres: string[],
    release_date: number,
    summary: string,
    actors: string[],
    director: string[],
    poster_path: string
    rating: number
}