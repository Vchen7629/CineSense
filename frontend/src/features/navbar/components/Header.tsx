import { Switch } from "@/features/navbar/components/darkLightModeSwitch"
import { Link } from "react-router"
import { useAuthState } from "@/api/user-store"

const Header = () => {
    const { loggedIn } = useAuthState()

    return (
        <header className="flex justify-between w-screen h-[10vh] bg-[#879B9E] px-[2.5%]">
            <div className="flex h-full items-center space-x-[2vw] w-fit"> 
                <h2 className="text-3xl font-bold text-white">CineSense</h2>
                <Link to="/" className="text-xl text-white font-medium hover:text-gray-500">Home</Link>
                <Link to="/add-movies" className="text-xl text-white font-medium hover:text-gray-500">Add Movies</Link>
                <Link to="/recommendations" className="text-xl text-white font-medium hover:text-gray-500">Recommendations</Link>
            </div>
            <div className="flex h-full items-center space-x-[2vw] w-fit"> 
                <div className="flex items-center space-x-2">
                    <Switch id="airplane-mode"/>
                </div>
                <>
                    {loggedIn && ( // Display the User name when user is logged in
                        <div className="flex space-x-[1rem] items-center">
                            <div className="bg-[#D9D9D9] h-[2.5rem] w-[2.5rem] rounded-full"/>
                            <Link to="/profile" className="text-xl text-white font-medium hover:text-gray-500">
                                User Name
                            </Link>
                        </div>
                    )}
                    {!loggedIn && ( // Display the login and signup buttons if user is not logged in
                        <>
                            <Link to="/login" className="text-xl text-white font-medium hover:text-gray-500">Login</Link>
                            <Link to="/signup" className="text-xl text-white font-medium hover:text-gray-500">Sign-up</Link>
                        </>
                    )}
                </>
            </div>
        </header>
    )
}

export default Header   