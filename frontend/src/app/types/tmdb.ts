
export interface FetchTMDBMovies {
    query: string
    pageNumber: number
}

export interface TMDBMovieApiRes {
    id: number
    title: string
    original_title: string
    original_language: string
    overview: string
    backdrop_path: string
    poster_path: string
    genre_ids: number[]
    popularity: number
    release_date: string
    video: boolean
    adult: boolean
    vote_count: number
    vote_average: number
}