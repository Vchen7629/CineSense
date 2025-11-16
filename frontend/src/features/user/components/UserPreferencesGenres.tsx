import { CircleCheckBig } from "lucide-react";
import { all_genres } from "../misc/genreList";
import { useEffect } from "react";

interface UserPrefProps {
    selectedGenres: string[]
    setSelectedGenres: React.Dispatch<React.SetStateAction<string[]>>;
    setCanSignup: React.Dispatch<React.SetStateAction<boolean>>;
}

const UserPreferencesGenresGrid = ({ selectedGenres, setSelectedGenres, setCanSignup }: UserPrefProps) => {

    function toggleGenre(genre: string) {
        setSelectedGenres((prev: string[]) => {
            const isSelected = prev.includes(genre);

            // If removing → always allow
            if (isSelected) {
                return prev.filter(g => g !== genre);
            }
            
            // only allow adding 3 max genres
            if (prev.length < 3) {
                return [...prev, genre];
            }

            return prev;
        })
    }

    // if selected all 3, set state so signup button can be clicked
    useEffect(() => {
        setCanSignup(selectedGenres.length === 3);
    }, [selectedGenres]);

    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {all_genres.map((genre) => {
              const active = selectedGenres.includes(genre);
              return (
                <button
                  key={genre}
                  onClick={() => toggleGenre(genre)}
                  className={`flex items-center justify-between gap-2 px-5 py-3 rounded-lg border transition duration-250
                    ${active ? "bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner transform scale-100"
                    : "bg-[#2E454D] border-teal-600/50 text-slate-200 hover:scale-[1.03]"}
                  `}
                >
                  <span className="font-medium">{genre}</span>
                  {active && (
                    <CircleCheckBig/>
                  )}
                </button>
              );
            })}
          </div>
    )
}

export default UserPreferencesGenresGrid