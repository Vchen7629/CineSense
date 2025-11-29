import { useState, useEffect } from "react";

const STORAGE_KEY = 'recommendation_index'

// hook to store current index of rated movie of current batch to localstorage
// so rated movies in batch arent lost on refresh
export function useRecommendationIndex(user_id: string | undefined) {
    const [currentIndex, setCurrentIndex] = useState(() => {
        if (!user_id) return 0

        const stored = localStorage.getItem(`${STORAGE_KEY}_${user_id}`)
        if (stored) {
            try {
                return parseInt(stored, 10)
            } catch {
                return 0
            }
        }
        return 0
    })

    // Persist currentIndex to localstorage whenever it changes
    useEffect(() => {
        if (user_id) {
            localStorage.setItem(`${STORAGE_KEY}_${user_id}`, currentIndex.toString());
        }
    }, [currentIndex, user_id])

    const nextMovie = () => {
        setCurrentIndex(prev => prev + 1)
    }

    const resetIndex = () => {
        setCurrentIndex(0)
        if (user_id) {
            localStorage.removeItem(`${STORAGE_KEY}_${user_id}`);
        }
    }

    return {
        currentIndex,
        nextMovie,
        resetIndex,
    }
} 
