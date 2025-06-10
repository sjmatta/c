import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  className = ""
}) => {
  // Helper function for conditional classes
  const cn = (...classes: (string | boolean | undefined)[]) => 
    classes.filter(Boolean).join(' ');

  const baseButtonClasses = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2";
  
  const regularButtonClasses = `${baseButtonClasses} h-10 px-4 py-2 border border-gray-300 bg-white hover:bg-gray-100`;
  
  const numberButtonClasses = `${baseButtonClasses} h-10 w-10 border border-gray-300 bg-white hover:bg-gray-100`;
  
  const activeButtonClasses = "bg-blue-600 text-white hover:bg-blue-600/90";
  
  const disabledButtonClasses = "opacity-50 cursor-not-allowed";

  return (
    <div className={cn("flex items-center justify-center gap-2 py-4", className)}>
      {/* Previous Button */}
      <button
        className={cn(
          regularButtonClasses,
          currentPage === 1 && disabledButtonClasses
        )}
        disabled={currentPage === 1}
        onClick={() => onPageChange(currentPage - 1)}
        aria-label="Go to previous page"
      >
        Previous
      </button>

      {/* Page Numbers */}
      {Array.from({ length: totalPages }, (_, index) => {
        const pageNumber = index + 1;
        const isActive = currentPage === pageNumber;
        
        return (
          <button
            key={pageNumber}
            className={cn(
              numberButtonClasses,
              isActive && activeButtonClasses,
              !isActive && "hover:bg-gray-100"
            )}
            onClick={() => onPageChange(pageNumber)}
            aria-current={isActive ? "page" : undefined}
            aria-label={`Go to page ${pageNumber}`}
          >
            {pageNumber}
          </button>
        );
      })}

      {/* Next Button */}
      <button
        className={cn(
          regularButtonClasses,
          currentPage === totalPages && disabledButtonClasses
        )}
        disabled={currentPage === totalPages}
        onClick={() => onPageChange(currentPage + 1)}
        aria-label="Go to next page"
      >
        Next
      </button>
    </div>
  );
};

export default Pagination;