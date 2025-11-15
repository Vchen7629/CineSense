import type { DummyItem } from "../types/data"
import { ThumbsUpIcon, PlusIcon, TrashIcon } from "lucide-react"
import RateMovieButtons from "./rateButtons"
import { useWatched } from "@/global_state/user"

interface DisplayProps {
    movieData: DummyItem[],
    listView: boolean,
    gridView: boolean
}

const DisplayMovies = ({movieData, listView, gridView}: DisplayProps) => {
    const watched = useWatched((state: any) => state.watched)
    const setWatched = useWatched((state: any) => state.addWatchlist)
    const removeWatched = useWatched((state: any) => state.removeWatchlist)

    return (
        <ul className={`h-[95%] w-full space-y-[2%] ${gridView && "grid grid-cols-2 gap-4"}`}>
            {movieData.map((item: DummyItem) => (
                <li 
                    key={item.id} 
                    className={
                        `flex w-full text-xl font-semibold items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl border-2 border-[#3A5A7A]
                        ${listView && "h-[20%]"} ${gridView && "h-[85%]"}`
                    } 
                    role="listitem"
                >   
                    <img className={`bg-white ${listView && "w-[10%]"} ${gridView && "w-[20%]"} h-[85%]`}/>
                    <section 
                        className={`flex flex-col w-[70%] h-[80%] px-[2%] ${item.like ? 'text-yellow-300' : 'text-white'}`}
                    >
                        <span className="text-lg font-bold">{item.name}</span>
                        <span className="text-sm text-gray-400 h-3/4">{item.desc}</span>
                        <div className="flex items-center space-x-3 mt-4">
                            <button 
                                onClick={setWatched}
                                className="flex items-center space-x-1 px-3 py-1 bg-teal-600 hover:bg-teal-400 rounded-xl transition-colors duration-250"
                            >
                                <PlusIcon size={18}/>
                                <span className="text-sm">Add</span>
                            </button>
                            {watched && (
                                <>
                                    <button 
                                        onClick={removeWatched}
                                        className="flex items-center space-x-1 px-3 py-1 bg-gray-500 hover:bg-red-500 rounded-xl transition-colors duration-250"
                                    >
                                        <TrashIcon size={18}/>
                                        <span className="text-sm">Remove</span>
                                    </button>
                                    <RateMovieButtons/>
                                    <button className="flex items-center space-x-1 px-3 py-1 bg-green-600 hover:bg-green-400 rounded-xl transition-colors duration-250">
                                        <ThumbsUpIcon size={18}/>
                                        <span className="text-sm">Rate!</span>
                                    </button>
                                </>
                            )}
                        </div>
                    </section>
                    <section 
                        className={`flex flex-col items-center h-[80%] ${listView && "w-[20%]"} ${gridView && "w-[30%]"}`}
                    >   
                        <div className="flex space-x-2 ">
                        {item.genres.map((g, idx) => (
                            <div 
                                key={idx} 
                                className="px-1 py-1 text-xs bg-[#879B9E] rounded-md"
                            >
                                {g}
                            </div>
                        ))}
                        </div>
                    </section>
                </li>
            ))}
        </ul>
    )
}

export default DisplayMovies