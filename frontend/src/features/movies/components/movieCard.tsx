import { Dot, Check } from "lucide-react"
import { useMemo, useState } from "react"
import type { TMDBMovieApiRes } from "@/shared/types/tmdb"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/shared/components/shadcn/dialog"
import { getGenreName } from "../utils/genreMap"
import { useFetchMovieCredits } from "../hooks/useFetchMovieCredits"
import { useRateMovie } from "../../../shared/hooks/useRateMovie"
import RateMovieButton from "@/shared/components/app/rateMovieButton"
import RateMovieStars from "../../../shared/components/app/rateMovieStars"
import { useAuth } from "@/shared/hooks/useAuth"
import { useWatchlist } from "@/shared/hooks/useWatchlist"
import AddToWatchlistButton from "./addToWatchlistButton"
import type { movieWatchlistItem } from "../types/watchlist"
import RemoveFromWatchlistButton from "./removeFromWatchlistButton"

interface MovieCardProps {
    item: TMDBMovieApiRes;
    listView: boolean;
    gridView: boolean;
}

export default function MovieCard({ item, listView, gridView }: MovieCardProps) {
    const [rating, setRating] = useState(0);
    const [creditsDialogOpen, setCreditsDialogOpen] = useState(false);
    const { rateMovie, isLoading: isRating, isError: ratingError, isSuccess: ratingSuccess } = useRateMovie()
    const { user } = useAuth()

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


    return (
        <article
            key={item.id}
            className={
                `flex w-full relative text-xl font-semibold items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl group
                ${listView && "min-h-[20vh] py-2"} ${gridView && "flex-col h-[35vh] pt-[1.5vh]"}`
            }
            role="listitem"
        >
            {listView ? (
                <>
                    <img
                        src={`https://image.tmdb.org/t/p/w500${item.poster_path}`}
                        className="min-w-[12.5%] h-[20vh] bg-white object-cover object-top rounded-lg"
                    />
                    <section className="flex flex-col flex-grow min-w-0 min-h-[20vh] space-y-2 px-[2%]">
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
                                <button className="flex-1 text-left text-sm bg-[#375367] border-[0.1rem] border-[#20363e] text-gray-400 w-full p-1 rounded-lg overflow-hidden hover:bg-[#2d4452] transition-colors flex items-start">
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
                            <AddToWatchlistButton item={item}/>
                        ) : (
                            <div className="flex items-center gap-2">
                                <button
                                    className="flex items-center space-x-1 px-3 py-1.5 bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner hover:bg-teal-800 rounded-xl transition-colors duration-250"
                                >
                                    <Check size={18} />
                                    <span className="text-sm truncate">In Watchlist</span>
                                </button>
                                <RateMovieStars
                                    rating={rating}
                                    setRating={setRating}
                                />
                                <div className="flex gap-2">
                                    <RemoveFromWatchlistButton movie_id={String(item.id)}/>
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
                    <section className="flex flex-col min-h-[20vh] py-[1vh] w-fit space-y-[2vh] flex-shrink-0 ml-auto pr-2">
                        <div className="flex space-x-2 items-center w-fit">
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
                    <section className="relative w-[95%] h-[70%] min-h-[150px]">
                    {item.poster_path ? (
                        <img
                            src={`https://image.tmdb.org/t/p/w500${item.poster_path}`}
                            className="w-full h-full object-cover object-top rounded-lg"
                        />
                    ) : (
                        <div className="w-full h-full rounded-lg bg-[#2f3f44] flex items-center justify-center 
                                        text-gray-400 text-xs border border-white/10">
                            No Image
                        </div>
                    )}

                    {item.poster_path && (
                        <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t 
                                        from-[#394B51] to-transparent pointer-events-none"></div>
                    )}
                </section>
                    <Dialog>
                        <DialogTrigger asChild>
                            <span className="text-[16px] truncate w-[80%] min-h-[1.5rem] hover:text-teal-400 transition-colors duration-250">{item.title}</span>
                        </DialogTrigger>
                        <DialogContent className="bg-[#2d4452]">
                            <DialogHeader>
                                <DialogTitle className="text-xl">{item.title}</DialogTitle>
                            </DialogHeader>
                        </DialogContent>
                    </Dialog> 
                    <section className="flex w-[95%] h-fit items-center mt-2">
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
                    <div className="flex space-x-2 w-[95%] h-fit my-2">
                        {item.genre_ids && item.genre_ids.slice(0,2).map((genre: number, idx: number) => (
                            <div
                                key={idx}
                                className="inline-block bg-sky-500/20 truncate backdrop-blur-sm text-teal-200 text-[0.55rem] font-semibold rounded-full px-2.5 py-0.5 border
                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                {getGenreName(genre)}
                            </div>
                        ))}
                        {item.genre_ids.length == 0 && (
                            <div
                                className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                                no genres
                            </div>
                        )}
                        {item.genre_ids.length > 2 && (
                            <button className="inline-block bg-sky-500/20 truncate backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-1 py-0.5 border
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
                            <AddToWatchlistButton item={item} />
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <RateMovieStars
                                    rating={rating}
                                    setRating={setRating}
                                />
                                <div className="flex gap-2">
                                    <RemoveFromWatchlistButton movie_id={String(item.id)}/>
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
        </article>
    );
}
