import Header from "@/features/navbar/components/Header"

export default function RecommendationPage() {
    return (
        <main>
            <Header/>
            <div className="flex h-[90vh] w-full justify-center items-center ">
                <p className="text-white text-3xl"> </p>
            </div>

            {/*This will be the movies name and the body of the actual movie image*/}
            <div className="flex h-[90vh] w-full left-center items-center text-center">
                <div className="bg-[#A7BCBF] h-[32.5rem] w-[30rem] absolute top-40 ml-[38px] border-[0.5rem] rounded-[15px] border-[#384A4F]">
                    <p className="text-white text-3xl absolute -top-12 left-1/2 transform -translate-x-1/2">Movie Name</p>
                    <p className="text-white text-3xl absolute bottom-25 left-1/2 transform -translate-x-1/2 text-[25px]">Genera</p>
                    <div className="flex h-[90vh] w-full mt-[1rem] justify-between px-[15%] left-center items-center text-center">
                        {/*This will be the like button*/}
                        <div className="bg-[#33cc33] h-[2.8rem] w-[6rem] rounded-[15px]">
                            {/*You can put an icon here if you want. I would need the icon files though*/}
                        </div>
                        {/*This will be the DISLIKE button*/}
                        <div className="bg-[#cc3333] h-[2.8rem] w-[6rem] rounded-[15px]">
                            {/*You can put an icon here if you want. I would need the icon files though*/}
                        </div>
                    </div>
                </div>
            </div>


            {/*background flavor-image for description (Don't touch)*/}
            <div className="bg-[#A7BCBF] h-[32.5rem] w-[50.5rem] absolute top-40 ml-[600px] border-[0.5rem] rounded-[15px] border-[#384A4F]">
                {/*Publisher - who made the movie here.*/}
                <p className="text-white text-3xl absolute top-[1vh] text-[25px] ml-[6px]"> Publisher here </p>
                {/*Date - when was it made*/}
                <p className="text-white text-3xl absolute top-[6vh] text-[16px] ml-[6px]"> Release date here </p>
                {/*Description - what is this movie about.*/}
                <p className="text-white text-3xl absolute top-[12vh] text-[20px] ml-[6px]"> Movie description here </p>
            </div>
            
        </main>
    )
}

