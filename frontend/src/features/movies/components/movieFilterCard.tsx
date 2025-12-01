import { Loader } from "lucide-react"
import SearchBar from "./searchBar"
import { SearchFilter } from "./searchFilter"
import { genres, languages } from "../misc/filterItems"
import YearFilterComponent from "./yearFilter"
import PaginationComponent from "./pagination"

const MovieFilterCard = ({
    apiQuery,
    setApiQuery,
    setSearchQuery,
    genreFilterValue,
    setGenreFilterValue,
    languageFilterValue,
    setLanguageFilterValue,
    yearFilterValue,
    setYearFilterValue,
    isLoading,
    currentPage,
    setCurrentPage,
    totalPage
}: any) => {

    function handleSearch() {
        setSearchQuery(apiQuery)
        setCurrentPage(1)
        setGenreFilterValue("")
        setLanguageFilterValue("")
        setYearFilterValue("")
    }

    return (
        <div className="h-fit max-h-[80vh] w-[30%] bg-[#394B51] shadow-md shadow-black rounded-xl px-[1%] py-[1.5%]">
            <section className="flex items-center space-x-2 w-full mb-8">
                <SearchBar query={apiQuery} setQuery={setApiQuery}/>
                <button
                    onClick={handleSearch}
                    disabled={isLoading}
                    className={
                        `bg-teal-600 h-[2.5rem] hover:bg-teal-700 border-teal-400 text-white shadow-inner transition-colors duration-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed
                        ${isLoading ? "w-[15%] flex items-center justify-center" : "w-[20%]"}`}
                >
                    {isLoading ? (
                        <Loader className="animate-spin"/>
                    ) : "Search"}
                </button>
            </section>
            <section className="flex items-center justify-between px-4 mb-7">
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
            <section className="flex items-center justify-between px-4 mb-7">
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
            <section className="flex items-center justify-between px-4 mb-10">
                <div className="flex flex-col">
                    <span className="text-md text-white font-semibold">Filter By Year:</span>
                    <span className="text-sm text-gray-300">between 1888 - current</span>
                </div>
                <YearFilterComponent
                    yearFilterValue={yearFilterValue}
                    setYearFilterValue={setYearFilterValue}
                />
            </section>
            <PaginationComponent
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
                totalPage={totalPage}
            />
        </div>
    )
}

export default MovieFilterCard