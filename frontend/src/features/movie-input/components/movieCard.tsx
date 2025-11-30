import { PlusIcon, TrashIcon, Dot, Check, Loader, X, CheckCircle } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import type { TMDBMovieApiRes } from "@/shared/types/tmdb"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/shared/components/shadcn/dialog"
import { getGenreName } from "../utils/genreMap"
import { useFetchMovieCredits } from "../hooks/useFetchMovieCredits"
import { useRateMovie } from "../../../shared/hooks/useRateMovie"
import RateMovieButton from "@/shared/components/app/rateMovieButton"
import RateMovieStars from "../../../shared/components/app/rateMovieStars"
import { useAuth } from "@/shared/hooks/useAuth"
import { useWatchlist } from "@/shared/hooks/useWatchlist"
import { useQueryClient } from "@tanstack/react-query"
import { useAddToWatchlist } from "../hooks/useAddToWatchlist"
import { toast } from "sonner"

interface MovieCardProps {
    item: TMDBMovieApiRes;
    listView: boolean;
    gridView: boolean;
}

interface movieWatchlistItem {
    movie_id: string
    movie_name: string
    poster_path: string
    user_rating?: number
}

export default function MovieCard({ item, listView, gridView }: MovieCardProps) {
    const [rating, setRating] = useState(0);
    const [creditsDialogOpen, setCreditsDialogOpen] = useState(false);
    const { rateMovie, isLoading: isRating, isError: ratingError, isSuccess: ratingSuccess } = useRateMovie()
    const { addWatchlist, isLoading: isAdding, isError: watchlistError, isSuccess: watchlistSuccess } = useAddToWatchlist()
    const { user } = useAuth()
    const queryClient = useQueryClient()

    // Only fetch credits when dialog is opened
    const { data: credits, isLoading: creditsLoading } = useFetchMovieCredits({
        id: item.id,
        enabled: creditsDialogOpen
    });

    const { watchlist: watchlist = [] } = useWatchlist()
    const watchlistIds = useMemo(() => 
        new Set(watchlist.map((m: movieWatchlistItem) => m.movie_id)),
        [watchlist]
    )
    const isInWatchlist = watchlistIds.has(String(item.id))

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

    useEffect(() => {
        if (watchlistSuccess) {
            toast.success("Added to watchlist!", { 
                icon: <CheckCircle/>,
                style: { 
                    background: "#448094ff",
                    color: "#ffffff",
                    border: "#448094ff",
                }
            });
        }
    }, [watchlistSuccess])

    useEffect(() => {
        if (watchlistError) {
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
    }, [watchlistError])

    async function removeFromWatchlist(movieId: string) {
        queryClient.setQueryData(['watchlist', user.user_id], (old: movieWatchlistItem[] | undefined) =>
            (old || []).filter(m => m.movie_id !== movieId)
        );


        // Todo: remove from watchlist api call
    }

    return (
        <article
            key={item.id}
            className={
                `flex w-full relative text-xl font-semibold items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl group
                ${listView && "h-[20vh] "} ${gridView && "flex-col h-[35vh] pt-[1.5vh]"}`
            }
            role="listitem"
        >
            {listView ? (
                <>
                    <img
                        src={`https://image.tmdb.org/t/p/w500${item.poster_path}`}
                        className="w-[12.5%] h-[90%] bg-white object-cover object-top rounded-lg"
                    />
                    <section
                        className="flex flex-col w-[70%] h-full space-y-2 px-[2%] py-2"
                    >
                        <Dialog>
                            <DialogTrigger asChild>
                                <button className="text-left w-[90%] text-lg h-fit font-bold text-white truncate hover:text-teal-400 transition-colors">
                                    {item.title}
                                </button>
                            </DialogTrigger>
                            <DialogContent className="bg-[#2d4452]">
                                <DialogHeader>
                                    <DialogTitle className="text-xl">{item.title}</DialogTitle>
                                </DialogHeader>
                            </DialogContent>
                        </Dialog>
                        <div className="flex items-center">
                            <span className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                 border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                    {item.original_language}
                            </span>
                            <Dot size={18}/>
                            {item.genre_ids.length !== 0 ? (
                                <div className="flex flex-wrap w-fit gap-2 justify-center">
                                    {item.genre_ids.map((genreId, idx) => (
                                        <div
                                            key={idx}
                                            className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                                border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors"
                                        >
                                            {getGenreName(genreId)}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                                border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                    No Genres
                                </div>
                            )}
                            <Dot size={18}/>
                            {item.release_date !== "" ? (
                                <span className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                                border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                    {item.release_date}
                                </span>
                            ) : (
                                <span className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                                border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                    No Release Date
                                </span>
                            )}
                        </div>
                        <Dialog>
                            <DialogTrigger asChild>
                                <button className="text-left text-sm bg-[#375367] border-[0.1rem] border-[#20363e] text-gray-400 h-[45%] w-full p-1 rounded-lg overflow-hidden hover:bg-[#2d4452] transition-colors flex items-start">
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
                        {!isInWatchlist ? (
                            <button
                                onClick={() => addToWatchlist(item)}
                                className={`flex w-fit items-center space-x-1 px-2 py-1.5 ${watchlistError ? "bg-red-600 hover:bg-red-700" : "bg-teal-600 hover:bg-teal-700"} text-white rounded-md transition-colors duration-250`}
                            >  
                                {isAdding ? (
                                    <Loader className="animate-spin w-fit"/>
                                ) : watchlistError ? (
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
                        ) : (
                            <div className="flex items-center gap-2">
                                <button
                                    className="flex items-center space-x-1 px-3 py-1.5 bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner hover:bg-teal-800 rounded-xl transition-colors duration-250"
                                >
                                    <Check size={18} />
                                    <span className="text-sm">In Watchlist</span>
                                </button>
                                <RateMovieStars
                                    rating={rating}
                                    setRating={setRating}
                                />
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => removeFromWatchlist(String(item.id))}
                                        className="flex items-center space-x-1 px-3 py-1.5 bg-slate-500/40 hover:bg-red-600 rounded-md transition-colors duration-250"
                                    >
                                        <TrashIcon size={18}/>
                                        <span className="text-sm">Remove</span>
                                    </button>
                                    <RateMovieButton
                                        onClick={() => rateMovie(false, user.user_id, item, rating)}
                                        isLoading={isRating}
                                        isError={ratingError}
                                        isSuccess={ratingSuccess}
                                    />
                                </div>
                            </div>
                        )}
                    </section>
                    <section
                        className="flex flex-col items-center h-[80%] space-y-[2vh] w-[25%]"
                    >
                        <div className="flex space-x-2 items-center">
                            <div className="inline-flex items-center h-5 bg-yellow-500/20 backdrop-blur-sm text-amber-100 text-xs font-semibold rounded-full px-2.5
                                leading-none border border-amber-400/50 shadow-sm hover:bg-yellow-500/30 transition-colors">
                                Avg rating: {item?.vote_average.toFixed(1)}
                            </div>
                            <div className="inline-flex items-center h-5 bg-yellow-500/20 backdrop-blur-sm text-amber-100 text-xs font-semibold rounded-full px-2.5
                                leading-none border border-amber-400/50 shadow-sm hover:bg-yellow-500/30 transition-colors">
                                Popularity: {item?.popularity.toFixed(1)}
                            </div>
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className="text-sm text-gray-200">Actors/Directors</span>
                            <Dialog open={creditsDialogOpen} onOpenChange={setCreditsDialogOpen}>
                                <DialogTrigger asChild>
                                    <button className="bg-teal-600 text-white text-xs px-3 py-1 hover:bg-teal-700 rounded-md border-1 border-teal-400 transition-colors duration-250">
                                        View All
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
                    </section>
                </>
            ) : gridView && (
                <>
                    <section className="relative w-[95%] h-[70%]">
                        <img
                            src={`https://image.tmdb.org/t/p/w500${item.poster_path}`}
                            className="w-full h-full bg-white object-cover object-top rounded-lg"
                        />
                        <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-[#394B51] to-transparent pointer-events-none"></div>
                    </section>
                    <Dialog>
                        <DialogTrigger asChild>
                            <span className="text-[16px] truncate w-[80%] hover:text-teal-400 transition-colors duration-250">{item.title}</span>
                        </DialogTrigger>
                        <DialogContent className="bg-[#2d4452]">
                            <DialogHeader>
                                <DialogTitle className="text-xl">{item.title}</DialogTitle>
                            </DialogHeader>
                        </DialogContent>
                    </Dialog> 
                    <section className="flex w-[95%] items-center mt-2">
                        {item.release_date !== "" ? (
                            <span
                                className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                            border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                {item.release_date.slice(0,4)}
                            </span>
                        ) : (
                            <span 
                                className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors"
                            >
                                No Release Date
                            </span>
                        )}
                        <Dot size={18}/>
                        <div className="flex w-[20%] items-center">
                            <span
                                className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                            border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                {item.original_language}
                            </span>                        
                        </div>                    
                    </section>
                    <div className="flex space-x-2 w-[95%] mt-2">
                        {item.genre_ids.slice(0,2).map((genre: number, idx: number) => (
                            <div
                                key={idx}
                                className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                {getGenreName(genre)}
                            </div>
                        ))}
                        {item.genre_ids.length > 2 && (
                            <button className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-1 py-0.5 border
                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors"
                            >
                                +{item.genre_ids.length - 2} more
                            </button>
                        )}
                    </div>
                    {isInWatchlist && (
                        <div className="absolute top-0 right-0 flex items-center gap-1 px-2 py-1 bg-emerald-700/90 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full shadow-lg border border-emerald-500 z-10">
                            <Check size={12} />
                            <span>In Watchlist</span>
                        </div>
                    )}  
                    {/* Hover overlay with blur */}
                    <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex flex-col justify-center items-center gap-3 transition-opacity duration-200 backdrop-blur-md rounded-xl">
                        {!isInWatchlist ? (
                            <button
                                onClick={() => addToWatchlist(item)}
                                className="flex items-center space-x-1 px-3 py-2 bg-teal-600 text-white hover:bg-teal-700 rounded-md transition-colors duration-250"
                            >  
                                {isAdding ? (
                                    <Loader className="animate-spin"/>
                                ) : watchlistError ? (
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
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <RateMovieStars
                                    rating={rating}
                                    setRating={setRating}
                                />
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => removeFromWatchlist(String(item.id))}
                                        className="flex items-center space-x-1 px-2 py-1 bg-slate-500/40 hover:bg-red-600 rounded-md transition-colors duration-250"
                                    >
                                        <TrashIcon size={14}/>
                                        <span className="text-xs">Remove</span>
                                    </button>
                                    <RateMovieButton
                                        onClick={() => rateMovie(false, user.user_id, item, rating)}
                                        isLoading={isRating}
                                        isError={ratingError}
                                        isSuccess={ratingSuccess}
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                </>
            )}
            

            {/*
            <section
                className={`flex flex-col ${listView && "w-[70%]"} ${gridView && "w-[60%]"} h-[90%] space-y-2 px-[2%]`}
            >
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
            </section>*/}
        </article>
    );
}
