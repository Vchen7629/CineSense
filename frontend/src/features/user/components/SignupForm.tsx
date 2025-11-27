import { useState } from "react";

interface SignUpForm {
    onContinue: (
        data: {
            username: string,
            email: string,
            password: string
        }
    ) => void
}

const SignUpForm = ({ onContinue }: SignUpForm) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onContinue({ username, email, password });
    };

    return (
        <form onSubmit={handleSubmit} className="flex flex-col w-full space-y-[2%]">
            <div className="flex flex-col space-y-[2.5%] w-full">
                <label className="text-white text-[1.5vh] sm:text-[1.75vh]">Username:</label>
                <input 
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="enter username..."
                    className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                />
            </div>
            <div className="flex flex-col space-y-[2.5%] w-full">
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] block">Email:</label>
                <input 
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="enter username..."
                    className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                />
            </div>
            <div className="flex flex-col space-y-[2.5%] w-full">
                <label className="text-white text-[1.5vh] sm:text-[1.75vh] block">Password:</label>
                <input 
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="enter username..."
                    className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                />
            </div>
            <button
              type="submit"
              className="bg-teal-600 w-full h-[5.5vh] text-white font-medium border-2 border-black rounded-lg mt-8 flex items-center justify-center"
            >
              Continue
            </button>
        </form>
    )
}

export default SignUpForm