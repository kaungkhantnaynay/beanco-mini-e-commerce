import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CatalogPagination from "@/components/CatalogPagination";

describe("CatalogPagination", () => {
  it("preserves active filters in previous and next page links", () => {
    render(
      <CatalogPagination
        count={30}
        currentPage={2}
        pageSize={12}
        searchParams={new URLSearchParams({ type: "coffee", ordering: "-price", page: "2" })}
      />,
    );

    expect(screen.getByRole("link", { name: "Previous" })).toHaveAttribute(
      "href",
      "/products?type=coffee&ordering=-price&page=1",
    );
    expect(screen.getByRole("link", { name: "Next" })).toHaveAttribute(
      "href",
      "/products?type=coffee&ordering=-price&page=3",
    );
    expect(screen.getByText("Page 2 of 3")).toBeVisible();
  });
});
