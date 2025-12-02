import { getGenreName } from "./genreMap";
import { getLanguageName } from "./languageMap";

interface FilterProps {
    genre?: string
    language?: string
    year?: string
}

export function filterMovies(movies: any[], { genre, language, year }: FilterProps) {
    if (movies.length === 0) return [];

    let filtered = [...movies];

    // Filter by genre
    if (genre) {
        filtered = filtered.filter((movie) => {
            // Handle both genre_ids (array of numbers) and genres (array of strings)
            const movieGenres = movie.genre_ids
                ? movie.genre_ids.map((id: number) => getGenreName(id))
                : movie.genres || [];

            return movieGenres.includes(genre);
        });
    }

    // Filter by language
    if (language) {
        filtered = filtered.filter((movie) => {
            // Handle both original_language and language fields
            const movieLanguage = movie.original_language || movie.language || '';
            return getLanguageName(movieLanguage) === language;
        });
    }

    // Filter by year
    if (year) {
        filtered = filtered.filter((movie) => {
            // Handle both string dates ("2024-01-01") and number years (2024)
            const movieYear = typeof movie.release_date === 'string'
                ? movie.release_date.split('-')[0]
                : String(movie.release_date);
            return movieYear === year;
        });
    }

    return filtered;
}