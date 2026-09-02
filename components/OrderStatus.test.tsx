import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import OrderStatus from "@/components/OrderStatus";
import { createPaymentSession, getOrderStatus } from "@/lib/api/commerce";

vi.mock("@/lib/api/commerce", () => ({ createPaymentSession: vi.fn(), getOrderStatus: vi.fn() }));

describe("OrderStatus", () => {
  beforeEach(() => vi.mocked(getOrderStatus).mockReset().mockResolvedValue({ public_id: "order-123", status: "awaiting_payment", currency: "THB", total: "350.00", created_at: "2026-09-02T08:00:00Z", updated_at: "2026-09-02T08:00:00Z" }));

  it("shows a privacy-safe confirmation and payment state", async () => {
    render(<OrderStatus publicId="order-123" />);
    expect(await screen.findByText("Thank you for your order")).toBeVisible();
    expect(screen.getByText("Awaiting payment")).toBeVisible();
    expect(screen.getByText(/Payment has not been captured/)).toBeVisible();
    expect(getOrderStatus).toHaveBeenCalledWith("order-123");
  });

  it("opens only the Stripe-hosted checkout returned by the API", async () => {
    const redirect = vi.fn();
    vi.mocked(createPaymentSession).mockResolvedValue({ public_id: "attempt-1", status: "open", checkout_url: "https://checkout.stripe.com/c/pay/test", amount: "350.00", currency: "THB", expires_at: "2026-09-02T08:30:00Z" });
    render(<OrderStatus publicId="order-123" onRedirect={redirect} />);
    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: "Pay securely with Stripe" }));
    expect(createPaymentSession).toHaveBeenCalledTimes(1);
    expect(redirect).toHaveBeenCalledWith("https://checkout.stripe.com/c/pay/test");
  });
});
