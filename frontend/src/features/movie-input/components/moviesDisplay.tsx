import type { DummyItem } from "../types/data"
import { ThumbsUpIcon, PlusIcon, TrashIcon, Heart } from "lucide-react"
import RateMovieButtons from "./rateButtons"
import { useState } from "react"
import { useRateMovie } from "../hooks/useRateMovie"

interface DisplayProps {
    movieData: DummyItem[],
    listView: boolean,
    gridView: boolean
}

const DisplayMovies = ({movieData, listView, gridView}: DisplayProps) => {
    const [openWatched, setOpenWatched] = useState<{ [key: string]: boolean }>({});
    const [ratings, setRatings] = useState<{ [key: string]: number }>({});
    const rateMovie = useRateMovie();

    const handleAdd = (id: string | number) => {
        setOpenWatched(prev => ({ ...prev, [id]: true }));
    };

    const handleRemove = (id: string | number) => {
        setOpenWatched(prev => ({ ...prev, [id]: false }));
    };

    const handleSetRating = (id: string | number, value: number) => {
        setRatings(prev => ({ ...prev, [id]: value }));
    };

    return (
        <ul className={`h-[95%] w-full space-y-[2%] ${gridView && "grid grid-cols-2 gap-4"}`}>
            {movieData.map((item: DummyItem) => {
                const isOpen = !!openWatched[item.id];
                const itemRating = ratings[item.id] || 0;

                return (
                    <li 
                        key={item.id} 
                        className={
                            `flex w-full text-xl font-semibold items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl 
                            ${listView && "h-[20%]"} ${gridView && "h-[85%]"}`
                        } 
                        role="listitem"
                    >   
                        <img className={`bg-white ${listView && "w-[10%]"} ${gridView && "w-[20%]"} h-[85%]`}/>
                        <section 
                            className={`flex flex-col ${listView && "w-[70%]"} ${gridView && "w-[50%]"} h-[80%] px-[2%]`}
                        >
                            <span className="text-lg font-bold text-white">{item.name}</span>
                            <span className="text-sm text-gray-400 h-3/4">{item.desc}</span>
                            <div className="flex items-center space-x-3 mt-4 w-[100%]">
                                {!isOpen ? (
                                    <button
                                        onClick={() => handleAdd(item.id)}
                                        className="flex items-center space-x-1 px-3 py-1.5 bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner hover:bg-teal-800 rounded-xl transition-colors duration-250"
                                    >
                                        <PlusIcon size={18} />
                                        <span className="text-sm">Add</span>
                                    </button>
                                ) : (
                                    <button
                                        onClick={() => handleAdd(item.id)}
                                        className="flex items-center space-x-1 px-3 py-1.5 bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner hover:bg-teal-800 rounded-xl transition-colors duration-250"
                                    >
                                        <Heart size={18} />
                                        <span className="text-sm">Added!</span>
                                    </button>
                                )}
                                {isOpen && (
                                    <div className="w-[80%] flex">
                                        <button 
                                            onClick={() => handleRemove(item.id)}
                                            className="flex items-center space-x-1 px-3 py-1 bg-slate-500/40 hover:bg-red-600 rounded-xl transition-colors duration-250"
                                        >
                                            <TrashIcon size={18}/>
                                            <span className="text-sm">Remove</span>
                                        </button>
                                        <RateMovieButtons 
                                            rating={itemRating} 
                                            setRating={(value) => handleSetRating(item.id, value)}
                                        />
                                        <button 
                                            onClick={() => rateMovie(item, itemRating)}
                                            className="flex items-center space-x-1 px-3 py-1 bg-green-400/20 shadow-inner hover:bg-green-800 rounded-xl transition-colors duration-250"
                                        >
                                            <ThumbsUpIcon size={18}/>
                                            <span className="text-sm">Rate!</span>
                                        </button>
                                    </div>
                                )}
                            </div>
                        </section>
                        <section 
                            className={`flex flex-col items-center h-[80%] ${listView && "w-[25%] space-y-2"} ${gridView && "w-[35%] space-y-4"}`}
                        >   
                            <div className="flex space-x-2 ">
                            {item.genres.map((g, idx) => (
                                <div 
                                    key={idx} 
                                    className="px-1 py-1 text-xs bg-teal-500/20 border border-teal-400 text-teal-200 shadow-inner rounded-md"
                                >
                                    {g}
                                </div>
                            ))}
                            </div>
                            <div className="flex space-x-2 text-white items-center">
                                <span className="text-sm">Cast: </span>
                                {item.actors.map((name, idx) => (
                                    <div 
                                        key={idx} 
                                        className="text-sm text-teal-500"
                                    >
                                        {name}
                                    </div>
                                ))}
                            </div>
                            <div className="flex space-x-2 text-white items-center">
                                <span className="text-sm">Director: </span>
                                {item.director.map((name, idx) => (
                                    <div 
                                        key={idx} 
                                        className="text-sm text-teal-500"
                                    >
                                        {name}
                                    </div>
                                ))}
                            </div>
                        </section>
                    </li>
                )
            })}
        </ul>
    )
}

export default DisplayMovies