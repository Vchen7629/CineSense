import type { DummyItem } from "../types/data"
import { callAPI, search } from "../../../app/services/MovieSearchService"
import { useState } from "react"

interface SearchProps {
    data: DummyItem[]
    setData: React.Dispatch<React.SetStateAction<DummyItem[]>>
    listView: boolean
    gridView: boolean
}



const SearchBar = ({listView, gridView}: SearchProps) => {

    // This is whats currently being typed. Don't delete this incase we need it.
    const [searchText, setSearchText] = useState<string>("")


    //searching once the button is pressed
    const handleClick = () => 
    {
    search(searchText)
    }



    return (
        <div>
            <input 
                value={searchText}
                onChange={(e) => {
                    setSearchText(e.target.value);
                }}
                className={
                    `bg-[#879B9E] border-2 text-xl text-white border-[#3A5A7A] focus:outline-none px-[1%] rounded-2xl
                    ${listView && "px-[5%] h-[100%] w-full"} ${gridView && "px-[1%] h-[90%] w-full"}
                `}

                placeholder="enter a movie name... "

                // Works w/ both the Enter key and the Search button.
                onKeyDown= 
                {
                    (e) => {
                        if (e.key === 'Enter') 
                        {
                            search(searchText);
                        }
                    }
                }
            />
            <button onClick={handleClick}>
                Search Button
            </button>
        </div>
    )
}

export default SearchBar
