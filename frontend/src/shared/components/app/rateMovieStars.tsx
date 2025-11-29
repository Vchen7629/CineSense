import { Star } from "lucide-react"
import { useState } from "react";

interface rateButtonProps {
    rating: number
    setRating: (rating: number) => void;
}

const RateMovieStars = ({rating, setRating}: rateButtonProps) => {
    const [hovered, setHovered] = useState<number>(0);

    const handleStarHover = (index: number, isLeftHalf: boolean) => {
        const starValue = isLeftHalf ? index + 0.5 : index + 1;
        setHovered(starValue);
    };

    const handleStarClick = (index: number, isLeftHalf: boolean) => {
        const starValue = isLeftHalf ? index + 0.5 : index + 1;
        setRating(starValue);
    };

    return (
        <div className="flex">
            {Array.from({ length: 5 }).map((_, index) => {
                const fullStarValue = index + 1;
                const halfStarValue = index + 0.5;
                const activeRating = hovered || rating;

                const isFull = fullStarValue <= activeRating;
                const isHalf = !isFull && halfStarValue <= activeRating;

                return (
                    <div
                        key={index}
                        className="relative cursor-pointer p-1"
                        onMouseLeave={() => setHovered(0)}
                    >
                        <div className="relative w-6 h-6">
                            <div className="absolute inset-0 pointer-events-none">
                                {isHalf ? (
                                    <div className="relative w-6 h-6">
                                        <Star className="absolute inset-0 w-6 h-6 stroke-teal-600 transition-colors duration-250" />
                                        <div className="absolute inset-0 w-1/2 overflow-hidden">
                                            <Star className="w-6 h-6 fill-teal-400 stroke-teal-400 transition-colors duration-250" />
                                        </div>
                                    </div>
                                ) : (
                                    <Star
                                        className={`
                                            w-6 h-6 transition-colors duration-250
                                            ${isFull 
                                                ? "fill-teal-400 stroke-teal-400" 
                                                : "stroke-teal-600"
                                            }
                                        `}
                                    />
                                )}
                            </div>
                            {/* Left half hover zone (0.5 rating) */}
                            <div
                                className="absolute inset-y-0 left-0 w-1/2 z-10"
                                onMouseEnter={() => handleStarHover(index, true)}
                                onClick={() => handleStarClick(index, true)}
                            />
                            {/* Right half hover zone (1.0 rating) */}
                            <div
                                className="absolute inset-y-0 right-0 w-1/2 z-10"
                                onMouseEnter={() => handleStarHover(index, false)}
                                onClick={() => handleStarClick(index, false)}
                            />
                        </div>
                    </div>
                );
            })}
        </div>
    )
}

export default RateMovieStars