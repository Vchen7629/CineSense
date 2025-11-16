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
      </div>
    </main>
  );
}
