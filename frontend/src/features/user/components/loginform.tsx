import { email, z } from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/shared/components/shadcn/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod"
import { Toaster, toast } from "sonner";
import { onError } from "../utils/formError";
import { useLogin } from "../hooks/useLogin";
import { useNavigate } from "react-router";
import { Loader2 } from "lucide-react";

const formSchema = z.object({
    email: z.email({ pattern: z.regexes.html5Email }).min(4, {
        message: "Invalid Email, please enter a valid email",
    }),
    password: z.string().min(1, {
        message: "Missing password, please enter your password",
    }),
})

const LoginForm = () => {
    const { login, isLoading, isError, } = useLogin()
    const navigate = useNavigate()

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            email: "",
            password: ""
        },
    })

    async function onSubmit (values: z.infer<typeof formSchema>) {
        try {
            await login(values.email, values.password)

            navigate("/profile")
        } catch (error: any) {
            if (error.response?.data?.detail == "invalid email or password") {
                toast.error("Login failed, invalid email or password")
                return
            } else {
                toast.error("Login failed, try a new ")
                return
            }
        }
    };


    return (
        <Form {...form}>
            <Toaster position="bottom-right" expand visibleToasts={3} closeButton/>
            <form onSubmit={form.handleSubmit(onSubmit, onError)} className="flex flex-col w-full space-y-[2%]">
                <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                        <FormItem className="flex flex-col space-y-[2.5%] w-full">
                            <FormLabel className="text-white text-[1.5vh] sm:text-[1.75vh]">Email</FormLabel>
                            <FormControl>
                                <input 
                                    {...field}
                                    placeholder="enter email..."
                                    className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                                />
                            </FormControl>
                        </FormItem>
                    )}
                /> 
                <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                        <FormItem className="flex flex-col space-y-[2.5%] w-full">
                            <FormLabel className="text-white text-[1.5vh] sm:text-[1.75vh]">Password</FormLabel>
                            <FormControl>
                                <input 
                                    {...field}
                                    placeholder="enter password..."
                                    className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                                />
                            </FormControl>
                        </FormItem>
                    )}
                /> 
                <button
                    type="submit"
                    disabled={!form.formState.isValid}
                    className="bg-teal-600 w-full h-[5.5vh] text-white font-medium border-2 border-black rounded-lg mt-8 flex items-center justify-center disabled:bg-teal-800 disabled:cursor-not-allowed transition-all"
                >   
                    {isLoading ? (
                        <Loader2 className="animate-spin" />
                    ) : (
                        <span>Log In</span>
                    )}
                </button>
            </form>
        </Form>
    )
}

export default LoginForm