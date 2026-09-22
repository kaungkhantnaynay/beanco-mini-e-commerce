import { afterEach, describe, expect, it, vi } from "vitest";
import {
  COMMERCE_TIMEOUT_MS,
  addCartItem,
  createOrder,
  createPaymentSession,
  getCart,
  removeCartItem,
  updateCartItem,
} from "@/lib/api/commerce";

describe("commerce API", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("keeps the anonymous cart cookie on every cart request", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await Promise.all([
      getCart(),
      addCartItem("COFFEE-250", 2),
      updateCartItem("item-id", 3),
      removeCartItem("item-id"),
    ]);

    expect(fetchMock).toHaveBeenCalledTimes(4);
    for (const call of fetchMock.mock.calls) {
      expect(call[1]).toEqual(
        expect.objectContaining({
          credentials: "include",
          cache: "no-store",
          signal: expect.any(AbortSignal),
        }),
      );
    }
    expect(fetchMock.mock.calls[1][1]).toEqual(expect.objectContaining({ method: "POST" }));
    expect(fetchMock.mock.calls[2][1]).toEqual(expect.objectContaining({ method: "PATCH" }));
    expect(fetchMock.mock.calls[3][1]).toEqual(expect.objectContaining({ method: "DELETE" }));
  });

  it("allows free-tier commerce requests enough time to survive a cold start", async () => {
    vi.useFakeTimers();
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    const fetchMock = vi.fn().mockImplementation(
      (_url: string, options: RequestInit) =>
        new Promise((_resolve, reject) => {
          options.signal?.addEventListener("abort", () =>
            reject(new DOMException("The operation was aborted.", "AbortError")),
          );
        }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const request = getCart();
    const timeoutExpectation = expect(request).rejects.toMatchObject({ code: "timeout" });
    await vi.advanceTimersByTimeAsync(COMMERCE_TIMEOUT_MS - 1);
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(false);
    await vi.advanceTimersByTimeAsync(1);
    await timeoutExpectation;
    vi.useRealTimers();
  });

  it("sends the idempotency key when creating an order", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ public_id: "order-id" }), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);

    await createOrder({
      customer_email: "buyer@example.test",
      shipping_method: "standard_th",
      shipping_address: {
        full_name: "Mali Example", phone: "0812345678", address_line_1: "99 Coffee Lane",
        address_line_2: "", subdistrict: "Khlong Tan", district: "Watthana",
        province: "Bangkok", postal_code: "10110", country_code: "TH",
      },
    }, "stable-checkout-key");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/orders/",
      expect.objectContaining({
        credentials: "include",
        method: "POST",
        headers: expect.objectContaining({ "Idempotency-Key": "stable-checkout-key" }),
      }),
    );
  });

  it("creates Stripe Checkout with the guest cookie and a retry key", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ public_id: "attempt-id", checkout_url: "https://checkout.stripe.com/test" }), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);

    await createPaymentSession("order-id", "stable-payment-key");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/orders/order-id/payment-session/",
      expect.objectContaining({
        credentials: "include",
        method: "POST",
        headers: expect.objectContaining({ "Idempotency-Key": "stable-payment-key" }),
      }),
    );
  });
});
