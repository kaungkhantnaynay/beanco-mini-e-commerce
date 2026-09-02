import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CheckoutFlow from "@/components/CheckoutFlow";
import { createOrder, getCart, previewCheckout } from "@/lib/api/commerce";
import { ApiRequestError } from "@/lib/api/client";

const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/api/commerce", () => ({ createOrder: vi.fn(), getCart: vi.fn(), previewCheckout: vi.fn() }));

const cart = {
  public_id: "cart-id", currency: "THB" as const,
  items: [{ public_id: "item-id", variant_sku: "BEAN-250", product_name: "Fictional Roast", option_name: "250g", quantity: 1, unit_price: "350.00", line_total: "350.00" }],
  subtotal: "350.00", discount_total: "0.00", shipping_total: "0.00", tax_total: "0.00", total: "350.00", expires_at: "2026-09-03T00:00:00Z",
};

async function completeCheckoutForm() {
  const user = userEvent.setup();
  const values: Array<[string, string]> = [
    ["Email", "buyer@example.test"], ["Full name", "Mali Example"], ["Phone", "081-234-5678"],
    ["Address", "99 Coffee Lane"], ["Subdistrict", "Khlong Tan"], ["District", "Watthana"],
    ["Province", "Bangkok"], ["Postal code", "10110"],
  ];
  for (const [label, value] of values) await user.type(screen.getByLabelText(label), value);
  await user.click(screen.getByRole("button", { name: "Review order" }));
  expect(await screen.findByRole("status")).toHaveTextContent("Address and availability confirmed");
  return user;
}

describe("CheckoutFlow", () => {
  beforeEach(() => {
    push.mockReset();
    vi.mocked(getCart).mockReset().mockResolvedValue(cart);
    vi.mocked(previewCheckout).mockReset().mockImplementation(async (input) => ({ cart, shipping_address: input.shipping_address, shipping_method: { code: "standard_th", name: "Standard delivery", fee: "0.00", minimum_business_days: 3, maximum_business_days: 5 } }));
    vi.mocked(createOrder).mockReset().mockResolvedValue({ public_id: "order-123" } as never);
  });

  it("previews server totals before creating one idempotent order", async () => {
    render(<CheckoutFlow />);
    expect(await screen.findByText("Fictional Roast")).toBeVisible();
    const user = await completeCheckoutForm();
    await user.click(screen.getByRole("button", { name: /Place order/ }));

    expect(createOrder).toHaveBeenCalledTimes(1);
    expect(vi.mocked(createOrder).mock.calls[0][1].length).toBeGreaterThanOrEqual(16);
    expect(push).toHaveBeenCalledWith("/orders/order-123");
  });

  it("reuses the idempotency key when an order request is safely retried", async () => {
    vi.mocked(createOrder)
      .mockRejectedValueOnce(new ApiRequestError({ code: "network_error", detail: "Try again." }))
      .mockResolvedValueOnce({ public_id: "order-123" } as never);
    render(<CheckoutFlow />);
    expect(await screen.findByText("Fictional Roast")).toBeVisible();
    const user = await completeCheckoutForm();

    await user.click(screen.getByRole("button", { name: /Place order/ }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Try again.");
    await user.click(screen.getByRole("button", { name: /Place order/ }));

    expect(createOrder).toHaveBeenCalledTimes(2);
    expect(vi.mocked(createOrder).mock.calls[1][1]).toBe(vi.mocked(createOrder).mock.calls[0][1]);
    expect(push).toHaveBeenCalledWith("/orders/order-123");
  });
});
