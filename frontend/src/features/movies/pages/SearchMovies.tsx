import Header from "@/features/navbar/components/Header";
import { useState, useMemo } from "react";
import GridListViewComponent from "../components/gridListViewComponent";
import { useSearchMovies } from "../hooks/useSearchMovies";
import type { TMDBMovieApiRes } from "@/shared/types/tmdb";
import MovieCard from "../components/movieCard";
import LoadingMovieSkeleton from "../components/loadingMovieSkeleton";
import MovieFilterCard from "../components/movieFilterCard";
import { getGenreName } from "../utils/genreMap";
import { getLanguageName } from "../utils/languageMap";
import { Toaster } from "sonner";
import { filterMovies } from "../utils/filterMovieResults";
import ListViewMovieCardComponent from "../components/listViewMovieCardComponent";
import { useWatchlist } from "@/shared/hooks/useWatchlist";
import GridViewMovieCardComponent from "../components/gridViewMovieCardComponent";

const SearchMoviesPage = () => {
    const [currentPage, setCurrentPage] = useState<number>(1)
    const [apiQuery, setApiQuery] = useState<string>("")
    const [searchQuery, setSearchQuery] = useState<string>("") // Only updates on button click
    const [gridView, setGridView] = useState<boolean>(false)
    const [listView, setListView] = useState<boolean>(true)
    const [itemsPerPage, setItemsPerPage] = useState<number>(5)
    const [genreFilterValue, setGenreFilterValue] = useState<string>("")
    const [languageFilterValue, setLanguageFilterValue] = useState<string>("")
    const [yearFilterValue, setYearFilterValue] = useState<string>("")
    const { watchlist: watchlist = [] } = useWatchlist()

    // React Query hook with loading state
    const { data: apiRes = [], isLoading, error } = useSearchMovies({
        query: searchQuery,
        maxPages: 5,
        enabled: searchQuery.length > 0
    })

    // filtering logic
    const filteredApiRes = useMemo(() => (
        filterMovies(apiRes, {
            genre: genreFilterValue,
            language: languageFilterValue,
            year: yearFilterValue
        })
    ), [apiRes, genreFilterValue, languageFilterValue, yearFilterValue]);

    const totalPage = Math.ceil(filteredApiRes.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    const paginatedMovies = filteredApiRes.slice(startIndex, endIndex)

    return (
        <>
            <Header/>
            <Toaster position="bottom-right" expand visibleToasts={3} closeButton/>
            <main className="flex flex-col min-h-[90vh] overflow-auto w-full py-[6vh] px-[8vw]">
                <section className="flex w-full h-[10%] items-center justify-between mb-[2%]">
                    <div className="flex flex-col">
                        <span className="text-3xl text-white font-bold">Add Movies to your Watchlist</span>
                        <span className="text-xl text-gray-400">Search movies from tmdb and add them to your watchlist!</span>
                    </div>
                    <GridListViewComponent 
                        listViewAmount={4}
                        gridViewAmount={12}
                        listView={listView} 
                        setListView={setListView} 
                        gridView={gridView} 
                        setGridView={setGridView} 
                        setItemsPerPage={setItemsPerPage}
                    />
                </section>
                <section className="flex w-full min-h-[90vh] space-x-[5%]">
                    <MovieFilterCard
                        apiQuery={apiQuery}
                        setApiQuery={setApiQuery}
                        setSearchQuery={setSearchQuery}
                        genreFilterValue={genreFilterValue}
                        setGenreFilterValue={setGenreFilterValue}
                        languageFilterValue={languageFilterValue}
                        setLanguageFilterValue={setLanguageFilterValue}
                        yearFilterValue={yearFilterValue}
                        setYearFilterValue={setYearFilterValue}
                        isLoading={isLoading}
                        currentPage={currentPage}
                        setCurrentPage={setCurrentPage}
                        totalPage={totalPage}
                    />
                    {listView ? (
                        <div className="w-[70%] h-full flex flex-col">
                            {paginatedMovies.length > 0 ? (
                                <ul className="h-full w-full space-y-[2%]">
                                    {paginatedMovies.map((item: TMDBMovieApiRes) => {
                                        return (
                                            <ListViewMovieCardComponent watchlist={watchlist} item={item} isSearchPage={true}/>
                                        )
                                    })}
                                </ul>
                            ) : isLoading ? (
                                <LoadingMovieSkeleton listView={listView} gridView={gridView}/>
                            ) : error ? (
                                <div className="flex items-center justify-center h-3/4 w-full ">
                                    <div className="text-center">
                                        <span className="text-2xl text-red-400">Error Fetching Movies</span>
                                        <p className="text-gray-500 mt-2">Try again later!</p>
                                    </div>
                                </div>
                            ) : (paginatedMovies.length === 0 && searchQuery !== "") ? (
                                <div className="flex items-center justify-center h-3/4 w-full ">
                                    <div className="text-center">
                                        <span className="text-2xl text-gray-400">No movies found for {apiQuery}</span>
                                        <p className="text-gray-500 mt-2">Try a different search term or different filters</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex items-center justify-center w-full ">
                                    <div className="text-center mt-[20vh]">
                                        <span className="text-2xl text-gray-400">No Search Query</span>
                                        <p className="text-gray-500 mt-2">Try searching for a movie in the searchbar</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="h-full w-[70%]">
                            {paginatedMovies.length > 0 ? (
                                <div className="grid grid-cols-4 gap-4">
                                    {paginatedMovies.map((item: TMDBMovieApiRes) => (
                                        <GridViewMovieCardComponent movie={item} showRating={false} watchlist={watchlist} isSearchPage={true}/>
                                    ))}
                                </div>
                            ) : isLoading ? (
                                <LoadingMovieSkeleton listView={listView} gridView={gridView}/>
                            ) : error ? (
                                <div className="flex items-center justify-center h-3/4 w-full ">
                                    <div className="text-center">
                                        <span className="text-2xl text-red-400">Error Fetching Movies</span>
                                        <p className="text-gray-500 mt-2">Try again later!</p>
                                    </div>
                                </div>
                            ) : (paginatedMovies.length === 0 && searchQuery !== "") ? (
                                <div className="flex items-center justify-center h-3/4 w-full ">
                                    <div className="text-center">
                                        <span className="text-2xl text-gray-400">No movies found for {apiQuery}</span>
                                        <p className="text-gray-500 mt-2">Try a different search term or different filters</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex items-center justify-center h-3/4 w-full ">
                                    <div className="text-center">
                                        <span className="text-2xl text-gray-400">No Search Query</span>
                                        <p className="text-gray-500 mt-2">Try searching for a movie in the searchbar</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </section>
            </main>
        </>
    )
}

export default SearchMoviesPage