import type React from "react"

interface yearFilterValueProps {
  yearFilterValue: string
  setYearFilterValue: React.Dispatch<React.SetStateAction<string>>
}

const YearFilterComponent = ({ yearFilterValue, setYearFilterValue }: yearFilterValueProps) => {

  const minYear = 1888;
  const maxYear = new Date().getFullYear();

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = e.target.value

    // Allow empty input
    if (raw === "") {
      setYearFilterValue("");
      return;
    }

    // Only allow digits
    if (/^\d+$/.test(raw)) {
      const num = Number(raw);

      // Allow typing even if not complete
      if (raw.length <= 4) {
        // Only set if it's potentially valid (not checking max yet to allow typing)
        if (raw.length < 4 || (num >= minYear && num <= maxYear)) {
          setYearFilterValue(raw);
        }
      }
    }
  }

  return (
    <input
      type="text"
      value={yearFilterValue}
      onChange={handleChange}
      placeholder="YYYY"
      maxLength={4}
      className="pl-2 rounded-lg h-8 w-14 border bg-teal-500/20 text-teal-200 shadow-inner hover:bg-teal-800"
    />
  )
}


export default YearFilterComponent
