import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ProductPurchase from "@/components/ProductPurchase";
import { addCartItem } from "@/lib/api/commerce";

vi.mock("@/lib/api/commerce", () => ({ addCartItem: vi.fn() }));

const variant = { sku: "BEAN-250", option_name: "250g whole bean", weight_grams: 250, grind: "whole_bean" as const, price: "350.00", available: true, available_quantity: 5 };
const cart = { public_id: "cart-id", currency: "THB" as const, items: [], subtotal: "350.00", discount_total: "0.00", shipping_total: "0.00", tax_total: "0.00", total: "350.00", expires_at: "2026-09-03T00:00:00Z" };

describe("ProductPurchase", () => {
  beforeEach(() => vi.mocked(addCartItem).mockReset());

  it("prevents duplicate clicks while adding and confirms the server total", async () => {
    let resolveRequest: ((value: typeof cart) => void) | undefined;
    vi.mocked(addCartItem).mockReturnValue(new Promise((resolve) => { resolveRequest = resolve; }));
    render(<ProductPurchase productName="Fictional Roast" variants={[variant]} />);
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: "Add to cart" }));
    expect(screen.getByRole("button", { name: "Adding…" })).toBeDisabled();
    expect(addCartItem).toHaveBeenCalledTimes(1);
    resolveRequest?.(cart);

    expect(await screen.findByRole("status")).toHaveTextContent("Fictional Roast added");
    expect(screen.getByRole("link", { name: "View cart" })).toHaveAttribute("href", "/cart");
  });
});
