import Header from "@/features/navbar/components/Header";
import SearchBar from "../components/searchBar";
import { useState } from "react";
import { dummyData } from "../misc/dummyData";
import type { DummyItem } from "../types/data";
import PaginationComponent from "../components/pagination";
import GridListViewComponent from "../components/gridListViewComponent";
import DisplayMovies from "../components/moviesDisplay";
import { SearchFilter } from "../components/searchFilter";
import { genres, languages } from "../misc/filterItems";
import YearFilterComponent from "../components/yearFilter";

export default function MovieInputPage() {
    const [currentPage, setCurrentPage] = useState<number>(1)
    const [data] = useState<DummyItem[]>(dummyData)
    const [filteredData, setFilteredData] = useState<DummyItem[]>(dummyData)
    const [gridView, setGridView] = useState<boolean>(false)
    const [listView, setListView] = useState<boolean>(true)
    const [apiRes] = useState<any>()

    const itemsPerPage = 4
    const totalPage = Math.ceil(filteredData.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    const paginatedMovies = filteredData.slice(startIndex, endIndex)

    return (
        <>
            <Header/>     
            <main className="flex flex-col justify-between h-[90vh] w-full py-[6vh] px-[10vw]">
                <section className="flex w-full h-[10%] items-center justify-between mb-[1%]">
                    <div className="flex flex-col">
                        <span className="text-3xl text-white font-bold">Add Movies to your Watchlist</span>
                        <span className="text-xl text-gray-400">Search movies from tmdb and add them to your watchlist!</span>
                    </div>
                    <GridListViewComponent listView={listView} setListView={setListView} gridView={gridView} setGridView={setGridView}/>
                </section>
                {listView ? (
                    <section className="flex w-full h-full space-x-[5%]">
                        <div className="h-[60%] w-[30%] bg-[#394B51] shadow-md shadow-black rounded-xl px-[1%] py-[1.5%]">
                            <div className="h-[95%]">
                                <section className="w-full h-[13%] mb-[7.5%]">
                                    <SearchBar apiRes={apiRes} setApiRes={setFilteredData} listView={listView} gridView={gridView}/>
                                </section>
                                <section className="flex items-center justify-between px-4 mb-[5%]">
                                    <div className="flex flex-col">
                                        <span className="text-md text-white font-semibold">Filter By Genres:</span>
                                        <span className="text-xs text-gray-300">choose a genre to filter results</span>
                                    </div>
                                    <SearchFilter list={genres} placeholder_text="genres"/>
                                </section>
                                <section className="flex items-center justify-between px-4 mb-[5%]">
                                    <div className="flex flex-col">
                                        <span className="text-md text-white font-semibold">Filter By Languages:</span>
                                        <span className="text-xs text-gray-300">choose a language to filter results</span>
                                    </div>
                                    <SearchFilter list={languages} placeholder_text="language"/>
                                </section>
                                <section className="flex items-center justify-between px-4">
                                    <div className="flex flex-col">
                                        <span className="text-md text-white font-semibold">Filter By Year:</span>
                                        <span className="text-sm text-gray-300">between 1888 - current</span>
                                    </div>
                                    <YearFilterComponent/>
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
                            <DisplayMovies movieData={paginatedMovies} listView={listView} gridView={gridView}/>
                        </div>
                    </section>
                ) : gridView && (
                    <section className="flex flex-col h-full space-y-[1%]">
                        <section className="flex items-center w-full h-[10%] ">
                            <SearchBar apiRes={apiRes} setApiRes={setFilteredData} listView={listView} gridView={gridView}/>
                        </section>
                        <section className="flex items-center px-2 space-x-[1%]">
                            <span className="text-xl mr-[2%] text-white font-light">Filters:</span>
                            <SearchFilter list={genres} placeholder_text="genres"/>
                            <SearchFilter list={languages} placeholder_text="language"/>
                            <section className="flex items-center space-x-2">
                                <span className="text-md text-white font-light">Year:</span>
                                <YearFilterComponent/>
                            </section>
                        </section>
                        <section className="flex flex-col w-full h-[85%]">
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
                            <DisplayMovies movieData={paginatedMovies} listView={listView} gridView={gridView}/>
                        </section>
                    </section>
                )}
            </main>
        </>
    )
}