import * as React from "react"
import * as SwitchPrimitive from "@radix-ui/react-switch"
import { cn } from "@/lib/utils"

export function LikeDislikeSwitch({ className, ...props }: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      className={cn(
        "group relative inline-flex h-6 w-16 items-center rounded-full justify-between px-1 peer",
        "bg-[#2E454D]",
        "shadow-xs transition-all outline-2 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb
        className={cn(
          "block h-5 w-5 rounded-full bg-[#879B9E] transition-transform duration-200",
          "translate-x-0 data-[state=checked]:translate-x-[125%]"
        )}
      />
    </SwitchPrimitive.Root>
  )
}
