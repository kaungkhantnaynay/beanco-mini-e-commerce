import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiRequest } from "@/lib/api/client";
import { buildCatalogQuery, CATALOG_TIMEOUT_MS, getProducts } from "@/lib/api/catalog";

vi.mock("@/lib/api/client", () => ({ apiRequest: vi.fn() }));

describe("buildCatalogQuery", () => {
  it("maps whitelisted catalog filters to the API query contract", () => {
    const query = new URLSearchParams(
      buildCatalogQuery({
        category: "coffee",
        type: "coffee",
        featured: true,
        availability: false,
        search: "floral roast",
        minimum_price: "600.00",
        maximum_price: "900.00",
        ordering: "-price",
        page: 2,
      }),
    );

    expect(Object.fromEntries(query)).toEqual({
      category: "coffee",
      type: "coffee",
      featured: "true",
      availability: "false",
      search: "floral roast",
      minimum_price: "600.00",
      maximum_price: "900.00",
      ordering: "-price",
      page: "2",
    });
  });
});

describe("catalog requests", () => {
  beforeEach(() => {
    vi.mocked(apiRequest).mockReset();
    vi.mocked(apiRequest).mockResolvedValue({ count: 0, next: null, previous: null, results: [] });
  });

  it("allows a free Render service enough time to wake before timing out", async () => {
    await getProducts({ featured: true });

    expect(apiRequest).toHaveBeenCalledWith(
      "products/?featured=true",
      expect.objectContaining({ timeoutMs: CATALOG_TIMEOUT_MS }),
    );
    expect(CATALOG_TIMEOUT_MS).toBe(60_000);
  });
});
