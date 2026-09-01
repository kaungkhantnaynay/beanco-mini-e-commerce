import { describe, expect, it } from "vitest";
import { buildCatalogQuery } from "@/lib/api/catalog";

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
