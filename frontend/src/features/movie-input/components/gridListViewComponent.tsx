
interface gridListViewProps {
    gridView: boolean
    setGridView: (gridView: boolean) => void
    listView: boolean
    setListView: (listView: boolean) => void
}

// Component to switch between grid and list view
const GridListViewComponent = ({ gridView, setGridView, listView, setListView }: gridListViewProps) => {

    return (
        <div className="flex w-[12.5%] h-[65%] p-1 space-x-2 bg-black rounded-lg bg-transparent border border-[#879B9E]">
            <button 
                onClick={() => {setListView(true); setGridView(false)}}
                className={
                    `h-full w-[49%] rounded-md text-white font-bold
                    ${listView ? "bg-[#879B9E] hover:bg-blue-200 transition-colors duration-200 hover:text-gray-600" : "bg-transparent"}`
                }>
                List View
            </button>
            <button 
                onClick={() => {setListView(false); setGridView(true)}}
                className={
                    `h-full w-[49%] rounded-md text-white font-bold
                    ${gridView ? "bg-[#879B9E] hover:bg-blue-200 transition-colors duration-200 hover:text-gray-600" : "bg-transparent hover:text-blue-200"} `
                    }>
                Grid View
            </button>
        </div>
    )
}

export default GridListViewComponent