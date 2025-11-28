import { AxiosError } from "axios"
import { tmdb_api } from "../client/basePath"
import type { FetchTMDBMovies } from "../../shared/types/tmdb"

const apiKey = import.meta.env.VITE_API_KEY || "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwM2Q2YWFlZDhhZWQ0MWVjMGY4ZmVhM2MyZWYwNGU1ZCIsIm5iZiI6MTc1ODc3MzE3MC4yNDcsInN1YiI6IjY4ZDRiZmIyOTYxNzQwMTEyM2EyYmMyNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.aDdNgN5KfMoSVfsPxuQrbsWPMXeVQDjU1GymrTmVNNc"

export const TMDBServices = {
    fetchMovieByName: async({
        query,
        pageNumber
    }: FetchTMDBMovies) => {
        try {
            const apiRes = await tmdb_api.get(`search/movie?query=${query}&include_adult=true&language=en-US&page=${pageNumber}`, {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'accept': 'application/json' 
                }
            })
            
            return apiRes.data
        } catch (error: unknown) {
            if (error instanceof AxiosError) {
                console.error(error.response?.data || error.message)
                throw error
            } else if (error instanceof Error) {
                console.error(error.message)
                throw error
            } else {
                console.error(error)
                throw error
            }
        }
    },

    fetchMovieCredits: async({ id }: { id: number }) => {
        try {
            const apiRes = await tmdb_api.get(`movie/${id}/credits?language=en-US`, {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'accept': 'application/json' 
                }
            })

            return apiRes.data
        } catch (error: unknown) {
            if (error instanceof AxiosError) {
                console.error(error.response?.data || error.message)
                throw error
            } else if (error instanceof Error) {
                console.error(error.message)
                throw error
            } else {
                console.error(error)
                throw error
            }
        }
    }
}