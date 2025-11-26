import { ThumbsUpIcon, PlusIcon, TrashIcon, Heart, Loader, Check, X } from "lucide-react"
import { useState } from "react"
import type { TMDBMovieApiRes } from "@/app/types/tmdb"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/shared/components/shadcn/dialog"
import { getGenreName } from "../utils/genreMap"
import { useFetchMovieCredits } from "../hooks/useFetchMovieCredits"
import RateMovieButtons from "./rateButtons"
import { useRateMovie } from "../hooks/useRateMovie"

interface MovieCardProps {
    item: TMDBMovieApiRes;
    listView: boolean;
    gridView: boolean;
}

export default function MovieCard({ item, listView, gridView }: MovieCardProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [rating, setRating] = useState(0);
    const [creditsDialogOpen, setCreditsDialogOpen] = useState(false);
    const { rateMovie, isLoading: isRating, isError: ratingError, isSuccess: ratingSuccess } = useRateMovie()

    // Only fetch credits when dialog is opened
    const { data: credits, isLoading: creditsLoading } = useFetchMovieCredits({
        id: item.id,
        enabled: creditsDialogOpen
    });

    

    const handleAdd = () => {
        setIsOpen(true);
    };

    const handleRemove = () => {
        setIsOpen(false);
    };

    return (
        <li
            className={
                `flex w-full text-xl font-semibold items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl
                ${listView && "h-[25%]"} ${gridView && "max-h-[20vh]"}`
            }
            role="listitem"
        >
            <img className={`bg-white ${listView && "w-[10%]"} ${gridView && "w-[20%]"} h-[85%]`}/>
            <section
                className={`flex flex-col ${listView && "w-[70%]"} ${gridView && "w-[60%]"} h-[90%] space-y-2 px-[2%]`}
            >
                <Dialog>
                    <DialogTrigger asChild>
                        <button className="text-left w-[90%] text-lg h-[40%] font-bold text-white truncate hover:text-teal-400 transition-colors">
                            {item.title}
                        </button>
                    </DialogTrigger>
                    <DialogContent className="bg-[#2d4452]">
                        <DialogHeader>
                            <DialogTitle className="text-xl">{item.title}</DialogTitle>
                        </DialogHeader>
                    </DialogContent>
                </Dialog>
                <Dialog>
                    <DialogTrigger asChild>
                        <button className="text-left text-sm bg-[#375367] border-[0.1rem] border-[#20363e] text-gray-400 h-3/4 w-full p-1 rounded-lg overflow-hidden hover:bg-[#2d4452] transition-colors flex items-start">
                            <div className="line-clamp-3 w-full">
                                {item.overview !== "" ? item.overview : "No overview"}
                            </div>
                        </button>
                    </DialogTrigger>
                    <DialogContent className="bg-[#2d4452] max-w-2xl">
                        <DialogHeader>
                            <DialogTitle className="text-xl text-white">Movie overview</DialogTitle>
                        </DialogHeader>
                        <div className="text-gray-300 mt-4 max-h-96 overflow-y-auto">
                            {item.overview !== "" ? item.overview : "No overview available"}
                        </div>
                    </DialogContent>
                </Dialog>
                <div className="flex items-center space-x-3 w-[100%]">
                    {!isOpen ? (
                        <button
                            onClick={handleAdd}
                            className="flex items-center space-x-1 px-3 py-1.5 bg-teal-600 text-white hover:bg-teal-700 rounded-xl transition-colors duration-250"
                        >
                            <PlusIcon size={18} />
                            <span className="text-sm">Add</span>
                        </button>
                    ) : (
                        <button
                            onClick={handleAdd}
                            className="flex items-center space-x-1 px-3 py-1.5 bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner hover:bg-teal-800 rounded-xl transition-colors duration-250"
                        >
                            <Heart size={18} />
                            <span className="text-sm">Added!</span>
                        </button>
                    )}
                    {isOpen && (
                        <div className="w-[80%] flex">
                            <button
                                onClick={handleRemove}
                                className="flex items-center space-x-1 px-3 py-1 bg-slate-500/40 hover:bg-red-600 rounded-xl transition-colors duration-250"
                            >
                                <TrashIcon size={18}/>
                                <span className="text-sm">Remove</span>
                            </button>
                            <RateMovieButtons
                                rating={rating}
                                setRating={setRating}
                            />
                            <button
                                onClick={() => rateMovie(item, rating)}
                                className="flex items-center justify-center space-x-1 w-fit px-3 py-1 bg-green-400/20 shadow-inner hover:bg-green-800 rounded-xl transition-colors duration-250"
                            >   
                                {isRating ? (
                                    <div className="flex w-[2vw] justify-center">
                                        <Loader className="animate-spin"/>
                                    </div>
                                ) : ratingError ? (
                                    <>
                                        <X size={18}/>
                                        <span className="text-sm">Error rating</span>
                                    </>
                                ) : ratingSuccess ? (
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
                        </div>
                    )}
                </div>
            </section>
            <section
                className={`flex flex-col items-center h-[80%] justify-between ${listView && "w-[25%]"} ${gridView && "w-[30%]"}`}
            >
                {item.genre_ids.length !== 0 ? (
                    <div className="flex flex-wrap gap-2 justify-center">
                        {item.genre_ids.map((genreId, idx) => (
                            <div
                                key={idx}
                                className="px-2 py-1 text-xs bg-teal-500/20 border border-teal-400 text-teal-200 shadow-inner rounded-md"
                            >
                                {getGenreName(genreId)}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="px-2 py-1 text-xs bg-teal-500/20 border border-teal-400 text-teal-200 shadow-inner rounded-md">
                        No Genres
                    </div>
                )}
                <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-200">Actors/Directors</span>
                    <Dialog open={creditsDialogOpen} onOpenChange={setCreditsDialogOpen}>
                        <DialogTrigger asChild>
                            <button className="bg-teal-600 text-white text-xs px-3 py-1 hover:bg-teal-700 rounded-md border-1 border-teal-400 transition-colors duration-250">
                                View More
                            </button>
                        </DialogTrigger>
                        <DialogContent className="bg-[#2d4452] max-w-2xl">
                            <DialogHeader>
                                <DialogTitle className="text-xl text-white">Cast & Crew</DialogTitle>
                            </DialogHeader>
                            {creditsLoading ? (
                                <div className="text-gray-300 mt-4">Loading...</div>
                            ) : (
                                <>
                                    <div className="text-gray-300 mt-4">
                                        <span className="font-semibold">Actors: </span>
                                        {credits?.actors.join(', ') || 'No actors available'}
                                    </div>
                                    <div className="text-gray-300 mt-4">
                                        <span className="font-semibold">Directors: </span>
                                        {credits?.directors.join(', ') || 'No directors available'}
                                    </div>
                                </>
                            )}
                        </DialogContent>
                    </Dialog>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-200">Release Date: </span>
                    {item.release_date !== "" ? (
                        <span className="px-1 py-1 text-xs bg-teal-500/20 border border-teal-400 text-teal-200 shadow-inner rounded-md">
                            {item.release_date}
                        </span>
                    ) : (
                        <span className="px-1 py-1 text-xs bg-teal-500/20 border border-teal-400 text-teal-200 shadow-inner rounded-md">
                            No Release Date
                        </span>
                    )}
                </div>
            </section>
        </li>
    );
}
