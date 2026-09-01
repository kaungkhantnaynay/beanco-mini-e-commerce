import { apiRequest } from "@/lib/api/client";
import type {
  Category,
  PaginatedResponse,
  ProductDetail,
  ProductFilters,
  ProductSummary,
} from "@/lib/types/api";

export const CATALOG_REVALIDATE_SECONDS = 300;

export function buildCatalogQuery(filters: ProductFilters = {}): string {
  const query = new URLSearchParams();

  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") query.set(key, String(value));
  }

  return query.toString();
}

export async function getProducts(
  filters: ProductFilters = {},
): Promise<PaginatedResponse<ProductSummary>> {
  const query = buildCatalogQuery(filters);
  return apiRequest<PaginatedResponse<ProductSummary>>(`products/${query ? `?${query}` : ""}`, {
    next: { revalidate: CATALOG_REVALIDATE_SECONDS, tags: ["catalog-products"] },
  });
}

export async function getProduct(slug: string): Promise<ProductDetail> {
  return apiRequest<ProductDetail>(`products/${encodeURIComponent(slug)}/`, {
    next: { revalidate: CATALOG_REVALIDATE_SECONDS, tags: ["catalog-products", `product-${slug}`] },
  });
}

export async function getCategories(): Promise<PaginatedResponse<Category>> {
  return apiRequest<PaginatedResponse<Category>>("categories/?page_size=48", {
    next: { revalidate: CATALOG_REVALIDATE_SECONDS, tags: ["catalog-categories"] },
  });
}
