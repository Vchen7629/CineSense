import { CheckCircle, Loader, PlusIcon, X } from "lucide-react"
import { useAddToWatchlist } from "../hooks/useAddToWatchlist"
import { queryClient } from "@/api/client/queryClient"
import type { TMDBMovieApiRes } from "@/shared/types/tmdb"
import { useAuth } from "@/shared/hooks/useAuth"
import { useEffect } from "react"
import { toast } from "sonner"
import type { movieWatchlistItem } from "../types/watchlist"

const AddToWatchlistButton = ({ item }: any) => {
    const { addWatchlist, isLoading, isError, isSuccess } = useAddToWatchlist()
    const { user } = useAuth()

    useEffect(() => {
        if (isSuccess) {
            toast.success("Added to watchlist!", { 
                icon: <CheckCircle/>,
                style: { 
                    background: "#448094ff",
                    color: "#ffffff",
                    border: "#448094ff",
                }
            });
        }
    }, [isSuccess])

    useEffect(() => {
        if (isError) {
            toast.error("Failed to add to watchlist", { 
                icon: <X/>,
                style: { 
                    background: "red",
                    color: "#ffffff",
                    border: "#448094ff",
                }
            })
            // Rollback optimistic update
            queryClient.invalidateQueries({ queryKey: ['watchlist', user.user_id]})
        }
    }, [isError])
    
    async function addToWatchlist(movie: TMDBMovieApiRes) {
        await addWatchlist(user.user_id, movie)

        // adds the movie to our cached watchlist, optimistic update
        queryClient.setQueryData(['watchlist', user.user_id], (old: movieWatchlistItem[] | undefined) => [
            ...(old || []), 
            {
                movie_id: String(movie.id),
                movie_name: movie.title,
                poster_path: movie.poster_path,
                user_rating: 0
            }
        ])
    }

    return (
        <button
            onClick={() => addToWatchlist(item)}
            className={`flex w-fit items-center space-x-1 px-2 py-1.5 ${isError ? "bg-red-600 hover:bg-red-700" : "bg-teal-600 hover:bg-teal-700"} text-white rounded-md transition-colors duration-250`}
        >  
            {isLoading ? (
                <Loader className="animate-spin w-fit"/>
            ) : isError ? (
                <>
                    <X size={16}/>
                    <span className="text-sm">Error rating</span>
                </>
            ) : (
                <>
                    <PlusIcon size={16} />
                    <span className="text-sm">Add to Watchlist</span>
                </>
            )}
        </button>
    )
}

export default AddToWatchlistButton