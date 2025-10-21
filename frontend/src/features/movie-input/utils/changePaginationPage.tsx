export function ChangePaginationPage(
  setCurrentPage: React.Dispatch<React.SetStateAction<number>>,
  totalPage: number,
  action: number, // pass in +1 for next, -1 for previous page
  currentPage: number
) {
  // calculate new page value
  const newPage = Math.min(Math.max(currentPage + action, 1), totalPage);

  // if new page is same as before, just return and dont call setCurrentPage
  if (newPage === currentPage) {
    return;
  }

  // Only call setCurrentPage if page changes, ie not page 1 or last page
  setCurrentPage(newPage)
}
