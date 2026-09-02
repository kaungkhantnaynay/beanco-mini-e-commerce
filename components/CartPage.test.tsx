import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CartPage from "@/components/CartPage";
import { getCart, updateCartItem } from "@/lib/api/commerce";

vi.mock("@/lib/api/commerce", () => ({ getCart: vi.fn(), updateCartItem: vi.fn(), removeCartItem: vi.fn() }));

const cart = {
  public_id: "cart-id", currency: "THB" as const,
  items: [{ public_id: "item-id", variant_sku: "BEAN-250", product_name: "Fictional Roast", option_name: "250g", quantity: 1, unit_price: "350.00", line_total: "350.00" }],
  subtotal: "350.00", discount_total: "0.00", shipping_total: "0.00", tax_total: "0.00", total: "350.00", expires_at: "2026-09-03T00:00:00Z",
};

describe("CartPage", () => {
  beforeEach(() => {
    vi.mocked(getCart).mockReset().mockResolvedValue(cart);
    vi.mocked(updateCartItem).mockReset().mockResolvedValue({ ...cart, items: [{ ...cart.items[0], quantity: 2, line_total: "700.00" }], subtotal: "700.00", total: "700.00" });
  });

  it("loads the cookie cart and replaces totals with the update response", async () => {
    render(<CartPage />);
    expect(await screen.findByText("Fictional Roast")).toBeVisible();
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Increase Fictional Roast quantity" }));
    expect(updateCartItem).toHaveBeenCalledWith("item-id", 2);
    expect(await screen.findByLabelText("Fictional Roast quantity")).toHaveTextContent("2");
    expect(screen.getAllByText(/฿700/).length).toBeGreaterThan(0);
  });
});
