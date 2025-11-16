import type React from "react"
import { useState } from "react"

const YearFilterComponent = () => {
  const [year, setYear] = useState<string>()

  const minYear = 1888;
  const maxYear = new Date().getFullYear();

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = e.target.value

    // Allow empty input
    if (raw === "") {
      setYear("");
      return;
    }

    // Only allow digits
    if (/^\d+$/.test(raw)) {
      const num = Number(raw);

      if (num >= minYear && num <= maxYear) {
        setYear(raw);
      }
    }
  }

  return (
    <input 
      type="text"
      value={year}
      onChange={handleChange}
      placeholder="YYYY"
      className="pl-2 rounded-lg h-8 w-14 border bg-teal-600" 
    />
  )
}


export default YearFilterComponent
