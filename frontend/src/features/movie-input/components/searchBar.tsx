import type { DummyItem } from "../types/data"
import { HandleSearch } from "../utils/handleSearch"

interface SearchProps {
    data: DummyItem[],
    setData: React.Dispatch<React.SetStateAction<DummyItem[]>>
}

const SearchBar = ({ data, setData}: SearchProps) => {

    return (
        <input 
            onChange={(e) => HandleSearch(e.target.value, data, setData)}
            className="h-[80%] w-1/2 bg-[#879B9E] border-2 text-xl text-white border-[#3A5A7A] focus:outline-none px-[1%] rounded-2xl"
            placeholder="enter a movie name... "
        />
    )
}

export default SearchBar