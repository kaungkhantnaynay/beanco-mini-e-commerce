import { apiRequest } from "@/lib/api/client";
import type {
  Cart,
  CheckoutPreview,
  CheckoutPreviewInput,
  Order,
  OrderCreateInput,
  OrderStatusResponse,
  PaymentCheckoutSession,
} from "@/lib/types/api";

const browserMutationOptions = {
  cache: "no-store" as const,
  credentials: "include" as const,
};

export function getCart(): Promise<Cart> {
  return apiRequest<Cart>("cart/", browserMutationOptions);
}

export function addCartItem(variantSku: string, quantity: number): Promise<Cart> {
  return apiRequest<Cart>("cart/items/", {
    ...browserMutationOptions,
    method: "POST",
    body: JSON.stringify({ variant_sku: variantSku, quantity }),
  });
}

export function updateCartItem(publicId: string, quantity: number): Promise<Cart> {
  return apiRequest<Cart>(`cart/items/${publicId}/`, {
    ...browserMutationOptions,
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
}

export async function removeCartItem(publicId: string): Promise<void> {
  await apiRequest<null>(`cart/items/${publicId}/`, {
    ...browserMutationOptions,
    method: "DELETE",
  });
}

export function previewCheckout(input: CheckoutPreviewInput): Promise<CheckoutPreview> {
  return apiRequest<CheckoutPreview>("checkout/preview/", {
    ...browserMutationOptions,
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function createOrder(input: OrderCreateInput, idempotencyKey: string): Promise<Order> {
  return apiRequest<Order>("orders/", {
    ...browserMutationOptions,
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify(input),
  });
}

export function getOrderStatus(publicId: string): Promise<OrderStatusResponse> {
  return apiRequest<OrderStatusResponse>(`orders/${publicId}/status/`, {
    cache: "no-store",
  });
}

export function createPaymentSession(
  publicId: string,
  idempotencyKey: string,
): Promise<PaymentCheckoutSession> {
  return apiRequest<PaymentCheckoutSession>(`orders/${publicId}/payment-session/`, {
    ...browserMutationOptions,
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
  });
}
