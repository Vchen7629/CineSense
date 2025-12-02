import { useAuth } from "@/shared/hooks/useAuth"
import { useRemoveFromWatchlist } from "../hooks/useRemoveFromWatchlist"
import { queryClient } from "@/api/client/queryClient"
import type { movieWatchlistItem } from "../types/watchlist"
import { CheckCircle, Loader, TrashIcon, X } from "lucide-react"
import { useEffect } from "react"
import { toast } from "sonner"

const RemoveFromWatchlistButton = ({ movie_id }: { movie_id: string }) => {
    const { removeFromWatchlist, isLoading, isError, isSuccess } = useRemoveFromWatchlist()
    const { user } = useAuth()

    async function removeWatchlist(movieId: string) {
        await removeFromWatchlist(user.user_id, movieId)

        queryClient.setQueryData(['watchlist', user.user_id], (old: movieWatchlistItem[] | undefined) =>
            (old || []).filter(m => m.movie_id !== movieId)
        );
    }

    useEffect(() => {
        if (isSuccess) {
            toast.success("removed from watchlist!", { 
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
            toast.error("Failed remove from watchlist", { 
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
    

    
    return (
        <button
            onClick={() => removeWatchlist(movie_id)}
            className="flex items-center space-x-1 px-3 py-1.5 bg-slate-500/40 hover:bg-red-600 rounded-md transition-colors duration-250"
        >   
            {isLoading ? (
                <Loader className="animate-spin w-fit"/>
            ) : isError ? (
                <>
                    <X size={16}/>
                    <span className="text-sm">Error removing</span>
                </>
            ) : (
                <>
                    <TrashIcon size={18} />
                    <span className="text-sm">Remove</span>
                </>
            )}
        </button>
    )
}

export default RemoveFromWatchlistButton