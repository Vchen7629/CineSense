import { Skeleton } from "@/shared/components/shadcn/skeleton"

const LoadingMovieRecommendationsSkeleton = () => {

    return (
        <>
            <section className="flex flex-col justify-between relative items-center pt-[2.5vh] h-[32.5rem] w-[30rem] bg-[#394B51] shadow-md shadow-black rounded-xl">
                <Skeleton className="w-[55%] h-[7.5%]" />
                <div className="flex justify-center items-center space-x-4 h-[10%] w-full mb-4">
                    <Skeleton className="w-[40%] h-[55%]"/>
                    <Skeleton className="w-[15%] h-[70%] rounded-xl" />
                </div>
            </section>

            <section className="flex flex-col relative bg-[#394B51] h-[32.5rem] w-[50.5rem] px-[0.5vw] py-[2.5vh] rounded-xl shadow-md shadow-black rounded-xl">
                <div className="flex ml-[12px] space-x-[2.75%] items-center">
                    <Skeleton className="w-[15.5%] h-10"/>
                    <Skeleton className="w-[16%] h-9 rounded-xl"/>
                    <Skeleton className="w-[16%] h-9 rounded-xl"/>
                </div>
                <div className="flex ml-[12px] space-x-[2.75%] mt-[20px]">
                    <Skeleton className="w-[12.5%] h-10 mr-11"/>
                    <Skeleton className="w-[16%] h-9 rounded-xl"/>
                    <Skeleton className="w-[16%] h-9 rounded-xl"/>
                    <Skeleton className="w-[16%] h-9 rounded-xl"/>                   
                </div>
                <Skeleton className="h-[19.7rem] mt-[20px] w-[97%] rounded-[15px] ml-[8px]"/>
                <div className="flex w-full items-center mt-[20px] px-4 justify-between">
                    <Skeleton className="ml-[-9px] h-[2.6rem] w-[15%] rounded-[15px]"/>
                    <Skeleton className="h-[2.6rem] py-1 w-[40%] rounded-[15px]"/>
                    <Skeleton  className="h-[2.6rem] w-[20%] rounded-[15px] "/>
                </div>
            </section>
        </>
    )
}

export default LoadingMovieRecommendationsSkeleton