interface SearchProps {
    query: string
    setQuery: React.Dispatch<React.SetStateAction<string>>
    listView: boolean
    gridView: boolean
}

const SearchBar = ({ query, setQuery, listView, gridView}: SearchProps) => {

    return (
        <input 
            onChange={(e) => setQuery(e.target.value)}
            className={
                `bg-[#879B9E] border-2 text-xl text-white border-[#3A5A7A] focus:outline-none px-[1%] rounded-2xl
                ${listView && "px-[5%] h-[100%] w-full"} ${gridView && "px-[1%] h-[90%] w-full"}
            `}
            value={query}
            placeholder="enter a movie name... "
        />
    )
}

export default SearchBar