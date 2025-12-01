"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/shared/components/shadcn/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/shared/components/shadcn/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/shared/components/shadcn/popover"

interface searchFilterProps {
  list: filterItem[]
  filterValue: string
  setCurrentPage: React.Dispatch<React.SetStateAction<number>>
  setFilterValue: React.Dispatch<React.SetStateAction<string>>
  placeholder_text: string
}

interface filterItem {
  value: string
  label: string
}

export function SearchFilter({list, filterValue, setCurrentPage, setFilterValue, placeholder_text}: searchFilterProps) {
  const [open, setOpen] = React.useState(false)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between bg-teal-500/20 border-teal-400 text-teal-200 shadow-inner hover:bg-teal-800 border-none transition-colors duration-250"
        >
          {filterValue
            ? list.find((item: filterItem) => item.value === filterValue)?.label
            : `Select ${placeholder_text}...`}
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder={`Search ${placeholder_text}...`} className="h-9" />
          <CommandList>
            <CommandEmpty>No {placeholder_text} found.</CommandEmpty>
            <CommandGroup>
              {list.map((item: filterItem) => (
                <CommandItem
                  key={item.value}
                  value={item.value}
                  onSelect={(currentValue) => {
                    const newValue = currentValue === filterValue ? "" : currentValue;
                    setFilterValue(newValue);
                    setOpen(false);
                    setCurrentPage(1);
                  }}
                >
                  {item.label}
                  <Check
                    className={cn(
                      "ml-auto",
                      filterValue === item.value ? "opacity-100" : "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
