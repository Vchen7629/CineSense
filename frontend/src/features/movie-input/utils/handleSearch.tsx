import type { DummyItem } from "../types/data";

// Function to filter archive data based on search input
export function HandleSearch(
    query: string, 
    data: DummyItem[], 
    setData: React.Dispatch<React.SetStateAction<DummyItem[]>>
) {
    if (!query) {
        return setData(data)
    } else {
        setData(data
            .filter(item => item.name != null && item.name.toLowerCase().includes(query.toLowerCase())) // combine null check and search
        );
    };
}