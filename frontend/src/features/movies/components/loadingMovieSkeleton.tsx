import { Skeleton } from "@/shared/components/shadcn/skeleton"
import { Dot } from "lucide-react"

const LoadingMovieSkeleton = ({ listView, gridView}: any) => {

    return (
        <div className={`h-full w-full space-y-[2%] ${gridView && "grid grid-cols-4 gap-4"}`}>
            {listView ? (
                Array.from({ length: 4 }).map((_, idx) => (
                    <li
                        key={idx}
                        className={`flex w-full items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl
                            ${listView && "h-[20vh]"} ${gridView && "flex-col h-[35vh] pt-[1.5vh]"}`}
                    >
                        {/* Poster skeleton */}
                        <Skeleton className="w-[12.5%] h-[90%]"/>

                        {/* Content skeleton */}
                        <section className="flex flex-col w-[70%] h-full space-y-2 px-[2%] py-2">
                            <Skeleton className="h-6 w-[50%]" />
                            <div className="flex items-center">
                                <Skeleton className="rounded-full h-5 w-8"/>
                                <Dot />
                                <div className="flex items-center space-x-2">
                                    <Skeleton className="rounded-full h-5 w-18"/>
                                    <Skeleton className="rounded-full h-5 w-16"/>
                                </div>
                                <Dot />
                                <Skeleton className="rounded-full h-5 w-18"/>       
                            </div>
                            <Skeleton className="h-[45%] w-full" />
                            <Skeleton className="h-8 w-33" />
                        </section>

                        {/* popularity/avg rating/actors button */}
                        <section className="flex flex-col items-center h-[85%] w-[25%] space-y-3">
                            <div className="flex space-x-2">
                                <Skeleton className="rounded-full h-5 w-23" />
                                <Skeleton className="rounded-full h-5 w-22" />
                            </div>
                            <div className="flex items-center space-x-2">
                                <Skeleton className="h-5 w-26" />
                                <Skeleton className="h-7 w-18" />
                            </div>
                        </section>
                    </li>
                ))
            ) : gridView && (
                Array.from({ length: 12 }).map((_, idx) => (
                    <article
                        key={idx}
                        className="flex flex-col space-y-2 w-full items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl
                             h-[35vh] pt-[1.5vh]"
                    >
                        <Skeleton className="w-[95%] h-[65%]"/>
                        <Skeleton className="w-[95%] h-6 left-0"/>
                        <div className="flex w-[95%] items-center">
                            <Skeleton className="rounded-full h-5 w-14" />
                            <Dot/>
                            <Skeleton className="rounded-full h-5 w-8" />
                        </div>
                        <div className="flex w-[95%] items-center space-x-2">
                            <Skeleton className="rounded-full h-5 w-18" />
                            <Skeleton className="rounded-full h-5 w-20" />
                            <Skeleton className="rounded-full h-5 w-14" />
                        </div>
                    </article>
                ))
            )}
        </div>
    )
}

export default LoadingMovieSkeleton