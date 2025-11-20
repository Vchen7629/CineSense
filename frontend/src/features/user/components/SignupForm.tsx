
const SignUpForm = () => {
    return (
        <section className="flex flex-col w-full space-y-[2%]">
            <div className="flex flex-col space-y-[2.5%] w-full">
                <label className="text-white text-[1.5vh] sm:text-[1.75vh]">Username:</label>
                <input 
                    placeholder="enter username..."
                    className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                />
            </div>
            <div className="flex flex-col space-y-[2.5%] w-full">
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] block">Email:</label>
                <input 
                placeholder="enter username..."
                className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                />
            </div>
            <div className="flex flex-col space-y-[2.5%] w-full">
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] block">Password:</label>
                <input 
                placeholder="enter username..."
                className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                />
            </div>

        </section>
    )
}

export default SignUpForm