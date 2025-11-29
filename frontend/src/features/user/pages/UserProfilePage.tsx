import Header from "@/features/navbar/components/Header";
import { useAuth } from "@/shared/hooks/useAuth";

export default function ProfilePage() {
    // Colin Harris - UserProfilePage -
    // I labeled everything with comments so you know what each section is for.

    // List of important locations:
    // Favorites is under the favorites background flavor-image section.
    // Bio is under the bio background flavor-image section. Shares a similar name with favorites.
    const { user } = useAuth() 

    return (
        <main>
            <Header/>

            {/*background image for the page, user should be able to customize?*/}
            <div className="bg-[#55757F] h-[22.5rem] w-full absolute top border-[0.5rem] rounded-[15px] border-[#384A4F]">
                
            </div>
            
            {/*favorites flavor-text, don't touch*/}
            <div className="flex h-[90vh] w-full left-center items-center">
                <p className="text-white text-3xl absolute top-[60vh] ml-[52px]"> Users Favorites </p>
            </div>
            
            {/*profile picture*/}
            <div className="bg-[#D9D9D9] h-[12.5rem] w-[12.5rem] rounded-full absolute top-50 ml-[50px]"/>

            {/*background flavor-image FAVORITES / pading for FAVORITES (Don't touch)*/}
            <div className="bg-[#55757F] h-[14.5rem] w-[80.5rem] absolute top-120 ml-[50px] border-[0.5rem] rounded-[15px] border-[#384A4F]">
                {/*Favorites, update this based on what they like.*/}
                <p className="text-white text-3xl absolute top-[2vh] text-[25px] ml-[6px]"> List of Favorites </p>
            </div>

            {/*background flavor-image BIO / pading for BIO (Don't touch)*/}
            <div className="bg-[#2E454D] h-[12.5rem] w-[50.5rem] absolute top-48 ml-[320px] border-[0.5rem] rounded-[15px] border-[#384A4F]">
                {/*BIO, update this based on what they type or change.*/}
                <p className="text-white text-3xl absolute top-[2vh] text-[25px] ml-[6px]"> Bio here </p>
            </div>

            {/*This will be the username*/}
            <div className="flex h-[50vh] w-full left-center items-center">
                <p className="text-white text-3xl absolute top-36 text-[36px] ml-[330px]"> {user.username} </p>
            </div>

            {/*Edit User Name button*/}
            <div className="bg-[#D9D9D9] h-[2rem] w-[2rem] rounded-full absolute top-38 ml-[520px]"/>

            {/*Edit Bio button*/}
            <div className="bg-[#D9D9D9] h-[2rem] w-[2rem] rounded-full absolute top-54 ml-[1140px]"/>

        </main>

        
    )
}
