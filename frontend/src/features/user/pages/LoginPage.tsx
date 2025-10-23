import Header from "@/features/navbar/components/Header";
import { Link } from "react-router";

export default function LoginPage() {
    return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      
      <div className="px-8">
        <p className="mt-15 text-white text-5xl">Log In</p>
      </div>

      <p className="absolute top-[250px] ml-[30px] text-white text-2xl">Username or Email:</p>

      <div className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-72 ml-[30px] border-4 border-[#000000] flex items-center">
        <p className="text-black text-[20px] ml-[10px]">Username/Email Here</p>
      </div>


      <p className="absolute top-[400px] ml-[30px] text-white text-2xl">Password:</p>

      <div className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-110 ml-[30px] border-4 border-[#000000] flex items-center">
        <p className="text-black text-[20px] ml-[10px]">Password Here</p>
      </div>

      <div className="absolute top-[540px] ml-30[px] flex flex-col space-y-2">
        <Link
            to="/signup"
            className="text-blue-400 text-[20px] ml-[30px] underline hover:text-blue-300 transition-colors"
        >
            Don't Have An Account?
        </Link>
      </div>


      <Link
        to = "/"
        className="flex absolute bottom-70 left-10 px-8 py-4 !bg-green-800 items-center justify-center text-white text-xl font-medium w-72 border-2 border-black"
        style={{ outline: '2px solid black', outlineOffset: '0px', borderRadius: '9999px' }}
      >
        Login
      </Link>
    </main>
  );
}