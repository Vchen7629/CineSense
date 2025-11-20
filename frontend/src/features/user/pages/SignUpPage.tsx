import Header from "@/features/navbar/components/Header";
import { PencilIcon } from "lucide-react";
import { Link } from "react-router";
import SignUpForm from "../components/SignupForm";

const SignUpPage = () => {
  return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      <section className="flex flex-col space-y-[2.5vh] items-center mx-auto py-[7vh] h-full">
        <section className="flex flex-col space-y-[1vh] items-center">
          <span className="text-4xl text-white font-bold">Sign Up With CineSense</span>
          <span className="text-lg text-gray-300">Step 1 of 2: Enter Your Account Credentials</span>
        </section>
        <section className="flex flex-col w-[30%] space-y-[1%] items-center h-[65vh] bg-[#394B51] shadow-md shadow-black rounded-xl py-[3%] px-[3%]">
          <div className="relative flex justify-center items-center">
            <button
              className="absolute left-[-1.5vw] -translate-x-1/2 top-1/2 -translate-y-1/2 flex justify-center items-center bg-teal-600 w-8 h-8 rounded-full shadow-lg hover:bg-teal-700 transition-colors"
            >
              <PencilIcon className="w-5 h-5 text-white"/>
            </button>

            <div className="w-16 h-16 md:w-24 md:h-24 lg:w-32 lg:h-32 rounded-full overflow-hidden border-2 border-black flex-shrink-0">
              <img
                src="/placeholder-avatar.png"
                alt=""
                className="w-full h-full object-cover rounded-full bg-white"
              />
            </div>
          </div>
          <SignUpForm />
            <Link
              to="/userpreferences"
              className="bg-teal-600 w-full h-[10%] text-white font-medium border-2 border-black rounded-lg mt-8 flex items-center justify-center"
            >
              Continue
          </Link>
        </section>
      </section>
    </main>
  );
}

export default SignUpPage