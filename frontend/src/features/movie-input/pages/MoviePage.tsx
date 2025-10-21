import Header from "@/features/navbar/components/Header";
import SearchBar from "../components/searchBar";
import DisplayAddedMovie from "../components/moviesDisplay";
import { useState } from "react";
import { dummyData } from "../misc/dummyData";
import ClearButton from "../components/clearButton";
import SaveButton from "../components/saveButton";
import type { DummyItem } from "../types/data";

export default function MovieInputPage() {
    const [data, setData] = useState<DummyItem[]>(dummyData)
    const [filteredData, setFilteredData] = useState<DummyItem[]>(dummyData)

    return (
        <>
            <Header/>
            <main className="flex flex-col justify-between h-[90vh] w-full py-[5vh] px-[5vw]">
                <section className="flex w-full h-[10%] justify-between">
                    <SearchBar data={data} setData={setFilteredData}/>
                    <div className="flex items-center h-full w-[12.5%] space-x-6">
                        <ClearButton setFilteredData={setFilteredData}/>
                        <SaveButton/>
                    </div>
                </section>
                <DisplayAddedMovie movieData={filteredData} setMovieData={setData} setFilteredMovieData={setFilteredData}/>
            </main>
        </>
    )
}