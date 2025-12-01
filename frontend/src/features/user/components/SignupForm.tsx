import { z } from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/shared/components/shadcn/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod"
import { Toaster } from "sonner";
import { onError } from "../utils/formError";

interface SignUpForm {
    onContinue: (
        data: {
            username: string,
            email: string,
            password: string
        }
    ) => void
}

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
  email: z.email({ pattern: z.regexes.html5Email }).min(4, {
    message: "Please enter a valid email in the form of example@example.com",
  }),
  password: z.string().min(2, {
    message: "Password must be at least 2 characters.",
  }),
})

const SignUpForm = ({ onContinue }: SignUpForm) => {
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            username: "",
            email: "",
            password: ""
        },
    })

    function onSubmit (values: z.infer<typeof formSchema>) {
        onContinue(values);
    };

    return (
        <Form {...form}>
            <Toaster position="bottom-right" expand visibleToasts={3} closeButton/>
            <form onSubmit={form.handleSubmit(onSubmit, onError)} className="flex flex-col w-full space-y-[2%]">
                <FormField
                    control={form.control}
                    name="username"
                    render={({ field }) => (
                        <FormItem className="flex flex-col space-y-[2.5%] w-full">
                            <FormLabel className="text-white text-[1.5vh] sm:text-[1.75vh]">Username</FormLabel>
                            <FormControl>
                                <input 
                                    {...field}
                                    placeholder="enter username..."
                                    className="bg-[#2E454D] h-[5.5vh] w-full border-2 border-black rounded-lg flex items-center px-[1vw]"
                                />
                            </FormControl>
                        </FormItem>
                    )}
                /> 
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
                                    type="password"
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
                    Continue
                </button>
            </form>
        </Form>
    )
}

export default SignUpForm