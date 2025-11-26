import Header from "@/features/navbar/components/Header";
import SearchBar from "../components/searchBar";
import { useState, useMemo } from "react";
import PaginationComponent from "../components/pagination";
import GridListViewComponent from "../components/gridListViewComponent";
import { SearchFilter } from "../components/searchFilter";
import { genres, languages } from "../misc/filterItems";
import YearFilterComponent from "../components/yearFilter";
import { useSearchMovies } from "../hooks/useSearchMovies";
import { Loader } from "lucide-react";
import type { TMDBMovieApiRes } from "@/app/types/tmdb";
import MovieCard from "../components/movieCard";
import LoadingMovieSkeleton from "../components/loadingMovieSkeleton";
import { getGenreName } from "../utils/genreMap";
import { getLanguageName } from "../utils/languageMap";

export default function MovieInputPage() {
    const [currentPage, setCurrentPage] = useState<number>(1)
    const [apiQuery, setApiQuery] = useState<string>("")
    const [searchQuery, setSearchQuery] = useState<string>("") // Only updates on button click
    const [gridView, setGridView] = useState<boolean>(false)
    const [listView, setListView] = useState<boolean>(true)
    const [itemsPerPage, setItemsPerPage] = useState<number>(4)
    const [genreFilterValue, setGenreFilterValue] = useState<string>("")
    const [languageFilterValue, setLanguageFilterValue] = useState<string>("")
    const [yearFilterValue, setYearFilterValue] = useState<string>("")

    // React Query hook with loading state
    const { data: apiRes = [], isLoading, error } = useSearchMovies({
        query: searchQuery,
        maxPages: 5,
        enabled: searchQuery.length > 0
    })

    // filtering logic
    const filteredApiRes = useMemo(() => {
        if (apiRes.length === 0) {
            return [];
        }

        let filtered = [...apiRes];

        if (genreFilterValue) {
            filtered = filtered.filter((movie) =>
                movie.genre_ids.some((genreId: number) => getGenreName(genreId) === genreFilterValue)
            );
        }

        if (languageFilterValue) {
            filtered = filtered.filter((movie) =>
                getLanguageName(movie.original_language) === languageFilterValue
            );
        }

        if (yearFilterValue) {
            filtered = filtered.filter((movie) => {
                const movieYear = movie.release_date?.split('-')[0];
                return movieYear === yearFilterValue;
            });
        }

        return filtered;
    }, [apiRes, genreFilterValue, languageFilterValue, yearFilterValue]);

    const totalPage = Math.ceil(filteredApiRes.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    const paginatedMovies = filteredApiRes.slice(startIndex, endIndex)

    const handleSearch = () => {
        setSearchQuery(apiQuery)
        setCurrentPage(1)
        setGenreFilterValue("")
        setLanguageFilterValue("")
        setYearFilterValue("")
    }

    return (
        <>
            <Header/>
            <main className="flex flex-col justify-between h-[90vh] overflow-auto w-full py-[6vh] px-[10vw]">
                <section className="flex w-full h-[10%] items-center justify-between mb-[1%]">
                    <div className="flex flex-col">
                        <span className="text-3xl text-white font-bold">Add Movies to your Watchlist</span>
                        <span className="text-xl text-gray-400">Search movies from tmdb and add them to your watchlist!</span>
                    </div>
                    <GridListViewComponent listView={listView} setListView={setListView} gridView={gridView} setGridView={setGridView} setItemsPerPage={setItemsPerPage}/>
                </section>
                {listView ? (
                    <section className="flex w-full h-full space-x-[5%]">
                        <div className="h-[60%] w-[30%] bg-[#394B51] shadow-md shadow-black rounded-xl px-[1%] py-[1.5%]">
                            <div className="h-[95%]">
                                <section className="flex items-center space-x-2 w-full h-[13%] mb-[7.5%]">
                                    <SearchBar query={apiQuery} setQuery={setApiQuery} listView={listView} gridView={gridView}/>
                                    <button
                                        onClick={handleSearch}
                                        disabled={isLoading}
                                        className={
                                            `bg-teal-600 hover:bg-teal-700 border-teal-400 text-white shadow-inner transition-colors duration-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed
                                            ${isLoading ? "h-[90%] w-[15%] flex items-center justify-center" : "h-[90%] w-[20%]"}`}
                                    >
                                        {isLoading ? (
                                            <Loader className="animate-spin"/>
                                        ) : "Search"}
                                    </button>
                                </section>
                                <section className="flex items-center justify-between px-4 mb-[5%]">
                                    <div className="flex flex-col">
                                        <span className="text-md text-white font-semibold">Filter By Genres:</span>
                                        <span className="text-xs text-gray-300">choose a genre to filter results</span>
                                    </div>
                                    <SearchFilter
                                        list={genres}
                                        filterValue={genreFilterValue}
                                        setCurrentPage={setCurrentPage}
                                        setFilterValue={setGenreFilterValue}
                                        placeholder_text="genres"
                                    />
                                </section>
                                <section className="flex items-center justify-between px-4 mb-[5%]">
                                    <div className="flex flex-col">
                                        <span className="text-md text-white font-semibold">Filter By Languages:</span>
                                        <span className="text-xs text-gray-300">choose a language to filter results</span>
                                    </div>
                                    <SearchFilter
                                        list={languages}
                                        filterValue={languageFilterValue}
                                        setCurrentPage={setCurrentPage}
                                        setFilterValue={setLanguageFilterValue}
                                        placeholder_text="language"
                                    />
                                </section>
                                <section className="flex items-center justify-between px-4">
                                    <div className="flex flex-col">
                                        <span className="text-md text-white font-semibold">Filter By Year:</span>
                                        <span className="text-sm text-gray-300">between 1888 - current</span>
                                    </div>
                                    <YearFilterComponent
                                        yearFilterValue={yearFilterValue}
                                        setYearFilterValue={setYearFilterValue}
                                    />
                                </section>
                            </div>
                            <PaginationComponent
                                currentPage={currentPage}
                                setCurrentPage={setCurrentPage}
                                totalPage={totalPage}
                                listView={listView}
                                gridView={gridView}
                            />
                        </div>
                        <div className="w-[65%] flex flex-col">
                            {paginatedMovies.length > 0 ? (
                                <ul className={`h-full w-full space-y-[2%] ${gridView && "grid grid-cols-2 gap-4"}`}>
                                {paginatedMovies.map((item: TMDBMovieApiRes) => {
                                    return (
                                        <MovieCard item={item} listView={listView} gridView={gridView}/>
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
                                <div className="flex items-center justify-center h-3/4 w-full ">
                                    <div className="text-center">
                                        <span className="text-2xl text-gray-400">No Search Query</span>
                                        <p className="text-gray-500 mt-2">Try searching for a movie in the searchbar</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </section>
                ) : gridView && (
                    <section className="flex flex-col h-full space-y-[1%]">
                        <section className="flex items-center space-x-2 w-full h-[10%] ">
                            <SearchBar query={apiQuery} setQuery={setApiQuery}listView={listView} gridView={gridView}/>
                            <button
                                onClick={handleSearch}
                                disabled={isLoading}
                                className={
                                    `bg-teal-600 hover:bg-teal-700 border-teal-400 text-white shadow-inner transition-colors duration-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed
                                    ${gridView && "h-[80%] w-[10%]"}
                                    ${isLoading && "h-[90%] w-[15%] flex items-center justify-center"}
                                `}
                            >
                                {isLoading ? (
                                    <Loader className="animate-spin"/>
                                ) : "Search"}
                            </button>
                        </section>
                        <section className="flex items-center px-2 space-x-[1%]">
                            <span className="text-xl mr-[2%] text-white font-light">Filters:</span>
                            <SearchFilter
                                list={genres}
                                filterValue={genreFilterValue}
                                setCurrentPage={setCurrentPage}
                                setFilterValue={setGenreFilterValue}
                                placeholder_text="genres"
                            />
                            <SearchFilter
                                list={languages}
                                filterValue={languageFilterValue}
                                setCurrentPage={setCurrentPage}
                                setFilterValue={setLanguageFilterValue}
                                placeholder_text="language"
                            />
                            <section className="flex items-center space-x-2">
                                <span className="text-md text-white font-light">Year:</span>
                                <YearFilterComponent
                                    yearFilterValue={yearFilterValue}
                                    setYearFilterValue={setYearFilterValue}
                                />
                            </section>
                        </section>
                        <section className="flex flex-col w-full h-[85vh]">
                            <div className="flex items-center justify-between mb-5 pl-2">
                                <span className="text-xl text-white">Results</span>
                                <PaginationComponent
                                    currentPage={currentPage}
                                    setCurrentPage={setCurrentPage}
                                    totalPage={totalPage}
                                    listView={listView}
                                    gridView={gridView}
                                />
                            </div>
                            {paginatedMovies.length > 0 ? (
                                <ul className={`h-full w-full space-y-[2%] ${gridView && "grid grid-cols-2 gap-4"}`}>
                                {paginatedMovies.map((item: TMDBMovieApiRes) => {
                                    return (
                                        <MovieCard item={item} listView={listView} gridView={gridView}/>
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
                                <div className="flex items-center justify-center h-3/4 w-full ">
                                    <div className="text-center">
                                        <span className="text-2xl text-gray-400">No Search Query</span>
                                        <p className="text-gray-500 mt-2">Try searching for a movie in the searchbar</p>
                                    </div>
                                </div>
                            )}
                        </section>
                    </section>
                )}
            </main>
        </>
    )
}