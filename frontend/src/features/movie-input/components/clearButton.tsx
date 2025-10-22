import type { DummyItem } from "../types/data"
import { HandleClear } from "../utils/handleClear"

interface ClearProps {
    setFilteredData: React.Dispatch<React.SetStateAction<DummyItem[]>>
}

const ClearButton = ({ setFilteredData }: ClearProps) => {

    return (
        <button 
            className="h-[65%] w-[45%] bg-[#879B9E] hover:bg-[#A0B1B4] transition-colors duration-200 rounded-xl border-3 border-[#3A5A7A]" 
            onClick={() => HandleClear(setFilteredData)}
        >
            clear
        </button>
    )
}

export default ClearButton