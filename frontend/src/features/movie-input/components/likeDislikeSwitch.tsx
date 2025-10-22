import * as React from "react"
import * as SwitchPrimitive from "@radix-ui/react-switch"
import { cn } from "@/lib/utils"

export function LikeDislikeSwitch({ className, ...props }: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      className={cn(
        "group relative inline-flex h-[1.5rem] w-18 items-center rounded-full justify-between px-2 peer",
        "!bg-[#2E454D] data-[state=checked]:bg-primary data-[state=unchecked]:bg-input dark:data-[state=unchecked]:bg-input/80",
        "shadow-xs transition-all outline-2  disabled:cursor-not-allowed disabled:opacity-50",
        "outline-black",
        className
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb
        className={cn(
            "absolute left-8.5 h-[1.5rem] w-[1.5rem] rounded-full ml-[-45%]",
            "bg-[#879B9E]",
            "pointer-events-none ring-0 transition-transform duration-250", 
            "data-[state=checked]:translate-x-[calc(185%)] data-[state=unchecked]:translate-x-0"
        )}
      >
      </SwitchPrimitive.Thumb>
    </SwitchPrimitive.Root>
  )
}
