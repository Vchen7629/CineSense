import { Routes, Route } from 'react-router'
import InitPage from './init-page'
import RecommendationPage from './features/recommendations/pages/RecommendationPage'
import MovieInputPage from './features/movie-input/pages/MoviePage'
import LoginPage from './features/user/pages/LoginPage'
import UserProfilePage from './features/user/pages/UserProfilePage'

function App() {
  return (
    <Routes>
      <Route path='' element={<InitPage/>}/>
      <Route path='recommendations' element={<RecommendationPage/>}/>
      <Route path='add-movies' element={<MovieInputPage/>}/>
      <Route path='login' element={<LoginPage/>}/>
      <Route path='profile' element={<UserProfilePage/>}/>
    </Routes>
  )
}

export default App
