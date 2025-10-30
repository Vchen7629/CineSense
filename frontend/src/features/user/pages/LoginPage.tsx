import Header from "@/features/navbar/components/Header";
import { Link } from "react-router";

export default function LoginPage() {
    return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      
      <div className="px-8">
        <p className="mt-15 text-white text-5xl">Log In</p>
      </div>

      <label
        htmlFor="username"
        className="absolute top-[250px] ml-[30px] text-white text-2xl"
      >
        Username or Email:
      </label>

      <input
        id="username"
        type="text"
        placeholder="Enter username/email"
        className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-72 ml-[30px] border-4 border-[#000000] text-black text-[20px] pl-[15px] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
      />

      <label
        htmlFor="password"
        className="absolute top-[400px] ml-[30px] text-white text-2xl"
      >
        Password:
      </label>

      <input
        id="password"
        type="text"
        placeholder="Enter password"
        className="bg-[#C7DEDB] h-[5rem] w-[64rem] absolute top-110 ml-[30px] border-4 border-[#000000] text-black text-[20px] pl-[15px] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
      />

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