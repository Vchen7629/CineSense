import { Switch } from "@/features/navbar/components/darkLightModeSwitch"
import { Link, useLocation } from "react-router"
import { useAuth } from "../../../shared/hooks/useAuth"
import { useLogout } from "../hooks/useLogout"
import { LogOut } from "lucide-react"

const Header = () => {
    // location so we only call authenticate on routes where
    // users are definitely not logged 
    const location = useLocation()
    const unauthenticatedRoutes = ['/login', '/signup', '/userpreferences']
    const shouldSkipAuth = unauthenticatedRoutes.includes(location.pathname)

    const { isAuthenticated, user } = useAuth({ enabled: !shouldSkipAuth})
    const logout = useLogout()
    
    async function handleLogout() {
        try {
            await logout()
        } catch (error: any) {
            console.log(error)
            return
        }
    }

    return (
        <header className="flex justify-between w-screen h-[10vh] bg-[#394B51] shadow-lg px-[2.5%]">
            <div className="flex h-full items-center space-x-[2vw] w-fit"> 
                <Link to="/" className="text-3xl font-bold text-white hover:text-teal-400 transition-colors duration-250">CineSense</Link>
                {isAuthenticated && (
                    <>
                        <Link to="/search" className="text-xl text-white font-medium hover:text-teal-500 transition-colors duration-250">Search</Link>
                        <Link to="/recommendations" className="text-xl text-white font-medium hover:text-teal-500 transition-colors duration-250">Recommendations</Link>
                        <Link to="/watchlist" className="text-xl text-white font-medium hover:text-teal-500 transition-colors duration-250">My Movies</Link>
                    </>
                )}
            </div>
            <div className="flex h-full items-center space-x-[2vw] w-fit"> 
                <div className="flex items-center space-x-2">
                    <Switch id="airplane-mode"/>
                </div>
                <>
                    {isAuthenticated && ( // Display the User name when user is logged in
                        <div className="flex space-x-[1rem] items-center">
                            <div className="bg-[#D9D9D9] h-[2.5rem] w-[2.5rem] rounded-full"/>
                            <Link to="/profile" className="text-xl text-white font-medium hover:text-gray-500">
                                {user.username}
                            </Link>
                            <button 
                                onClick={() => handleLogout()}
                                className="ml-2 flex items-center space-x-2 p-2 hover:text-teal-400 transition-colors duration-250"
                            >
                                <LogOut />
                                <span>Logout</span>
                            </button>
                        </div>
                    )}
                    {!isAuthenticated && ( // Display the login and signup buttons if user is not logged in
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