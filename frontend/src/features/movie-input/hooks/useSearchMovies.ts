import { useQuery } from '@tanstack/react-query';
import { TMDBServices } from '@/api/services/tmdb';

interface UseSearchMoviesParams {
    query: string;
    maxPages?: number;
    enabled?: boolean;
}

export function useSearchMovies({ query, maxPages = 20, enabled = true }: UseSearchMoviesParams) {
    return useQuery({
        queryKey: ['movies', 'search', query, maxPages],
        queryFn: async () => {
            // Fetch first page
            const firstPage = await TMDBServices.fetchMovieByName({ query, pageNumber: 1 });

            // Calculate total pages to fetch
            const totalPages = Math.min(firstPage.total_pages, maxPages);

            if (totalPages === 1) return firstPage.results;

            // Fetch remaining pages in parallel
            const remainingPages = await Promise.all(
                Array.from({ length: totalPages - 1 }, (_, i) =>
                    TMDBServices.fetchMovieByName({ query, pageNumber: i + 2 })
                )
            );

            return [firstPage, ...remainingPages].flatMap(page => page.results);
        },
        enabled: enabled && query.length > 0,
    });
}
