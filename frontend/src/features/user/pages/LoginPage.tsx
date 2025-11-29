import Header from "@/features/navbar/components/Header";
import { Link } from "react-router";
import LoginForm from "../components/loginform";

const LoginPage = () => {

    return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />
      <section className="flex flex-col space-y-[2.5vh] items-center mx-auto py-[7vh] h-full">
        <section className="flex flex-col w-[30%] space-y-[4%] items-center h-[65vh] bg-[#394B51] shadow-md shadow-black rounded-xl py-[3%] px-[3%]">
          <section className="flex flex-col space-y-[1.5vh] items-center">
            <span className="text-4xl text-white font-bold">Login</span>
            <span className="text-gray-400 text-lg">Welcome back!</span>
          </section>
          <LoginForm />
          <div className="flex flex-col items-center space-y-[1%]">
            <span>Don't Have An Account?</span>
            <Link
                to="/signup"
                className="text-blue-400 text-md hover:text-blue-300 transition-colors"
            >
                Sign-Up
            </Link>
          </div>
        </section>
      </section>
    </main>
  );
}

export default LoginPage