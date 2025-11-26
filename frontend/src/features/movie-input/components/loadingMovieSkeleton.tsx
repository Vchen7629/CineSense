import { Skeleton } from "@/shared/components/shadcn/skeleton"

const LoadingMovieSkeleton = ({ listView, gridView}: any) => {

    return (
        <ul className={`h-full w-full space-y-[2%] ${gridView && "grid grid-cols-2 gap-4"}`}>
            {Array.from({ length: 4 }).map((_, idx) => (
                <li
                    key={idx}
                    className={`flex w-full items-center px-2 shadow-md shadow-black bg-[#394B51] rounded-xl
                        ${listView && "h-[25%]"} ${gridView && "h-[85%]"}`}
                >
                    {/* Poster skeleton */}
                    <Skeleton className={`${listView && "w-[10%]"} ${gridView && "w-[20%]"} h-[85%]`} />

                    {/* Content skeleton */}
                    <section className={`flex flex-col ${listView && "w-[70%] h-[90%] space-y-2"} ${gridView && "w-[50%] h-[80%]"} px-[2%]`}>
                        <Skeleton className="h-6 w-3/4" />
                        <Skeleton className="h-full w-full" />
                        <Skeleton className="h-8 w-24" />
                    </section>

                    {/* Metadata skeleton */}
                    <section className={`flex flex-col items-center h-[80%] ${listView && "w-[25%] space-y-3"} ${gridView && "w-[35%] space-y-4"}`}>
                        <div className="flex space-x-2">
                            <Skeleton className="h-6 w-12" />
                            <Skeleton className="h-6 w-12" />
                        </div>
                        <Skeleton className="h-8 w-20" />
                        <Skeleton className="h-6 w-28" />
                    </section>
                </li>
            ))}
        </ul>
    )
}

export default LoadingMovieSkeleton