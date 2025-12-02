
import Header from "@/features/navbar/components/Header"
import { Skeleton } from "@/shared/components/shadcn/skeleton"
import { BookMarked, ChevronRight, Dot } from "lucide-react"
import { useAuth } from "@/shared/hooks/useAuth"
import GridViewMovieCardComponent from "../components/gridViewMovieCardComponent"
import { useGetWatchlistMovies } from "../hooks/useGetWatchlistMovies"
import { useMemo, useState } from "react"
import { Toaster } from "sonner"
import GridListViewComponent from "../components/gridListViewComponent"
import SearchBar from "../components/searchBar"
import { SearchFilter } from "../components/searchFilter"
import { genres, languages } from "../misc/filterItems"
import { filterMovies } from "../utils/filterMovieResults"
import YearFilterComponent from "../components/yearFilter"
import ListViewMovieCardComponent from "../components/listViewMovieCardComponent"
import { Link } from "react-router"
import PaginationComponent from "../components/pagination"

const ViewWatchlistPage = () => {
    const { user } = useAuth()
    const [currentPage, setCurrentPage] = useState<number>(1)
    const { data: watchlist = [], isLoading, isError, } = useGetWatchlistMovies(user.user_id)
    const [itemsPerPage, setItemsPerPage] = useState<number>(15)
    const [listView, setListView] = useState<boolean>(false)
    const [gridView, setGridView] = useState<boolean>(true)
    const [query, setQuery] = useState<string>("")
    const [genreFilterValue, setGenreFilterValue] = useState<string>("")
    const [languageFilterValue, setLanguageFilterValue] = useState<string>("")
    const [yearFilterValue, setYearFilterValue] = useState<string>("")
    
    // filtering logic
    const filteredApiRes = useMemo(() => {
        let filtered = filterMovies(watchlist, {
            genre: genreFilterValue,
            language: languageFilterValue,
            year: yearFilterValue
        });

        // Filter by search query if present
        if (query.trim()) {
            filtered = filtered.filter((movie: any) =>
                movie.title?.toLowerCase().includes(query.toLowerCase())
            );
        }

        return filtered;
    }, [watchlist, genreFilterValue, languageFilterValue, yearFilterValue, query]);

    const totalPage = Math.ceil(filteredApiRes.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    const paginatedMovies = filteredApiRes.slice(startIndex, endIndex)


    return (
        <>
            <Header/>
            <Toaster position="bottom-right" expand visibleToasts={3} closeButton/>
            <main className="flex min-h-[90vh] space-x-[5%] p-[5%] w-full">
                <section className="flex flex-col relative w-[20vw] h-[30vh] pl-[20px] py-[1%] space-y-4 shadow-md shadow-black bg-[#394B51] rounded-xl"> 
                    <div className="flex flex-col">
                        <span className="text-gray-200 text-xl font-bold">My Movies</span>
                        <span className="text-gray-400 text-sm">View your movie watchlist and not seen movies</span>
                    </div>
                    <div className="w-[90%] h-[0.1rem] bg-gray-500"/>
                    <Link to="/watchlist" className="flex relative w-[90%] py-1 items-center space-x-2 hover:bg-[#475b63] rounded-lg transition-colors duration-250">
                        <BookMarked size={24} className="text-teal-400"/>
                        <span className="text-teal-400 font-bold text-lg">Watchlist</span>
                        <ChevronRight className="absolute right-0 text-teal-400"/>
                    </Link>
                    <div className="absolute w-[90%] items-center bottom-4">
                        <PaginationComponent
                            currentPage={currentPage}
                            setCurrentPage={setCurrentPage}
                            totalPage={totalPage}
                        />
                    </div>
                </section>
                <div className="h-full w-[70vw]">
                    <section className="flex w-full items-center space-x-2 justify-between pb-[3vh]">
                        <div className="flex items-center space-x-2 w-[30%]">
                            <SearchBar query={query} setQuery={setQuery}/>
                            
                        </div>
                        <div className="flex items-center space-x-[1vw] w-fit">
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
                            <section className="flex items-center space-x-4">
                                <span className="text-md text-white font-semibold mb-1">Year:</span>
                                <YearFilterComponent
                                    yearFilterValue={yearFilterValue}
                                    setYearFilterValue={setYearFilterValue}
                                />
                            </section>
                            <GridListViewComponent
                                setCurrentPage={setCurrentPage}
                                listViewAmount={5}
                                gridViewAmount={15} 
                                listView={listView} 
                                setListView={setListView} 
                                gridView={gridView} 
                                setGridView={setGridView} 
                                setItemsPerPage={setItemsPerPage}
                            />
                        </div>
                    </section>
                    {isError ? (
                        <div className="flex flex-col space-y-1 w-full h-[50vh] bg-[#394B51] rounded-lg items-center justify-center">
                            <span className="text-2xl">Error Fetching Movies...</span>
                            <span className="text-lg text-gray-400">Something went wrong when loading your movies</span>
                        </div>
                    ) : (paginatedMovies.length === 0 && query !== "") ? (
                            <div className="flex items-center justify-center h-[50vh] items-center w-full ">
                                <div className="text-center">
                                    <span className="text-2xl text-gray-400">No movies in watchlist matching {query}</span>
                                    <p className="text-gray-500 mt-2">Try a different search term or different filters</p>
                                </div>
                            </div>
                    ) : listView && paginatedMovies.length > 0 ? (
                        <ul className="h-full w-full space-y-[2%]">
                            {paginatedMovies.map((item: any) => (
                                <ListViewMovieCardComponent watchlist={watchlist} item={item} isSearchPage={false} showRating={true}/>
                            ))}
                        </ul>
                    ) : gridView && paginatedMovies.length > 0 ? (
                        <section className="grid grid-cols-5 gap-4">
                            {paginatedMovies.map((movie: any) => (
                                <GridViewMovieCardComponent movie={movie} showRating={true} watchlist={watchlist} isSearchPage={false}/>     
                            ))}
                        </section>
                    ) : gridView && isLoading && (
                        <section className="grid grid-cols-6 gap-4">
                            {Array.from({ length: 12 }).map((_, idx) => (
                                <article
                                    key={idx}
                                    className="flex flex-col space-y-2 w-full items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl
                                        h-[30vh] pt-[1.5vh]"
                                >
                                    <Skeleton className="w-[95%] h-[65%]"/>
                                    <Skeleton className="w-[95%] h-6 left-0"/>
                                    <div className="flex w-[95%] items-center">
                                        <Skeleton className="rounded-full h-5 w-14" />
                                        <Dot/>
                                        <Skeleton className="rounded-full h-5 w-8" />
                                    </div>
                                    <div className="flex w-[95%] items-center space-x-2">
                                        <Skeleton className="rounded-full h-5 w-18" />
                                        <Skeleton className="rounded-full h-5 w-20" />
                                        <Skeleton className="rounded-full h-5 w-14" />
                                    </div>
                                </article>
                            ))}
                        </section>
                    )}
                </div>
            </main>
        </>
    )
}

export default ViewWatchlistPage