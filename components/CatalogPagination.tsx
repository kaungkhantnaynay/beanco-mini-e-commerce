import Link from "next/link";

function pageHref(current: URLSearchParams, page: number): string {
  const next = new URLSearchParams(current);
  next.set("page", String(page));
  return `/products?${next.toString()}`;
}

export default function CatalogPagination({
  count,
  currentPage,
  pageSize,
  searchParams,
}: {
  count: number;
  currentPage: number;
  pageSize: number;
  searchParams: URLSearchParams;
}) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  if (totalPages <= 1) return null;

  const linkClass =
    "rounded-md border bg-background px-4 py-2 text-sm font-medium transition-[background-color,transform] duration-150 active:scale-[0.97] motion-reduce:transform-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

  return (
    <nav className="mt-12 flex items-center justify-center gap-4" aria-label="Product pages">
      {currentPage > 1 ? (
        <Link className={linkClass} href={pageHref(searchParams, currentPage - 1)}>
          Previous
        </Link>
      ) : null}
      <span className="text-sm text-muted-foreground">
        Page {currentPage} of {totalPages}
      </span>
      {currentPage < totalPages ? (
        <Link className={linkClass} href={pageHref(searchParams, currentPage + 1)}>
          Next
        </Link>
      ) : null}
    </nav>
  );
}
