import Header from "@/features/navbar/components/Header";
import { PencilIcon } from "lucide-react";
import { Link } from "react-router";

export default function SignUpPage() {
  return (
    <main className="bg-[#2E454D] min-h-screen">
      <Header />

      <div className="mx-auto pr-[0.5vw] sm:pr-[1vw] lg:pr-[2vw] pl-0 pt-[2vh] sm:pt-[3vh] lg:pt-[4vh]">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-[2vh] lg:gap-[3vh]">

          <div className="flex flex-col lg:col-span-2">
            <h1 className="text-white text-[2vh] sm:text-[2.5vh] lg:text-[3vh] font-bold mt-[0.5vh] lg:mt-[1vh] mb-[3vh] lg:mb-[4vh] ml-[0.5vw] sm:ml-[1vw]">
              Sign Up With CineSense
            </h1>

            <div className="space-y-[3vh] sm:space-y-[4vh] ml-[0.5vw] sm:ml-[1vw] mt-[1vh] sm:mt-[1.5vh] max-w-[80vw]">
              <div>
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] mb-[1.5vh] block">Username:</label>
                <div className="bg-[#C7DEDB] h-[6vh] sm:h-[8vh] w-full border-4 border-black rounded-lg flex items-center px-[1vw]">
                  <span className="text-black text-[1.75vh] sm:text-[2vh]">Username Here</span>
                </div>
              </div>

              <div>
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] mb-[1.5vh] block">Email:</label>
                <div className="bg-[#C7DEDB] h-[6vh] sm:h-[8vh] w-full border-4 border-black rounded-lg flex items-center px-[1vw]">
                  <span className="text-black text-[1.75vh] sm:text-[2vh]">Email Here</span>
                </div>
              </div>

              <div>
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] mb-[1.5vh] block">Password:</label>
                <div className="bg-[#C7DEDB] h-[6vh] sm:h-[8vh] w-full border-4 border-black rounded-lg flex items-center px-[1vw]">
                  <span className="text-black text-[1.75vh] sm:text-[2vh]">Password Here</span>
                </div>
              </div>

              <div>
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] mb-[1.5vh] block">Confirm Password:</label>
                <div className="bg-[#C7DEDB] h-[6vh] sm:h-[8vh] w-full border-4 border-black rounded-lg flex items-center px-[1vw]">
                  <span className="text-black text-[1.75vh] sm:text-[2vh]">Confirm Password</span>
                </div>
              </div>
            </div>
          </div>

          <div className="relative flex flex-col items-center lg:items-start justify-start pt-[8vh] lg:pt-[12vh]">
            <div 
              className="bg-[#D9D9D9] rounded-full relative"
              style={{
                height: 'clamp(280px, 35vh, 450px)',
                width: 'clamp(280px, 35vh, 450px)',
                marginLeft: 'clamp(0px, 10vw, 200px)',
                marginTop: 'clamp(24px, 6vh, 96px)'
              }}
            >
              <div 
                className="absolute flex bg-[#D9D9D9] rounded-full items-center justify-center border-4 border-[#2E454D]"
                style={{
                  left: 'clamp(-72px, -9vw, -144px)',
                  top: 'clamp(140px, 17.5vh, 280px)',
                  height: 'clamp(56px, 7vh, 112px)',
                  width: 'clamp(56px, 7vh, 112px)'
                }}
              >
                <PencilIcon 
                  style={{
                    height: 'clamp(28px, 3.5vh, 56px)',
                    width: 'clamp(28px, 3.5vh, 56px)'
                  }}
                />
              </div>
            </div>

            <p 
              className="text-white"
              style={{
                fontSize: 'clamp(1.5rem, 3vh, 2.5rem)',
                marginTop: 'clamp(32px, 4vh, 64px)',
                marginLeft: 'clamp(0px, 17vw, 272px)'
              }}
            >
              Username
            </p>

            <Link
              to="/userpreferences"
              className="!bg-green-800 text-white font-medium border-2 border-black rounded-full hover:!bg-green-700 flex items-center justify-center"
              style={{
                marginTop: 'clamp(56px, 7vh, 112px)',
                paddingLeft: 'clamp(28px, 3.5vw, 56px)',
                paddingRight: 'clamp(28px, 3.5vw, 56px)',
                paddingTop: 'clamp(14px, 1.75vh, 28px)',
                paddingBottom: 'clamp(14px, 1.75vh, 28px)',
                fontSize: 'clamp(1.125rem, 2vh, 1.75rem)',
                width: 'clamp(160px, 20vw, 320px)',
                marginLeft: 'clamp(0px, 10.5vw, 192px)',
                outline: '2px solid black',
                outlineOffset: '0px'
              }}
            >
              Continue
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
