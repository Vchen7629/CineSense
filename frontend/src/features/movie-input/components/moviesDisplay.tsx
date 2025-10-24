import type { DummyItem } from "../types/data"
import { handleDeleteMovie } from "../utils/handleDeleteMovie"
import { LikeDislikeSwitch } from "./likeDislikeSwitch"
import { ThumbsUpIcon, ThumbsDownIcon, Trash2Icon } from "lucide-react"

interface DisplayProps {
    movieData: DummyItem[],
    setMovieData: React.Dispatch<React.SetStateAction<DummyItem[]>>
    setFilteredMovieData: React.Dispatch<React.SetStateAction<DummyItem[]>>
}

const DisplayAddedMovie = ({movieData, setMovieData, setFilteredMovieData}: DisplayProps) => {
    return (
        <ul className="h-[95%] w-full space-y-[1%]">
            {movieData.map((item: DummyItem) => (
                <li 
                    key={item.id} 
                    className="flex w-full text-xl font-semibold items-center h-[10%] shadow-[0_4px_12px_rgba(20,40,45,0.5)] bg-[#879B9E] rounded-xl border-2 border-[#3A5A7A]" 
                    role="listitem"
                >
                    <section 
                        className={`flex w-[10%] justify-center items-center ${item.like ? 'text-yellow-300' : 'text-white'}`}
                    >
                        {item.name}
                    </section>
                    <section 
                        className={`flex w-[50%] justify-center items-center ${item.like ? 'text-yellow-300' : 'text-white'}`}
                    >
                        {item.desc}
                    </section>
                    <section 
                        className={`flex w-[25%] justify-center items-center ${item.like ? 'text-yellow-300' : 'text-white'}`}
                    >
                        {item.genres}
                    </section>
                    <section className="flex items-center space-x-2 w-[8%] ">
                        <ThumbsUpIcon/>
                        <LikeDislikeSwitch />
                        <ThumbsDownIcon/>
                    </section>
                    <section className="flex w-[5%] justify-end">
                        <Trash2Icon onClick={() => handleDeleteMovie(movieData, setMovieData, setFilteredMovieData, item.id)}/>
                    </section>
                </li>
            ))}
        </ul>
    )
}

export default DisplayAddedMovie