import Header from "@/features/navbar/components/Header";
import { PencilIcon } from "lucide-react";
import { Link } from "react-router";

export default function SignUpPage() {
  return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      
      <div className="px-10">
        <p className="mt-20 text-white text-3xl">Sign Up With CineSense</p>
      </div>

      <div className="bg-[#D9D9D9] h-[20rem] w-[20rem] rounded-full absolute top-[300px] ml-[1260px]" />

      <div className="flex bg-[#D9D9D9] h-[4rem] w-[4rem] rounded-full absolute top-[450px] ml-[1125px] items-center justify-center " >
        <PencilIcon size = {40}/>
      </div>

      
      <p className="absolute top-[650px] ml-[1355px] text-white text-3xl">Username</p>

      <p className="absolute top-[290px] ml-[30px] text-white text-lg">Username:</p>
      <div className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-80 ml-[30px] border-4 border-[#000000]">
        <p className="text-black text-[25px] ml-[6px] mt-[15px]">Username Here</p>
      </div>

      <p className="absolute top-[430px] ml-[30px] text-white text-lg">Email:</p>
      <div className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-115 ml-[30px] border-4 border-[#000000]">
        <p className="text-black text-[25px] ml-[6px] mt-[15px]">Email Here</p>
      </div>
      
      <p className="absolute top-[570px] ml-[30px] text-white text-lg">Password:</p>
      <div className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-150 ml-[30px] border-4 border-[#000000]">
        <p className="text-black text-[25px] ml-[6px] mt-[15px]">Password Here</p>
      </div>

      <p className="absolute top-[710px] ml-[30px] text-white text-lg">Confirm Password:</p>
      <div className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-185 ml-[30px] border-4 border-[#000000]">
        <p className="text-black text-[25px] ml-[6px] mt-[15px]">Confirm Password</p>
      </div>

      <Link
        to = "/userpreferences"
        className="flex absolute bottom-40 left-320 px-8 py-4 !bg-green-800 items-center justify-center text-white text-xl font-medium w-72 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '9999px' }}
      >
        Continue
      </Link>
    </main>
  );
}