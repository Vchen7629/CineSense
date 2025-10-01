import { useState } from "react";

export const SignUpConfirmButton = () => {
    const [email, setEmail] = useState(""); 

    function handleClick() {
        console.log("Sign Up Confirm Button Clicked");

        setEmail("newemail@example.com");
    }

    return (
        <main className="w-full h-full bg-red-500 margin-top-16">
            <button onClick={handleClick}/>
            <input type="text" placeholder="Enter your email" />
            <p>{email}</p>  
        </main>
    )
}