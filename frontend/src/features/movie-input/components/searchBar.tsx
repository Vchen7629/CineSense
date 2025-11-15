import type { DummyItem } from "../types/data"
import { HandleSearch } from "../utils/handleSearch"

interface SearchProps {
    data: DummyItem[]
    setData: React.Dispatch<React.SetStateAction<DummyItem[]>>
    listView: boolean
    gridView: boolean
}

const SearchBar = ({ data, setData, listView, gridView}: SearchProps) => {

    return (
        <input 
            onChange={(e) => HandleSearch(e.target.value, data, setData)}
            className={
                `h-[100%] w-full bg-[#879B9E] border-2 text-xl text-white border-[#3A5A7A] focus:outline-none px-[1%] rounded-2xl
                ${listView && "px-[5%]"} ${gridView && "px-[1%]"}
            `}
            placeholder="enter a movie name... "
        />
    )
}

export default SearchBar