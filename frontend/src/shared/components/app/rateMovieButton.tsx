import { queryClient } from "@/api/client/queryClient"
import { Check, CheckCircle, Loader, ThumbsUpIcon, X } from "lucide-react"
import { useEffect } from "react"
import { toast } from "sonner"

interface SubmitRatingButtonProps {
    onClick: () => void
    isLoading: boolean
    isError: boolean
    isSuccess: boolean
}

const RateMovieButton = ({ onClick, isLoading, isError, isSuccess }: SubmitRatingButtonProps) => {
    useEffect(() => {
        if (isSuccess) {
            toast.success("successfully rated movie!", { 
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
            toast.error("Failed to rate movie...", { 
                icon: <X/>,
                style: { 
                    background: "red",
                    color: "#ffffff",
                    border: "#448094ff",
                }
            })
        }
    }, [isError])
    
    return (
        <button
            onClick={onClick}
            className="flex items-center justify-center space-x-1 w-fit px-3 py-1 bg-green-400/20 shadow-inner hover:bg-green-800 rounded-xl transition-colors duration-250"
        >   
            {isLoading ? (
                <div className="flex w-[2vw] justify-center">
                    <Loader className="animate-spin"/>
                </div>
            ) : isError ? (
                <>
                    <X size={18}/>
                    <span className="text-sm">Error rating</span>
                </>
            ) : isSuccess ? (
                <>
                    <Check size={18}/>
                    <span className="text-sm">Rated</span>
                </>
                
            ) : (
                <>
                    <ThumbsUpIcon size={18}/>
                    <span className="text-sm">Rate!</span>
                </>
            )}
        </button>
    )
}

export default RateMovieButton