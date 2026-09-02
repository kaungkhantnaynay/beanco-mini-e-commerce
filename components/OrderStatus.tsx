"use client";

import { CheckCircle2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import Button from "@/components/Button";
import ButtonLink from "@/components/ButtonLink";
import { createPaymentSession, getOrderStatus } from "@/lib/api/commerce";
import { ApiRequestError } from "@/lib/api/client";
import { formatTHB } from "@/lib/format";
import type { OrderStatusResponse } from "@/lib/types/api";

const statusLabels: Record<OrderStatusResponse["status"], string> = {
  awaiting_payment: "Awaiting payment",
  confirmed: "Confirmed",
  fulfilling: "Being prepared",
  shipped: "Shipped",
  delivered: "Delivered",
  cancelled: "Cancelled",
};

function checkoutKey() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `stripe-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function isStripeCheckoutUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && (url.hostname === "stripe.com" || url.hostname.endsWith(".stripe.com"));
  } catch {
    return false;
  }
}

export default function OrderStatus({
  publicId,
  onRedirect = (url) => window.location.assign(url),
}: {
  publicId: string;
  onRedirect?: (url: string) => void;
}) {
  const [order, setOrder] = useState<OrderStatusResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isPaying, setIsPaying] = useState(false);
  const paymentKey = useState(checkoutKey)[0];

  const loadOrder = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      setOrder(await getOrderStatus(publicId));
    } catch (caught) {
      setError(caught instanceof ApiRequestError ? caught.message : "We could not load this order.");
    } finally {
      setIsLoading(false);
    }
  }, [publicId]);

  useEffect(() => { void loadOrder(); }, [loadOrder]);

  async function handlePayment() {
    if (!order || isPaying) return;
    setIsPaying(true);
    setError("");
    try {
      const session = await createPaymentSession(order.public_id, paymentKey);
      if (!isStripeCheckoutUrl(session.checkout_url)) throw new Error("Unexpected checkout URL.");
      onRedirect(session.checkout_url);
    } catch (caught) {
      setError(caught instanceof ApiRequestError ? caught.message : "Secure payment could not be started. Please try again.");
      setIsPaying(false);
    }
  }

  if (isLoading) return <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground" role="status">Loading order…</div>;

  if (!order) {
    return (
      <div className="rounded-xl border bg-card p-8 text-center">
        <h2 className="text-xl font-semibold">Order could not be loaded</h2>
        <p className="mt-2 text-sm text-muted-foreground">{error}</p>
        <Button type="button" className="mt-5" onClick={() => void loadOrder()}>Try again</Button>
      </div>
    );
  }

  return (
    <section className="mx-auto max-w-2xl rounded-xl border bg-card p-6 shadow-sm sm:p-10" aria-labelledby="order-heading">
      <CheckCircle2 className="h-10 w-10 text-primary" aria-hidden="true" />
      <p className="mt-5 text-sm font-semibold uppercase tracking-[0.16em] text-primary">Order received</p>
      <h1 id="order-heading" className="mt-2 text-3xl font-bold tracking-tight">Thank you for your order</h1>
      <p className="mt-4 leading-relaxed text-muted-foreground">Your order is recorded and stock is reserved. Payment has not been captured yet.</p>
      <dl className="mt-8 divide-y rounded-lg border">
        <div className="flex flex-col gap-1 p-4 sm:flex-row sm:justify-between"><dt className="text-sm text-muted-foreground">Order reference</dt><dd className="break-all text-sm font-semibold">{order.public_id}</dd></div>
        <div className="flex justify-between gap-4 p-4"><dt className="text-sm text-muted-foreground">Status</dt><dd className="text-sm font-semibold">{statusLabels[order.status]}</dd></div>
        <div className="flex justify-between gap-4 p-4"><dt className="text-sm text-muted-foreground">Total</dt><dd className="text-sm font-semibold">{formatTHB(order.total)}</dd></div>
        <div className="flex justify-between gap-4 p-4"><dt className="text-sm text-muted-foreground">Created</dt><dd className="text-sm font-semibold">{new Intl.DateTimeFormat("en-TH", { dateStyle: "medium", timeStyle: "short" }).format(new Date(order.created_at))}</dd></div>
      </dl>
      <div className="mt-8 flex flex-wrap gap-3">
        {order.status === "awaiting_payment" ? <Button type="button" disabled={isPaying} aria-busy={isPaying} onClick={() => void handlePayment()}>{isPaying ? "Opening Stripe…" : "Pay securely with Stripe"}</Button> : null}
        <Button type="button" variant="outline" onClick={() => void loadOrder()}>Refresh status</Button>
        <ButtonLink href="/products">Continue shopping</ButtonLink>
      </div>
      {error ? <p className="mt-4 rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">{error}</p> : null}
    </section>
  );
}
