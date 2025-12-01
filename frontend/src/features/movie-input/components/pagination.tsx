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
}

// Component for pagination ui elements
const PaginationComponent = ({
  currentPage,
  setCurrentPage,
  totalPage,
}: PaginationProps) => {
  return (
    <main className="flex w-full justify-center items-center h-[5%] space-x-2">
      <button
        className="flex items-center justify-center h-7 w-7 hover:bg-teal-800 bg-teal-600 rounded-md shadow-sm shadow-black transition-colors duration-250"
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
      <div className='text-white text-lg font-light'>
        Showing {totalPage === 0 ? 0 : currentPage} of {totalPage}
      </div>
      <button
        className="flex items-center justify-center h-7 w-7 hover:bg-teal-800 bg-teal-600 rounded-md shadow-sm shadow-black transition-colors duration-250"
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
