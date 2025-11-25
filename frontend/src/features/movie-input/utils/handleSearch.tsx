import type { RateMovieApi } from "@/app/types/movie";

// Function to filter archive data based on search input
export function HandleSearch(
    query: string, 
    apiRes: RateMovieApi[], 
    setApiRes: React.Dispatch<React.SetStateAction<RateMovieApi[]>>
) {
    if (!query) {
        return setApiRes(apiRes)
    } else {
        setApiRes(apiRes
            .filter(item => item.title != null && item.title.toLowerCase().includes(query.toLowerCase())) // combine null check and search
        );
    };
}