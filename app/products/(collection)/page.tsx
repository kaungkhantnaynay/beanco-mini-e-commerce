import CatalogPagination from "@/components/CatalogPagination";
import { CatalogState } from "@/components/CatalogState";
import Container from "@/components/Container";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import ProductCard from "@/components/ProductCard";
import ProductFilters from "@/components/ProductFilters";
import { getCategories, getProducts } from "@/lib/api/catalog";
import type { Category, PaginatedResponse, ProductFilters as Filters, ProductSummary, ProductType } from "@/lib/types/api";

type SearchParams = Record<string, string | string[] | undefined>;

const first = (value: string | string[] | undefined) =>
  Array.isArray(value) ? value[0] : value;

function parsePage(value: string | undefined): number {
  const parsed = Number.parseInt(value ?? "1", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
}

function parseFilters(searchParams: SearchParams): Filters {
  const type = first(searchParams.type);
  const ordering = first(searchParams.ordering);
  const validTypes: ProductType[] = ["coffee", "equipment", "drinkware"];
  const validOrdering: NonNullable<Filters["ordering"]>[] = ["name", "-name", "price", "-price"];

  return {
    category: first(searchParams.category),
    type: validTypes.includes(type as ProductType) ? (type as ProductType) : undefined,
    availability: first(searchParams.availability) === "true" ? true : undefined,
    search: first(searchParams.search),
    minimum_price: first(searchParams.minimum_price),
    maximum_price: first(searchParams.maximum_price),
    ordering: validOrdering.includes(ordering as NonNullable<Filters["ordering"]>)
      ? (ordering as NonNullable<Filters["ordering"]>)
      : "name",
    page: parsePage(first(searchParams.page)),
    page_size: 12,
  };
}

function paginationParams(searchParams: SearchParams): URLSearchParams {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(searchParams)) {
    const scalar = first(value);
    if (scalar) query.set(key, scalar);
  }
  return query;
}

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const resolvedSearchParams = await searchParams;
  const filters = parseFilters(resolvedSearchParams);
  let error = "";
  let catalog: PaginatedResponse<ProductSummary> | null = null;
  let categories: Category[] = [];

  try {
    [catalog, { results: categories }] = await Promise.all([
      getProducts(filters),
      getCategories(),
    ]);
  } catch (caught) {
    error = caught instanceof Error ? caught.message : "The catalog is temporarily unavailable.";
  }

  return (
    <main className="min-h-screen bg-background font-sans antialiased">
      <Navbar />
      <div className="pb-12 pt-24">
        <Container>
          <div className="mb-10">
            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
              Coffee Collection
            </h1>
            <p className="mt-4 text-lg text-muted-foreground">
              Review the roasts, brew tools, and service-ready essentials behind the BeanCo program.
            </p>
          </div>

          <ProductFilters categories={categories} filters={filters} />

          {error ? (
            <CatalogState title="We could not load the collection" detail={error} retryHref="/products" />
          ) : catalog?.results.length ? (
            <>
              <p className="mb-5 text-sm text-muted-foreground" aria-live="polite">
                {catalog.count} {catalog.count === 1 ? "product" : "products"}
              </p>
              <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
                {catalog.results.map((product, index) => (
                  <ProductCard key={product.slug} product={product} index={index} />
                ))}
              </div>
              <CatalogPagination
                count={catalog.count}
                currentPage={filters.page ?? 1}
                pageSize={filters.page_size ?? 12}
                searchParams={paginationParams(resolvedSearchParams)}
              />
            </>
          ) : (
            <CatalogState
              title="No products match these filters"
              detail="Try a broader search or clear the current filters."
              retryHref="/products"
            />
          )}
        </Container>
      </div>
      <Footer />
    </main>
  );
}
