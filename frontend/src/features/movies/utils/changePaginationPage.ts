export function ChangePaginationPage(
  setCurrentPage: React.Dispatch<React.SetStateAction<number>>,
  totalPage: number,
  action: number,
  currentPage: number
) {
  // calculate new page value
  const newPage = Math.min(Math.max(currentPage + action, 1), totalPage);

  // if new page is same as before, just return and dont call setCurrentPage
  if (newPage === currentPage) {
    return;
  }

  setCurrentPage(newPage)
}
