import { Skeleton } from "@/shared/components/shadcn/skeleton"
import { Dot } from "lucide-react"
import { useEffect } from "react";

const LoadingMovieRecommendationsSkeleton = ({ isLoadingState, showContent, setShowSkeleton }: any) => {
    // Show skeleton only if loading takes longer than 500ms
    useEffect(() => {
        if (isLoadingState) {
            const skeletonTimer = setTimeout(() => setShowSkeleton(true), 1000);
            return () => clearTimeout(skeletonTimer);
        } else {
            setShowSkeleton(false);
        }
    }, [isLoadingState]);

    return (
        <>
            <div className={`absolute inset-0 flex flex-col space-y-[1vh] px-[0.5vw] py-[2.5vh] transition-opacity duration-300 ${isLoadingState || !showContent ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
                <div className="flex items-center justify-between w-[96%]">
                    <Skeleton className="w-[25%] h-10 ml-[1vw]" />
                    <div className="flex space-x-2 items-center">
                        <Skeleton className="w-32 h-5 rounded-full" />
                        <Skeleton className="w-28 h-5 rounded-full" />
                    </div>
                </div>
                <div className="flex space-x-2 ml-[2vw] mt-2">
                    <Skeleton className="w-[22.5%] h-7"/>
                    <Skeleton className="w-[10%] h-9 rounded-xl"/>
                </div>
                <div className="flex items-center ml-[2vw]">
                    <Skeleton className="w-[7.5%] h-5 rounded-full" />
                    <Dot size={28}/>
                    <Skeleton className="w-[7.5%] h-5 rounded-full" />
                    <Dot size={28}/>
                    <div className="flex space-x-2 w-[40%]">
                        <Skeleton className="w-[17.5%] h-5 rounded-full" />
                        <Skeleton className="w-[17.5%] h-5 rounded-full" />
                    </div>
                </div>
                <div className="flex flex-col ml-[2vw]">
                    <Skeleton className="w-[12.5%] h-6 rounded-xl"/>
                    <div className="flex space-x-2 mt-2">
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                    </div>
                </div>
                <div className="flex flex-col ml-[2vw]">
                    <Skeleton className="w-[12.5%] h-6 rounded-xl"/>
                    <div className="flex space-x-2 mt-2">
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                        <Skeleton className="w-[16.5%] h-8 rounded-full" />
                    </div>
                </div>
                <div className="bg-[#375367] h-[11.7rem] px-4 py-2 mt-[20px] w-[92.5%] rounded-[15px] ml-[2vw] border-[0.1rem] border-[#20363e]">
                    <div className="space-y-2">
                        <Skeleton className="w-full h-4" />
                        <Skeleton className="w-full h-4" />
                        <Skeleton className="w-full h-4" />
                        <Skeleton className="w-3/4 h-4" />
                    </div>
                </div>
            </div>
        </>
    )
}

export default LoadingMovieRecommendationsSkeleton