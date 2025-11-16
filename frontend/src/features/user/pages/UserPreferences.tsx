import Header from "@/features/navbar/components/Header";
import UserPreferencesHeader from "../components/UserPreferencesHeader";
import { useState } from "react";
import UserPreferencesGenresGrid from "../components/UserPreferencesGenres";
import { SignUpConfirmButton } from "../components/SignUpConfirmButton";

export default function UserPreferences() {
  const [selectedGenres, setSelectedGenres] = useState<string[]>([])
  const [canSignup, setCanSignup] = useState<boolean>(false)

  return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      
      <div className="flex flex-col space-y-[2.5vh] items-center mx-auto py-[5vh] h-full"> 
        <section className="flex flex-col space-y-2 text-center mb-12">
          <span className="text-white font-bold text-4xl sm:text-5xl lg:text-4xl">
            Pick Your Favorite Genres
          </span>
          <span className="text-gray-300 text-lg font-light">
            Step 2 of 2: Select At Least 3 To Personalize Your Recommendations
          </span>
        </section>
        <section className="flex flex-col w-[65%] h-[67.5vh] p-[2%] space-y-[2%] rounded-2xl bg-[#394B51] shadow-md shadow-black">
          <UserPreferencesHeader selectedGenres={selectedGenres} setSelectedGenres={setSelectedGenres}/>
          <UserPreferencesGenresGrid selectedGenres={selectedGenres} setSelectedGenres={setSelectedGenres} setCanSignup={setCanSignup}/>
          <div className="flex items-center justify-between w-full h-1/4">
            <span className="text-gray-300">The Selected genres will be used to create your initial recommendations</span>
            <SignUpConfirmButton selectedGenres={selectedGenres} canSignup={canSignup}/>
          </div>
        </section>

        {/*<div className="max-w-2xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5 lg:gap-6">
            <div className="space-y-4 sm:space-y-5 lg:space-y-6">
              <button
                onClick={() => alert("Confirm Comedy Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Comedy
              </button>

              <button
                onClick={() => alert("Confirm Action Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Action
              </button>

              <button
                onClick={() => alert("Confirm Romance Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Romance
              </button>

              <button
                onClick={() => alert("Confirm Thriller Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Thriller
              </button>

              <button
                onClick={() => alert("Confirm Animation Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Animation
              </button>
            </div>

            <div className="space-y-4 sm:space-y-5 lg:space-y-6">
              <button
                onClick={() => alert("Confirm Drama Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Drama
              </button>

              <button
                onClick={() => alert("Confirm Horror Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Horror
              </button>

              <button
                onClick={() => alert("Confirm Sci-Fi Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Sci-Fi
              </button>

              <button
                onClick={() => alert("Confirm Documentary Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Documentary
              </button>

              <button
                onClick={() => alert("Confirm Mystery Clicked!")}
                className="w-72 mx-auto px-6 py-4 bg-[#C7DEDB] text-[#2E454D] text-lg sm:text-xl font-medium border-2 border-black rounded-2xl hover:bg-[#b8d4d1] transition-colors block"
                style={{ outline: '2px solid black', outlineOffset: '0px' }}
              >
                Mystery
              </button>
            </div>
          </div>
        </div>

        <div className="text-center mt-16">
          <button
            onClick={() => alert("Confirm Complete Sign Up Clicked!")}
            className="px-24 py-4 !bg-green-800 text-white text-xl font-medium border-2 border-black hover:!bg-green-700 transition-colors w-[28rem]"
            style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '0px' }}
          >
            Complete Sign Up
          </button>
        </div>*/}
      </div>
    </main>
  );
}
