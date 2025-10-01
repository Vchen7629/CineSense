import { useState } from "react";

export const SignUpConfirmButton = () => {
    const [email, setEmail] = useState(""); 

    function handleClick() {
        console.log("Sign Up Confirm Button Clicked");

        setEmail("newemail@example.com");
    }

    return (
        <main>
            <button onClick={handleClick}>Confirm Sign Up</button>
            <input type="text" placeholder="Enter your email" />
            <p>{email}</p>  
        </main>
    )
}