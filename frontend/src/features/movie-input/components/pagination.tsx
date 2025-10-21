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
    <main className="flex w-full h-[5%] justify-center items-center space-x-2 ">
      <button
        className="flex items-center justify-center h-7 w-7 hover:text-cyan-200 bg-[#879B9E] rounded-md shadow-[0_4px_12px_rgba(20,40,45,0.5)] border-2 border-[#3A5A7A]"
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
        className="flex items-center justify-center h-7 w-7 hover:text-cyan-200 bg-[#879B9E] rounded-md shadow-[0_4px_12px_rgba(20,40,45,0.5)] border-2 border-[#3A5A7A]"
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
