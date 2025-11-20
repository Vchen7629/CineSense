import { useState } from "react"
import Header from "@/features/navbar/components/Header"
import RateMovieButtons from "@/features/movie-input/components/rateButtons"

export default function RecommendationPage() {
    {/*I probebly don't have to do this? But I'm going to do it for now. Change this if its not needed*/}
    const [rating, setRating] = useState(0);

    return (
        <main>
            <Header/>

    

            <div className="flex h-[90vh] w-full justify-center items-center ">
                <p className="text-white text-3xl"> </p>
            </div>

            {/*This will be the movies name and the body of the actual movie image*/}
            <div className="flex h-[90vh] w-full left-center items-center text-center">
                <div className="h-[32.5rem] w-[30rem] absolute top-40 ml-[38px] bg-[#394B51] shadow-md shadow-black rounded-xl">
                    
                    <p className="bold text-white text-3xl absolute -top-12 left-1/2 transform -translate-x-1/2 font-semibold">Movie Name</p>
                
                    <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2">
                        <RateMovieButtons rating={rating} setRating={setRating} />
                    </div>
                    
                </div>
                
            </div>

    

            {/*background flavor-image for description (Don't touch)*/}
            <div className="bg-[#394B51] h-[32.5rem] w-[50.5rem] absolute top-40 ml-[600px] rounded-xl shadow-md shadow-black rounded-xl">
                
                {/*Extra Box for detail under description (background)*/}
                 <div className="bg-[#375367] h-[19.7rem] w-[48rem] absolute top-32 rounded-[15px] ml-[8px] border-[0.1rem] border-[#20363e]">
                </div>
                
                {/*Publisher - who made the movie here.*/}
                <p className="text-white text-3xl absolute top-[1vh] text-[25px] ml-[12px] "> Directors: </p>
                <p className="text-white text-3xl absolute top-[1vh] text-[23px] ml-[160px] rounded-xl border-teal-400 border-[0.1rem] bg-teal-500/20 text-teal-200 shadow-inner px-3 py-1"> Name </p>
                <p className="text-white text-3xl absolute top-[1vh] text-[23px] ml-[380px] rounded-xl border-teal-400 border-[0.1rem] bg-teal-500/20 text-teal-200 shadow-inner px-3 py-1"> Name </p>

                {/*Actors*/}
                <p className="text-white text-3xl absolute top-[9vh] text-[25px] ml-[12px] "> Actors: </p>
                <p className="text-white text-3xl absolute top-[9vh] text-[23px] ml-[160px] rounded-xl border-teal-400 border-[0.1rem] bg-teal-500/20 text-teal-200 shadow-inner px-3 py-1"> Name </p>
                <p className="text-white text-3xl absolute top-[9vh] text-[23px] ml-[380px] rounded-xl border-teal-400 border-[0.1rem] bg-teal-500/20 text-teal-200 shadow-inner px-3 py-1"> Name </p>
                {/*Genere*/}
                <div className="bg-[#375367] h-[2.6rem] w-[18.5rem] absolute bottom-4 left-1/2 transform -translate-x-1/2 rounded-[15px] border-[0.1rem] border-[#20363e]">
                    <p className="bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 absolute bottom-1/6 left-1/2 transform -translate-x-1/2 text-[15px] rounded-xl border-teal-400 px-3 py-0.8 border-[0.1rem]">Genera2</p>
                    <p className="bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 absolute bottom-1/6 left-1/6 transform -translate-x-1/2 text-[15px] rounded-xl border-teal-400 px-3 py-0.8 border-[0.1rem]">Genera1</p>
                    <p className="bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 absolute bottom-1/6 left-5/6 transform -translate-x-1/2 text-[15px] rounded-xl border-teal-400 px-3 py-0.8 border-[0.1rem]">Genera3</p>
                </div>
                  {/*Languages*/}
                <div className="bg-[#375367] h-[2.6rem] w-[8rem] absolute bottom-4 rounded-[15px] border-[0.1rem] border-[#20363e] ml-[40rem]">
                    <p className="bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800 absolute bottom-1/6 left-1/2 transform -translate-x-1/2 text-[16px] rounded-xl border-teal-400 px-3 py-0.8 border-[0.1rem]">Languages</p>
                </div>
                {/*Date - when was it made*/}
                <p className="bg-teal-500/20 text-teal-200 shadow-inner text-3xl absolute bottom-5 text-[20px] ml-[12px] rounded-xl border-teal-400 border-[0.1rem] px-3 py-1"> Release date here </p>
                {/*Description - what is this movie about.*/}
                <p className="text-white text-3xl absolute top-[20vh] text-[20px] ml-[24px]"> Movie description here </p>
        
            </div>

    
            
        

        </main>
    )
}

