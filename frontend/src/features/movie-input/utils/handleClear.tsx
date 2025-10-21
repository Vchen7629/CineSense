import type { DummyItem } from "../types/data";

// Function to filter archive data based on search input
export function HandleClear(setData: React.Dispatch<React.SetStateAction<DummyItem[]>>) {
    setData([]);
}