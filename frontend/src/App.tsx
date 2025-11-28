import { Routes, Route } from 'react-router'
import RecommendationPage from './features/recommendations/pages/RecommendationPage'
import MovieInputPage from './features/movie-input/pages/MoviePage'
import LoginPage from './features/user/pages/LoginPage'
import SignUpPage from './features/user/pages/SignUpPage'
import HomePage from './features/homepage/pages/HomePage'
import ProfilePage from './features/user/pages/UserProfilePage'
import UserPreferences from './features/user/pages/UserPreferences'
import { ProtectedRoute } from './shared/components/app/protectedRoute'

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path='' element={<HomePage/>}/>
      <Route path='login' element={<LoginPage/>}/>
      <Route path='signup' element={<SignUpPage/>}/>

      {/* Protected routes - wrapped once */}
      <Route element={<ProtectedRoute/>}>
        <Route path='recommendations' element={<RecommendationPage/>}/>
        <Route path='add-movies' element={<MovieInputPage/>}/>
        <Route path='profile' element={<ProfilePage/>}/>
        <Route path='userpreferences' element={<UserPreferences/>}/>
      </Route>
    </Routes>
  )
}

export default App
