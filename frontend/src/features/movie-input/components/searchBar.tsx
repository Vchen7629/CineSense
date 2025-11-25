import type { RateMovieApi } from "@/app/types/movie"
import { HandleSearch } from "../utils/handleSearch"

interface SearchProps {
    data: RateMovieApi[]
    setData: React.Dispatch<React.SetStateAction<RateMovieApi[]>>
    listView: boolean
    gridView: boolean
}

const SearchBar = ({ data, setData, listView, gridView}: SearchProps) => {

    return (
        <input 
            onChange={(e) => HandleSearch(e.target.value, data, setData)}
            className={
                `bg-[#879B9E] border-2 text-xl text-white border-[#3A5A7A] focus:outline-none px-[1%] rounded-2xl
                ${listView && "px-[5%] h-[100%] w-full"} ${gridView && "px-[1%] h-[90%] w-full"}
            `}
            placeholder="enter a movie name... "
        />
    )
}

export default SearchBar