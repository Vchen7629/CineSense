import type { DummyItem } from '../types/data';

// Function for handling deleting archive record
export function handleDeleteMovie(
  data: DummyItem[],
  setData: React.Dispatch<React.SetStateAction<DummyItem[]>>,
  setFilteredData: React.Dispatch<React.SetStateAction<DummyItem[]>>, 
  id: number,
) {
  const updatedData = data.filter(item => item.id !== id);
  setData(updatedData);
  setFilteredData(updatedData);
}
