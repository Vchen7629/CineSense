import { useState, useEffect } from "react"
import Header from "@/features/navbar/components/Header"
import { useGetRecommendations } from "../hooks/useGetRecommendations";
import { useRecommendationIndex } from "../hooks/useRecommendationRating";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRateMovie } from "@/shared/hooks/useRateMovie";
import RateMovieStars from "@/shared/components/app/rateMovieStars";
import RateMovieButton from "@/shared/components/app/rateMovieButton";
import { Skeleton } from "@/shared/components/shadcn/skeleton";
import { Dot } from "lucide-react";
import LoadingMovieRecommendationsSkeleton from "../components/loadingSkeleton";


export default function RecommendationPage() {
    {/*I probebly don't have to do this? But I'm going to do it for now. Change this if its not needed*/}
    const [ rating, setRating ] = useState(0);
    const [ showContent, setShowContent ] = useState(false);
    const [ showSkeleton, setShowSkeleton ] = useState(false);
    const [ displayedMovie, setDisplayedMovie ] = useState<any>(null);
    const { user, isLoading: authLoading } = useAuth()
    const [ isRefetching, setIsRefetching ] = useState<boolean>(false)
    const { recommendations = [], isLoading, refetchRecommendations } = useGetRecommendations(user?.user_id || '')
    const { currentIndex, nextMovie, resetIndex } = useRecommendationIndex(user?.user_id)
    const { rateMovie, isLoading: isRating, isError: ratingError, isSuccess: ratingSuccess } = useRateMovie()

    const currentMovie = recommendations[currentIndex]
    const isLoadingState = authLoading || isLoading || isRefetching

    // Keep displaying previous movie while loading new one
    useEffect(() => {
        if (currentMovie && !isLoadingState) {
            setDisplayedMovie(currentMovie);
        }
    }, [currentMovie, isLoadingState]);

    // Crossfade transition effect - only on initial load, not when switching movies
    useEffect(() => {
        if (!displayedMovie) {
            // Initial load
            if (isLoadingState) {
                setShowContent(false);
            } else if (currentMovie) {
                const timer = setTimeout(() => setShowContent(true), 100);
                return () => clearTimeout(timer);
            }
        } else {
            // Already have content, keep it visible
            setShowContent(true);
        }
    }, [isLoadingState, currentMovie, displayedMovie])

    // handle user rating movies
    async function handleMovieRated() {
        try {
            await rateMovie(true, user.user_id, currentMovie, rating)
            setRating(0)
            
            // check if this was the last movie in batch
            if (currentIndex + 1 >= recommendations.length) {
                setIsRefetching(true)
                resetIndex() // reset to 0
                await refetchRecommendations() // refetch new batch of 10 movies
                setIsRefetching(false)
            } else {
                nextMovie()
            }
        } catch (error: any) {
            console.error("Failed to rate movie:", error)
            setIsRefetching(false)
        }
    }

    return (
        <main>
            <Header/>
                <div className="flex h-[90vh] space-x-[5%] px-[5%] w-full left-center items-center text-center">
                    {!displayedMovie && !isLoadingState ? (
                        <div className="flex h-[90vh] w-full justify-center items-center">
                            <p className="text-white text-3xl">No recommendations available</p>
                        </div>
                    ) : displayedMovie && (
                        <>
                            {/*This will be the movies name and the body of the actual movie image*/}
                            <section className="flex flex-col relative justify-center items-center h-[32.5rem] w-[30rem]">
                                {/* Skeleton - visible only if loading takes > 1s */}
                                {showSkeleton && (
                                    <div className={`absolute inset-0 transition-opacity duration-300 ${!showContent ? 'opacity-100' : 'opacity-0'}`}>
                                        <Skeleton className="h-[99%] w-[99%] rounded-xl" />
                                    </div>
                                )}
                                {/* Actual content - shows old data while loading */}
                                <img
                                    src={`https://image.tmdb.org/t/p/w500${displayedMovie.poster_path}`}
                                    className={`h-[99%] w-auto object-contain rounded-xl shadow-lg shadow-md shadow-black border-2 border-[#20363e] transition-opacity duration-300 ${showContent ? 'opacity-100' : 'opacity-0'}`}
                                    alt={displayedMovie.title}
                                />
                            </section>
                            <section className="flex flex-col space-y-[1vh] relative bg-[#394B51] h-[32.5rem] w-[50.5rem] px-[0.5vw] py-[2.5vh] rounded-xl shadow-md shadow-black">
                                {/* Skeleton overlay - visible only if loading takes > 500ms */}
                                {showSkeleton && 
                                    <LoadingMovieRecommendationsSkeleton 
                                        isLoadingState={isLoadingState} 
                                        showContent={showContent} 
                                        setShowSkeleton={setShowSkeleton}
                                    />
                                }
                                {/* Actual content - fades in when ready */}
                                <div className={`flex flex-col space-y-[1vh] transition-opacity duration-300 ${showContent ? 'opacity-100' : 'opacity-0'}`}>
                                    <div className="flex items-center justify-between w-[96%]">
                                        <span className="bold text-white text-left text-3xl font-semibold ml-[1vw] truncate w-[50%] oveflow-auto">
                                            {displayedMovie?.title}
                                        </span>
                                        <div className="flex space-x-2 items-center">
                                            <div className="inline-flex items-center h-5 bg-yellow-500/20 backdrop-blur-sm text-amber-100 text-xs font-semibold rounded-full px-2.5
                                                leading-none border border-amber-400/50 shadow-sm hover:bg-yellow-500/30 transition-colors">
                                                Avg rating: {displayedMovie?.tmdb_avg_rating.toFixed(1)}
                                            </div>
                                            <div className="inline-flex items-center h-5 bg-yellow-500/20 backdrop-blur-sm text-amber-100 text-xs font-semibold rounded-full px-2.5
                                                leading-none border border-amber-400/50 shadow-sm hover:bg-yellow-500/30 transition-colors">
                                                Popularity: {displayedMovie?.tmdb_popularity.toFixed(1)}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex space-x-2 ml-[2vw] mt-2">
                                        <RateMovieStars rating={rating} setRating={setRating} />
                                        <RateMovieButton
                                            onClick={handleMovieRated}
                                            isLoading={isRating}
                                            isError={ratingError}
                                            isSuccess={ratingSuccess}
                                        />
                                    </div>
                                    <div className="flex items-center ml-[2vw]">
                                        {/*Date - when was it made*/}
                                        <span
                                            className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                            {displayedMovie?.release_date}
                                        </span>
                                        <Dot size={28}/>
                                        {/*Languages*/}
                                        <span
                                            className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                            Language 1
                                        </span>
                                        <Dot size={28}/>
                                        <div className="flex space-x-2 w-fit">
                                            {displayedMovie?.genres.map((genre: string, idx: number) => (
                                                <div
                                                    key={idx}
                                                    className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                            border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                                    {genre}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    {/*Publisher - who made the movie here.*/}
                                    <div className="flex flex-col ml-[2vw]">
                                        <span className="text-left text-lg font-semibold text-gray-300"> Directors: </span>
                                        <div className="flex space-x-2 mt-2">
                                            {displayedMovie?.director.slice(0, 4).map((director: string, idx: number) => (
                                               <div
                                                    key={idx}
                                                    className="inline-flex items-center bg-teal-500/20 text-teal-200 text-sm font-medium rounded-full border border-teal-400/50 px-3
                                                        py-1 shadow-sm hover:bg-teal-500/30 transition-colors"
                                                >
                                                    {director}
                                                </div>
                                            ))}
                                            {displayedMovie?.director.length > 4 && (
                                                <button className="inline-flex items-center bg-teal-500/20 text-teal-200 text-sm font-medium rounded-full border border-teal-400/50 px-3
                                                        py-1 shadow-sm hover:bg-teal-500/30 transition-colors"
                                                >
                                                    +{displayedMovie.director.length - 5} more
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    {/*Actors*/}
                                    <div className="flex flex-col ml-[2vw] space-x-[20px]">
                                        <span className="text-left text-lg font-semibold text-gray-300"> Actors: </span>
                                        <div className="flex space-x-2 mt-2">
                                            {displayedMovie?.actors.slice(0, 5).map((actor: string, idx: number) => (
                                                <div
                                                    key={idx}
                                                    className="inline-flex items-center bg-teal-500/20 text-teal-200 text-sm font-medium rounded-full border border-teal-400/50 px-3
                                                        py-1 shadow-sm hover:bg-teal-500/30 transition-colors"
                                                >
                                                    {actor}
                                                </div>
                                            ))}
                                            {displayedMovie?.actors.length > 5 && (
                                                <button className="inline-flex items-center bg-teal-500/20 text-teal-200 text-sm font-medium rounded-full border border-teal-400/50 px-3
                                                        py-1 shadow-sm hover:bg-teal-500/30 transition-colors"
                                                >
                                                    +{displayedMovie.actors.length - 5} more
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                    {/*background flavor-image for description (Don't touch)*/}
                                    <div className="bg-[#375367] h-[11.7rem] text-start px-4 py-2 mt-[20px] w-[92.5%] rounded-[15px] overflow-auto ml-[2vw] border-[0.1rem] border-[#20363e]">
                                        {/*Description - what is this movie about.*/}
                                        <p className="text-white text-md">{displayedMovie?.summary}</p>
                                    </div>
                                </div>
                            </section>
                        </>
                    )}
                </div>
        </main>
    )
}

