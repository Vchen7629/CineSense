import Header from "@/features/navbar/components/Header";
import SearchBar from "../components/searchBar";
import { useState } from "react";
import { dummyData } from "../misc/dummyData";
import type { DummyItem } from "../types/data";
import PaginationComponent from "../components/pagination";
import GridListViewComponent from "../components/gridListViewComponent";
import DisplayMovies from "../components/moviesDisplay";

export default function MovieInputPage() {
    const [currentPage, setCurrentPage] = useState<number>(1)
    const [data] = useState<DummyItem[]>(dummyData)
    const [filteredData, setFilteredData] = useState<DummyItem[]>(dummyData)
    const [gridView, setGridView] = useState<boolean>(false)
    const [listView, setListView] = useState<boolean>(true)

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
                        <div className="h-[60%] w-[30%] shadow-lg shadow-gray-900 rounded-xl p-[1%] border border-[#879B9E]">
                            <section className="w-full h-[13%] mb-[5%]">
                                <SearchBar data={data} setData={setFilteredData} listView={listView} gridView={gridView}/>
                            </section>
                            <section className="flex flex px-2">
                                <span className="text-lg text-gray-300">Genre Filter</span>
                            </section>
                        </div>
                        <div className="w-[65%] flex flex-col">
                            <DisplayMovies movieData={paginatedMovies} listView={listView} gridView={gridView}/>
                            <PaginationComponent
                                currentPage={currentPage}
                                setCurrentPage={setCurrentPage}
                                totalPage={totalPage}
                                listView={listView}
                                gridView={gridView}
                            />
                        </div>
                    </section>
                ) : gridView && (
                    <>
                        <section className="w-full h-[10%] mb-[1%]">
                            <SearchBar data={data} setData={setFilteredData} listView={listView} gridView={gridView}/>
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
                    </>
                )}
            </main>
        </>
    )
}