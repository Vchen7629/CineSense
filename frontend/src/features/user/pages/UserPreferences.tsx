import Header from "@/features/navbar/components/Header";

export default function UserPreferences() {
  return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-20"> 
        <div className="text-center mb-12">
          <h1 className="text-white font-bold text-4xl sm:text-5xl lg:text-6xl">
            Pick Your Favorite Genres
          </h1>
          <p className="text-white text-xl sm:text-2xl mt-4 lg:mt-6">
            Select At Least 3 To Personalize Your Recommendations
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
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
        </div>
      </div>
    </main>
  );
}
