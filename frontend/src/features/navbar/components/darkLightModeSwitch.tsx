import * as React from "react"
import * as SwitchPrimitive from "@radix-ui/react-switch"
import { cn } from "@/lib/utils"
import lightmode from "@/shared/assets/lightmode.svg"
import darkmode from "@/shared/assets/darkmode.svg"

export function Switch({ className, ...props }: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      className={cn(
        "group relative inline-flex h-[2rem] w-26 items-center rounded-full justify-between px-2 peer",
        "bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner hover:bg-teal-800 data-[state=unchecked]:!bg-gray-400 data-[state=unchecked]:bg-input dark:data-[state=unchecked]:bg-input/80",
        "shadow-xs transition-all outline-2 outline-teal-700 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    >
        <span className="absolute left-8 text-[12px] font-medium text-white transition-opacity group-data-[state=checked]:opacity-0  group-data-[state=unchecked]:opacity-100">
            Light Mode
        </span>
        <span className="absolute left-2 text-[12px] font-medium opacity-0 group-data-[state=checked]:opacity-100  group-data-[state=unchecked]:opacity-0">
            Dark Mode
        </span>
      <SwitchPrimitive.Thumb
        className={cn(
            "absolute left-8.5 h-[1.6rem] w-[1.6rem] rounded-full ml-[-30%]",
            "data-[state=checked]:bg-gray-500 dark:data-[state=unchecked]:bg-foreground dark:data-[state=checked]:bg-primary-foreground",
            "pointer-events-none ring-0 transition-transform duration-250", 
            "data-[state=checked]:translate-x-[calc(275%)] data-[state=unchecked]:translate-x-0"
        )}
      >
        <img
            src={lightmode}
            alt="Light"
            className="h-[1.6rem] w-[1.6rem] rounded-full object-cover group-data-[state=checked]:hidden"
        />
        <img
            src={darkmode}
            alt="Dark"
            className="h-[1.6rem] w-[1.6rem] bg-teal-600/40 text-teal rounded-full object-cover hidden group-data-[state=checked]:block"
        />
      </SwitchPrimitive.Thumb>
    </SwitchPrimitive.Root>
  )
}
