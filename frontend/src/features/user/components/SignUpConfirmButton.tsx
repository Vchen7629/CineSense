import { useState } from "react";

export const SignUpConfirmButton = () => {
    const [email, setEmail] = useState(""); 

    function handleClick() {
        console.log("Sign Up Confirm Button Clicked");

        setEmail("newemail@example.com");
    }

    return (
        <main className="w-full h-full bg-red-500 mt-16">
            <button onClick={handleClick}> Confirm</button>
            <input  
                type="text"
                placeholder="Enter your email"
                value={email}
                onChange={e => setEmail(e.target.value)}
            />
            <p>{email}</p>  
        </main>
    )
}