interface SignUpConfirmButtonProps {
    selectedGenres: string[]
    canSignup: boolean
}

export const SignUpConfirmButton = ({ selectedGenres, canSignup }: SignUpConfirmButtonProps) => {

    function handleClick() {
        console.log(selectedGenres);
    }

    return (
        <button
            disabled={canSignup}
            className={`${canSignup ? "bg-teal-600 hover:bg-teal-700" : "bg-gray-700"} w-28 px-4 py-2 rounded-md transition-colors duration-250`}
            onClick={handleClick}
        >
            Sign-up
        </button>
    )
}