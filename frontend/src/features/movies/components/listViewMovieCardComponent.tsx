import { Dialog, DialogContent, DialogHeader, DialogTrigger } from "@/shared/components/shadcn/dialog"
import type { Movie } from "@/shared/types/tmdb"
import { DialogTitle } from "@radix-ui/react-dialog"
import { Check, Dot } from "lucide-react"
import { getGenreName } from "../utils/genreMap"
import AddToWatchlistButton from "./addToWatchlistButton"
import type { movieWatchlistItem } from "../types/watchlist"
import { useMemo, useState } from "react"
import RateMovieStars from "@/shared/components/app/rateMovieStars"
import RemoveFromWatchlistButton from "./removeFromWatchlistButton"
import RateMovieButton from "@/shared/components/app/rateMovieButton"
import { useRateMovie } from "@/shared/hooks/useRateMovie"
import { useAuth } from "@/shared/hooks/useAuth"
import { useFetchMovieCredits } from "../hooks/useFetchMovieCredits"

const ListViewMovieCardComponent = ({ item, isSearchPage, watchlist }: { item: Movie, isSearchPage: boolean, watchlist: movieWatchlistItem[]}) => {
    const [rating, setRating] = useState(0);
    const watchlistIds = useMemo(() => 
        new Set(watchlist.map((m: movieWatchlistItem) => m.movie_id)),
        [watchlist]
    )
    const isInWatchlist = watchlistIds.has(String(item.id))
    const { rateMovie, isLoading: isRating, isError: ratingError, isSuccess: ratingSuccess } = useRateMovie()
    const { user } = useAuth()
    const [creditsDialogOpen, setCreditsDialogOpen] = useState(false);

    let genres = item.genre_ids 
        ? item.genres
        : []

    // Only fetch credits when dialog is opened
    const { data: credits, isLoading: creditsLoading } = useFetchMovieCredits({
        id: item.id,
        enabled: creditsDialogOpen
    });

    return (
        <article
            key={item.id}
            className="flex w-full relative text-xl font-semibold items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl group
                min-h-[20vh] py-2"
            role="listitem"
        >
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
                            {item.original_language || item.language}
                    </span>
                    <Dot size={18}/>
                    {genres?.length !== 0 ? (
                        <div className="flex flex-wrap w-fit gap-2 justify-center">
                            {isSearchPage && item.genre_ids.map((genreId, idx) => (
                                <div
                                    key={idx}
                                    className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors"
                                >
                                    {getGenreName(genreId)}
                                </div>
                            ))}
                            {!isSearchPage && item.genre_ids.map((genre, idx) => (
                                <div
                                    key={idx}
                                    className="inline-block bg-sky-500/20 backdrop-blur-sm text-teal-200 text-xs font-semibold rounded-full px-2.5 py-0.5 border
                                                        border-teal-400/50 shadow-sm hover:bg-sky-500/30 transition-colors"
                                >
                                    {genre}
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
                    {!isSearchPage && (
                        <>
                            <Dot size={18}/>
                            <div className="flex items-center gap-1 px-2 py-1 bg-emerald-700/90 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full shadow-lg border border-emerald-500 z-10">
                                <Check size={12} />
                                <span>Added on: {item.added_at}</span>
                            </div> 
                        </>
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
                {!isInWatchlist && isSearchPage ? (
                    <AddToWatchlistButton item={item}/>
                ) : isSearchPage ? (
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
                ) : (
                    <div className="">
                        <RemoveFromWatchlistButton movie_id={String(item.id)}/>
                    </div>
                )}
            </section>
            {isSearchPage && (
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
            )}
        </article>
    )
}

export default ListViewMovieCardComponent