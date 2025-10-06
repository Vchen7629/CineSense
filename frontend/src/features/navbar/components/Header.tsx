import { Switch } from "@/features/navbar/components/darkLightModeSwitch"

const Header = () => {
    
    return (
        <header className="flex justify-between w-screen h-[10vh] bg-[#879B9E] px-[2.5%]">
            <div className="flex h-full items-center space-x-[2vw] w-fit"> 
                <h2 className="text-3xl font-bold text-white">CineSense</h2>
                <a href="/" className="text-xl text-white font-medium hover:text-gray-500">Home</a>
                <a href="/add-movies" className="text-xl text-white font-medium hover:text-gray-500">Add Movies</a>
                <a href="/recommendations" className="text-xl text-white font-medium hover:text-gray-500">Recommendations</a>
            </div>
            <div className="flex h-full items-center space-x-[2vw] w-fit"> 
                <div className="flex items-center space-x-2">
                    <Switch id="airplane-mode"/>
                </div>
                <div className="flex space-x-[1rem] items-center"> 
                    <div className="bg-[#D9D9D9] h-[2.5rem] w-[2.5rem] rounded-full"/>
                    <a href="/profile" className="text-xl text-white font-medium hover:text-gray-500">
                        User Name
                    </a>
                </div>
            </div>
        </header>
    )
}

export default Header   