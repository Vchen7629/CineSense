import type React from "react"

interface gridListViewProps {
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>
    listViewAmount: number
    gridViewAmount: number
    gridView: boolean
    setGridView: (gridView: boolean) => void
    listView: boolean
    setListView: (listView: boolean) => void
    setItemsPerPage: React.Dispatch<React.SetStateAction<number>>
}

// Component to switch between grid and list view
const GridListViewComponent = ({ setCurrentPage, listViewAmount, gridViewAmount, gridView, setGridView, listView, setListView, setItemsPerPage }: gridListViewProps) => {

    return (
        <div className="flex w-[12.5vw] h-[65%] p-1 space-x-2 bg-black rounded-4xl bg-transparent border border-[#879B9E]">
            <button 
                onClick={() => {setCurrentPage(1); setListView(true); setGridView(false); setItemsPerPage(listViewAmount)}}
                className={
                    `h-full w-[49%] rounded-xl text-white font-bold
                    ${listView ? "bg-teal-600 hover:bg-teal-400 transition-colors duration-200 hover:text-gray-600" : "bg-transparent"}`
                }>
                List View
            </button>
            <button 
                onClick={() => {setCurrentPage(1); setListView(false); setGridView(true); setItemsPerPage(gridViewAmount)}}
                className={
                    `h-full w-[49%] rounded-xl text-white font-bold
                    ${gridView ? "bg-teal-600 hover:bg-teal-400 transition-colors duration-200 hover:text-gray-600" : "bg-transparent hover:text-blue-200"} `
                    }>
                Grid View
            </button>
        </div>
    )
}

export default GridListViewComponent