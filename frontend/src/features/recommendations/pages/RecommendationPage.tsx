import {  useState } from "react"
import Header from "@/features/navbar/components/Header"
import { useGetRecommendations } from "../hooks/useGetRecommendations";
import { useRecommendationIndex } from "../hooks/useRecommendationRating";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRateMovie } from "@/shared/hooks/useRateMovie";
import RateMovieStars from "@/shared/components/app/rateMovieStars";
import RateMovieButton from "@/shared/components/app/rateMovieButton";
import LoadingMovieRecommendationsSkeleton from "../components/loadingSkeleton";

export default function RecommendationPage() {
    {/*I probebly don't have to do this? But I'm going to do it for now. Change this if its not needed*/}
    const [ rating, setRating ] = useState(0);
    const { user, isLoading: authLoading } = useAuth()
    const [ isRefetching, setIsRefetching ] = useState<boolean>(false)
    const { recommendations = [], isLoading, refetchRecommendations } = useGetRecommendations(user?.user_id || '')
    const { currentIndex, nextMovie, resetIndex } = useRecommendationIndex(user?.user_id)
    const { rateMovie, isLoading: isRating, isError: ratingError, isSuccess: ratingSuccess } = useRateMovie()

    const currentMovie = recommendations[currentIndex]

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
                <div className="flex h-[90vh] space-x-[5%] px-[5%] w-full left-center items-center text-center ">
                    {(authLoading || isLoading || isRefetching) ? (
                        <LoadingMovieRecommendationsSkeleton />
                    ) : !currentMovie ? (
                        <div className="flex h-[90vh] w-full justify-center items-center">
                            <p className="text-white text-3xl">No recommendations available</p>
                        </div>
                    ) : (
                        <>
                            {/*This will be the movies name and the body of the actual movie image*/}
                            <section className="flex flex-col relative items-center pt-[2.5vh] h-[32.5rem] w-[30rem] bg-[#394B51] shadow-md shadow-black rounded-xl">
                                <span className="bold text-white text-3xl font-semibold">
                                    {currentMovie.title}
                                </span>
                                <div className="flex space-x-2 absolute bottom-6">
                                    <RateMovieStars rating={rating} setRating={setRating} />
                                    <RateMovieButton 
                                        onClick={handleMovieRated}
                                        isLoading={isRating}
                                        isError={ratingError}
                                        isSuccess={ratingSuccess}
                                    />
                                </div>
                                
                            </section>

                            {/*background flavor-image for description (Don't touch)*/}
                            <section className="flex flex-col relative bg-[#394B51] h-[32.5rem] w-[50.5rem] px-[0.5vw] py-[2.5vh] rounded-xl shadow-md shadow-black rounded-xl">
                                {/*Publisher - who made the movie here.*/}
                                <div className="flex ml-[12px] space-x-[20px]">
                                    <span className="text-white  text-3xl text-[25px]"> Directors: </span>
                                    {currentMovie.director.slice(0, 4).map((director: string, idx: number) => (
                                        <div 
                                            key={idx}
                                            className="flex items-center bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 text-md rounded-xl border-teal-400 px-3 py-1 border-[0.1rem]"
                                        >
                                            {director}
                                        </div>
                                    ))}
                                    {currentMovie.director.length > 4 && (
                                        <button className="text-teal-400 text-[20px] hover:text-teal-300">
                                            +{currentMovie.director.length - 5} more
                                        </button>
                                    )}
                                </div>
                                
                                {/*Actors*/}
                                <div className="flex ml-[12px] space-x-[20px] mt-[20px]">
                                    <span className="text-white text-3xl text-[25px] mr-11"> Actors: </span>
                                    {currentMovie.actors.slice(0, 4).map((actor: string, idx: number) => (
                                        <div 
                                            key={idx}
                                            className="flex items-center bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 text-md rounded-xl border-teal-400 px-3 py-1 border-[0.1rem]"
                                        >
                                            {actor}
                                        </div>
                                    ))}
                                    {currentMovie.actors.length > 4 && (
                                        <button className="text-teal-400 text-[20px] hover:text-teal-300">
                                            +{currentMovie.actors.length - 5} more
                                        </button>
                                    )}
                                    </div>
                                {/*Extra Box for detail under description (background)*/}
                                <div className="bg-[#375367] h-[19.7rem] text-start p-4 mt-[20px] w-[48rem] rounded-[15px] ml-[8px] border-[0.1rem] border-[#20363e]">
                                    {/*Description - what is this movie about.*/}
                                    <p className="text-white text-3xl text-[20px]">{currentMovie.summary} </p>
                                </div>

                                <div className="flex w-full items-center mt-[20px] px-4 justify-between">
                                    {/*Date - when was it made*/}
                                    <div className="flex items-center justify-center ml-[-9px] bg-[#375367] h-[2.6rem] px-4 rounded-[15px] border-[0.1rem] border-[#20363e]">
                                        <p className="text-teal-200 shadow-inner text-lg rounded-xl border-teal-400  px-3 py-1">{currentMovie.release_date}</p>
                                    </div>
                                    {/*Genere*/}
                                    <div className="flex space-x-4 px-4 bg-[#375367] h-[2.6rem] py-1 w-fit rounded-[15px] border-[0.1rem] border-[#20363e]">
                                        {currentMovie.genres.map((genre: string, idx: number) => (
                                            <div 
                                                key={idx}
                                                className="flex items-center bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 text-sm rounded-xl border-teal-400 px-3 border-[0.1rem]"
                                            >
                                                {genre}
                                            </div>
                                        ))}
                                    </div>
                                    {/*Languages*/}
                                    <div className="flex items-center justify-center bg-[#375367] h-[2.6rem] w-[8rem] rounded-[15px] border-[0.1rem] border-[#20363e]">
                                        <p className="bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 text-sm rounded-xl border-teal-400 px-3 py-1 border-[0.1rem]">
                                        Languages
                                        </p>
                                    </div>
                                </div>
                            </section>
                        
                        </>
                    )}
                </div>
        </main>
    )
}

