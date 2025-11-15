import { Star } from "lucide-react"
import { useEffect, useState } from "react";

const RateMovieButtons = ({rating, setRating}: any) => {
    const [hovered, setHovered] = useState<number>(0);
    
    useEffect(() => {
        console.log("RATING CHANGED:", rating)
    }, [rating]);

    return (
        <div className="flex">
            {Array.from({ length: 5 }).map((_, index) => {
                const starValue = index + 1;
                const isFilled = starValue <= (hovered || rating);

                return (
                <div
                    key={index}
                    className="p-1"
                    onMouseEnter={() => setHovered(starValue)}
                    onMouseLeave={() => setHovered(0)}
                    onClick={() => setRating(starValue)}
                >
                    <Star
                    className={`
                        w-6 h-6 transition-colors duration-250
                        ${isFilled 
                        ? "fill-teal-400 stroke-teal-400" 
                        : "stroke-teal-600"
                        }
                    `}
                    />
                </div>
                );
            })}
        </div>
    )
}

export default RateMovieButtons