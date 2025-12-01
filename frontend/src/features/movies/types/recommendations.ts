export interface MovieRecommendation {
    movie_id: string
    poster_path: string
    release_date: number
    summary: string
    title: string
    actors: string[]
    director: string[]
    genres: string[]
    tmdb_avg_rating: number
    tmdb_vote_count: number
    tmdb_popularity: number
}

export interface RatingState {
    currentIndex: number;
    ratedMovieIds: string[];
    batchNumber: number;
}