import { Check, Loader, ThumbsUpIcon, X } from "lucide-react"

interface SubmitRatingButtonProps {
    onClick: () => void
    isLoading: boolean
    isError: boolean
    isSuccess: boolean
}

const RateMovieButton = ({ onClick, isLoading, isError, isSuccess }: SubmitRatingButtonProps) => {
    
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