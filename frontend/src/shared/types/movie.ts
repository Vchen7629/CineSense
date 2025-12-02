
export interface RateMovieApi {
    movie_id: string,
    user_id?: string,
    title: string,
    genres: string[],
    release_date: string,
    summary: string,
    actors: string[],
    director: string[],
    poster_path: string,
    language: string,
    rating?: number,
    tmdb_vote_avg: number,
    tmdb_vote_count: number,
    tmdb_popularity: number
}