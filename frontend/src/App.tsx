import { Routes, Route } from 'react-router'
import RecommendationPage from './features/recommendations/pages/RecommendationPage'
import MovieInputPage from './features/movie-input/pages/MoviePage'
import LoginPage from './features/user/pages/LoginPage'
import SignUpPage from './features/user/pages/SignUpPage'
import HomePage from './features/homepage/pages/HomePage'
import ProfilePage from './features/user/pages/UserProfilePage'
import UserPreferences from './features/user/pages/UserPreferences'

function App() {
  return (
    <Routes>
      <Route path='' element={<HomePage/>}/>
      <Route path='recommendations' element={<RecommendationPage/>}/>
      <Route path='add-movies' element={<MovieInputPage/>}/>
      <Route path='login' element={<LoginPage/>}/>
      <Route path='signup' element={<SignUpPage/>}/>
      <Route path='profile' element={<ProfilePage/>}/>
      <Route path='userpreferences' element={<UserPreferences/>}/>
    </Routes>
  )
}

export default App
