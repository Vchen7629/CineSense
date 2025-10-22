import Header from "@/features/navbar/components/Header";

export default function UserPreferences() {
  return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      
      <div className="px-10">
        <p className="mt-20 ml-115 text-white font-bold text-6xl">Pick Your Favorite Genres</p>
      </div>

      <div className="px-10">
        <p className="mt-10 ml-132 text-white text-2xl">Select Atleast 3 To Personalize Your Recommendations</p>
      </div>

      <button
        onClick={() => alert("Confirm Comedy Clicked!")}
        className="absolute top-92 left-124 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Comedy
      </button>

      <button
        onClick={() => alert("Confirm Action Clicked!")}
        className="absolute top-112 left-124 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Action
      </button>

      <button
        onClick={() => alert("Confirm Romance Clicked!")}
        className="absolute top-132 left-124 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Romance
      </button>

      <button
        onClick={() => alert("Confirm Thriller Clicked!")}
        className="absolute top-152 left-124 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Thriller
      </button>

      <button
        onClick={() => alert("Confirm Animation Clicked!")}
        className="absolute top-172 left-124 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Animation
      </button>

      <button
        onClick={() => alert("Confirm Drama Clicked!")}
        className="absolute top-92 left-220 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Drama
      </button>

      <button
        onClick={() => alert("Confirm Horror Clicked!")}
        className="absolute top-112 left-220 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Horror
      </button>

      <button
        onClick={() => alert("Confirm Sci-Fi Clicked!")}
        className="absolute top-132 left-220 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Sci-Fi
      </button>

      <button
        onClick={() => alert("Confirm Documentary Clicked!")}
        className="absolute top-152 left-220 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Documentary
      </button>

      <button
        onClick={() => alert("Confirm Myster Clicked!")}
        className="absolute top-172 left-220 px-8 py-4 bg-[#C7DEDB] text-[#2E454D] text-xl font-medium w-80 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '20px' }}
      >
        Mystery
      </button>

      <button
        onClick={() => alert("Confirm Complete Sign Up Clicked!")}
        className="absolute bottom-25 left-125 px-8 py-4 !bg-green-800 text-white text-xl font-medium w-175 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '0px' }}
      >
        Complete Sign Up
      </button>
    </main>
  );
}