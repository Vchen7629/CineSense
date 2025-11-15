import { ChangePaginationPage } from '../utils/changePaginationPage';


// Const for easier code readability
const PaginationDirection = {
  Previous: -1,
  Next: 1,
} as const;

interface PaginationProps {
  currentPage: number;
  setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
  totalPage: number;
  listView: boolean;
  gridView: boolean;
}

// Component for pagination ui elements
const PaginationComponent = ({
  currentPage,
  setCurrentPage,
  totalPage,
  listView,
  gridView
}: PaginationProps) => {
  return (
    <main className={`flex ${listView && "w-full justify-center items-center h-[5%]"} ${gridView && "h-full"} space-x-2`}>
      <button
        className="flex items-center justify-center h-7 w-7 hover:text-cyan-200 bg-[#879B9E] rounded-md shadow-sm shadow-black "
        onClick={() =>
          ChangePaginationPage(
            setCurrentPage,
            totalPage,
            PaginationDirection.Previous,
            currentPage
          )
        }
      >
        {'<'}
      </button>
      <div className='text-white text-lg font-semibold'>
        Showing {currentPage} of {totalPage}
      </div>
      <button
        className="flex items-center justify-center h-7 w-7 hover:text-cyan-200 bg-[#879B9E] rounded-md shadow-sm shadow-black"
        onClick={() =>
          ChangePaginationPage(
            setCurrentPage,
            totalPage,
            PaginationDirection.Next,
            currentPage
          )
        }
      >
        {'>'}
      </button>
    </main>
  );
};

export default PaginationComponent;
