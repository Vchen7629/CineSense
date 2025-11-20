import { useEffect, useState } from "react";

interface UserPreferencesProps {
    selectedGenres: string[]
    setSelectedGenres: React.Dispatch<React.SetStateAction<string[]>>;
}

const UserPreferencesHeader = ({ selectedGenres, setSelectedGenres }: UserPreferencesProps) => {
    const maxGenres = 3;
    const remaining = maxGenres - selectedGenres.length;
    const [canClear, setCanClear] = useState<boolean>(false)

    function toggleGenre(genre: string) {
        setSelectedGenres(prev => prev.filter(g => g !== genre));
    }

    function clearSelected(setSelectedGenres: (selectedGenres: string[]) => void) {
        setSelectedGenres([])
    }

    useEffect(() => {
        setCanClear(selectedGenres.length > 0);
    }, [selectedGenres])

    return (
        <header className="flex justify-between">
            <div className="flex items-center space-x-4">
                <span className="text-lg text-white font-bold">Selected Genres: </span>
                <div className="flex space-x-2 text-white items-center">
                    {selectedGenres.map((name, idx) => (
                        <div 
                            key={idx} 
                            className="px-3 py-1 rounded-full bg-teal-600/20 border border-teal-700 text-teal-200 text-sm flex items-center gap-2"
                        >   
                            <button onClick={() => toggleGenre(name)} className="text-teal-300 opacity-80 hover:opacity-100">✕</button>
                            <span className="opacity-80 hover:opacity-100">{name}</span>  
                        </div>
                    ))}
                </div>
            </div>
            <div className="flex space-x-4 items-center">
                <button 
                    disabled={!canClear}
                    onClick={() => clearSelected(setSelectedGenres)} 
                    className={
                        `flex justify-center w-16 px-4 py-2 rounded-md border-gray-700 text-center transition-colors duration-250
                        ${canClear ? "bg-teal-600/20 hover:bg-teal-600/40" : "bg-gray-700"}`
                    }>
                    <span>Clear</span>
                </button>
                <span className="text-gray-300">
                    {remaining > 0
                        ? `Select ${remaining} more`
                        : "Ready to Signup!"}
                </span>
            </div>
        </header>
    )
}

export default UserPreferencesHeader