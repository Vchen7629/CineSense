import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/shared/components/shadcn/dialog"
import { Check, Dot, Star } from "lucide-react"
import { getGenreName } from "../utils/genreMap"
import { useMemo, useState, useEffect } from "react"
import type { movieWatchlistItem } from "../types/watchlist"
import AddToWatchlistButton from "./addToWatchlistButton"
import RateMovieStars from "@/shared/components/app/rateMovieStars"
import RemoveFromWatchlistButton from "./removeFromWatchlistButton"
import RateMovieButton from "@/shared/components/app/rateMovieButton"
import { useRateMovie } from "@/shared/hooks/useRateMovie"
import { useAuth } from "@/shared/hooks/useAuth"

const GridViewMovieCardComponent = ({ movie, showRating, watchlist, isSearchPage }: any) => {
    const [rating, setRating] = useState(0);
    const [watchlistRating, setWatchlistRating] = useState<number>(0)
    const { rateMovie, isLoading: isRating, isError: ratingError, isSuccess: ratingSuccess } = useRateMovie()
    const { user } = useAuth()

    // Set watchlist rating from movie prop
    useEffect(() => {
        if (movie.rating !== undefined) {
            setWatchlistRating(movie.rating)
        }
    }, [movie.rating])

    const releaseYear = movie.release_date 
        ? String(movie.release_date).slice(0, 4)
        : null

    // handle both genre formats
    const displayGenres = movie.genres 
        ? movie.genres 
        : movie.genre_ids?.map(getGenreName)

    const watchlistIds = useMemo(() =>
        new Set((watchlist || []).map((m: movieWatchlistItem) => (m.movie_id))),
        [watchlist]
    )
    const isInWatchlist = watchlistIds.has(String(movie.id || movie.movie_id))
    
    return (
        <article
            key={movie.id}
            className="flex w-full relative text-xl font-semibold items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl group
                flex-col h-[35vh] pt-[1.5vh]"
            role="listitem"
        >
            <section className="relative w-[95%] h-[70%] min-h-[150px]">
                {movie.poster_path ? (
                    <img
                        src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                        className="w-full h-full object-cover object-top rounded-lg"
                    />
                ) : (
                    <div className="w-full h-full items-center rounded-lg bg-[#2f3f44] flex justify-center border border-white/10">
                        <span className="text-gray-400 text-xs">No Image</span>
                    </div>
                )}
                <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-[#394B51] to-transparent pointer-events-none"/>
            </section>
            <Dialog>
                <DialogTrigger asChild>
                    <span className="text-[16px] truncate w-[80%] min-h-[1.5rem] hover:text-teal-400 transition-colors duration-250">{movie.title}</span>
                </DialogTrigger>
                <DialogContent className="bg-[#2d4452]">
                    <DialogHeader>
                        <DialogTitle className="text-xl">{movie.title}</DialogTitle>
                    </DialogHeader>
                </DialogContent>
            </Dialog> 
            <section className="flex w-[95%] items-center h-fit movies-center mt-2">
                {movie.release_date !== "" ? (
                    <span
                        className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                    border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                        {releaseYear}
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
                <div className="flex w-fit movies-center">
                    <span
                        className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                    border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors">
                        {movie.language || movie.original_language}
                    </span>                        
                </div>
                <Dot size={18}/> 
                {(showRating && watchlistRating > 0) && (
                    <div className="flex w-fit justify-center gap-0.5">
                        {[1, 2, 3, 4, 5].map((starIndex) => {
                            const fillPercentage = Math.max(0, Math.min(1, watchlistRating - (starIndex - 1)))
                            return (
                                <div key={starIndex} className="relative inline-block">
                                    <Star size={17} className="stroke-emerald-600" />
                                    <div
                                        className="absolute top-0 left-0 overflow-hidden"
                                        style={{ width: `${fillPercentage * 100}%` }}
                                    >
                                        <Star size={17} className="stroke-emerald-600 fill-emerald-600" />
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}
                {(watchlistRating == 0 && showRating) && (
                    <span className="inline-block bg-emerald-700/90 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border
                                border-emerald-500 shadow-sm hover:bg-sky-500/30 transition-colors"
                    >
                        Not Rated
                    </span>
                )}                   
            </section>
            <div className="flex space-x-2 w-[95%] h-fit my-2">
                {displayGenres.length > 0 ? (
                    <>
                        {displayGenres.slice(0, 2).map((genre: string, idx: number) => (
                            <div
                                key={idx}
                                className="inline-block bg-sky-500/20 truncate backdrop-blur-sm text-teal-200 text-[0.55rem] font-semibold rounded-full px-2.5 py-0.5 border border-teal-400/50 shadow-sm 
                                    hover:bg-sky-500/30 transition-colors">
                                {genre}
                            </div>
                        ))}
                        {displayGenres.length > 2 && (
                            <button className="inline-block bg-sky-500/20 truncate backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-1 py-0.5 border border-teal-400/50 shadow-sm 
                                hover:bg-sky-500/30 transition-colors">
                                +{displayGenres.length - 2} more
                            </button>
                        )}
                    </>
                ) : (
                    <div className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border border-teal-400/50 shadow-sm hover:bg-sky-500/30 
                        transition-colors">
                        No genres
                    </div>
                  )}
            </div>
            {isInWatchlist && isSearchPage && (
                <div className="absolute top-0 right-0 flex items-center gap-1 px-2 py-1 bg-emerald-700/90 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full shadow-lg border border-emerald-500 z-10">
                    <Check size={12} />
                    <span>In Watchlist</span>
                </div>
            )} 
            {isInWatchlist && !isSearchPage && (
                <div className="absolute top-0 right-0 flex items-center gap-1 px-2 py-1 bg-emerald-700/90 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full shadow-lg border border-emerald-500 z-10">
                    <Check size={12} />
                    <span>Added on: {movie.added_at}</span>
                </div> 
            )}
            {/* Hover overlay with blur */}
            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex flex-col justify-center items-center gap-3 transition-opacity duration-200 backdrop-blur-md rounded-xl">
                {!isInWatchlist && isSearchPage ? (
                    <AddToWatchlistButton item={movie} />
                ) : isSearchPage ? (
                    <div className="flex flex-col items-center gap-2">
                        <RateMovieStars
                            rating={rating}
                            setRating={setRating}
                        />
                        <div className="flex gap-2">
                            <RemoveFromWatchlistButton movie_id={String(movie.id)}/>
                            <RateMovieButton
                                onClick={() => rateMovie(false, user.user_id, movie, rating)}
                                isLoading={isRating}
                                isError={ratingError}
                                isSuccess={ratingSuccess}
                            />
                        </div>
                    </div>
                ) : (
                    <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex flex-col justify-center items-center gap-3 transition-opacity duration-200 backdrop-blur-md rounded-xl">
                        <RemoveFromWatchlistButton movie_id={movie.movie_id}/>
                    </div>
                )}
            </div>
        </article>
    )
}

export default GridViewMovieCardComponent