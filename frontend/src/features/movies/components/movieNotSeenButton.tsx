import { useAuth } from "@/shared/hooks/useAuth"
import { useAddMovieToNotSeen } from "../hooks/useAddMovieToNotSeen"
import { CheckCircle, Loader, X } from "lucide-react"
import { useEffect } from "react"
import { toast } from "sonner"

const MovieNotSeenButton = ({ 
    movie_id, 
    setRating, 
    currentIndex, 
    recommendations,
    setIsRefetching,
    resetIndex,
    refetchRecommendations,
    nextMovie 
}: any) => {
    const { addToNotSeen, isLoading, isError, isSuccess } = useAddMovieToNotSeen()
    const { user } = useAuth()

    useEffect(() => {
        if (isSuccess) {
            toast.success("Added to not seen!", { 
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
            toast.error("Failed add to not seen", { 
                icon: <X/>,
                style: { 
                    background: "red",
                    color: "#ffffff",
                    border: "#448094ff",
                }
            })}
    }, [isError])

    async function handleMarkMovieUnseen(movie_id: string) {
        await addToNotSeen(user.user_id, movie_id)

        setRating(0)

        // check if this was the last movie in batch
        if (currentIndex + 1 >= recommendations.length && !isError) {
            setIsRefetching(true)
            resetIndex() // reset to 0
            await refetchRecommendations() // refetch new batch of 10 movies
            setIsRefetching(false)
        } else {
            nextMovie()
        }
    }

    return (
        <button 
            onClick={() => handleMarkMovieUnseen(movie_id)}
            className="px-3 py-1 bg-slate-700 rounded-lg"
        >
            {isLoading ? (
                <Loader className="animate-spin w-fit"/>
            ) : isError ? (
                <div className="flex items-center space-x-2">
                    <X size={16}/>
                    <span className="text-sm">Error Marking Unseen</span>
                </div>
            ) : (
                <>
                    <span className="text-sm">Haven't Seen</span>
                </>
            )}
        </button>
    )
}

export default MovieNotSeenButton