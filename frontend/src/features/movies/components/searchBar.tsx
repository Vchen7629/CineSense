interface SearchProps {
    query: string
    setQuery: React.Dispatch<React.SetStateAction<string>>
}

const SearchBar = ({ query, setQuery }: SearchProps) => {

    return (
        <input 
            type="search"
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 min-h-[2.5rem] bg-[#5C7A85] border-1 text-md text-white border-[#3A5A7A] focus:outline-none px-[1%] rounded-md px-[5%] w-full"
            value={query}
            placeholder="enter a movie name... "
        />
    )
}

export default SearchBar