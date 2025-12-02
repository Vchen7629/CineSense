import { Routes, Route } from 'react-router'
import LoginPage from './features/user/pages/LoginPage'
import SignUpPage from './features/user/pages/SignUpPage'
import HomePage from './features/homepage/pages/HomePage'
import ProfilePage from './features/user/pages/UserProfilePage'
import UserPreferences from './features/user/pages/UserPreferences'
import { ProtectedRoute } from './shared/components/app/protectedRoute'
import RecommendationPage from './features/movies/pages/MovieRecommendation'
import SearchMoviesPage from './features/movies/pages/SearchMovies'
import ViewWatchlistPage from './features/movies/pages/ViewWatchlist'

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path='' element={<HomePage/>}/>
      <Route path='login' element={<LoginPage/>}/>
      <Route path='signup' element={<SignUpPage/>}/>
      <Route path='userpreferences' element={<UserPreferences/>}/>

      {/* Protected routes - wrapped once */}
      <Route element={<ProtectedRoute/>}>
        <Route path='recommendations' element={<RecommendationPage/>}/>
        <Route path='search' element={<SearchMoviesPage/>}/>
        <Route path='profile' element={<ProfilePage/>}/>
        <Route path='watchlist' element={<ViewWatchlistPage />}/>
      </Route>
    </Routes>
  )
}

export default App
