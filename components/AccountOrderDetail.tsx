"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Button from "@/components/Button";
import { cancelAccountOrder, getAccountOrder } from "@/lib/api/account";
import { ApiRequestError } from "@/lib/api/client";
import { formatTHB } from "@/lib/format";
import type { Order } from "@/lib/types/api";

export default function AccountOrderDetail({ publicId }: { publicId: string }) {
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    void getAccountOrder(publicId).then(setOrder).catch((caught) => setError(caught instanceof ApiRequestError ? caught.message : "Order could not be loaded."));
  }, [publicId]);
  async function cancelOrder() {
    if (!order || !window.confirm(order.status === "confirmed" ? "Cancel this order and issue a full refund?" : "Cancel this unpaid order?")) return;
    setBusy(true); setError("");
    try { setOrder(await cancelAccountOrder(order.public_id)); }
    catch (caught) { setError(caught instanceof ApiRequestError ? caught.message : "Order cancellation failed."); }
    finally { setBusy(false); }
  }
  if (error && !order) return <div className="rounded-xl border bg-card p-8"><h1 className="text-2xl font-bold">Order unavailable</h1><p className="mt-3 text-muted-foreground" role="alert">{error}</p><Link className="mt-5 inline-block text-primary underline" href="/account">Back to account</Link></div>;
  if (!order) return <p className="rounded-xl border bg-card p-8" role="status">Loading order…</p>;
  return <section className="mx-auto max-w-3xl rounded-xl border bg-card p-6 sm:p-8"><Link className="text-sm text-primary underline" href="/account">← Back to account</Link><h1 className="mt-5 text-3xl font-bold">Order details</h1><p className="mt-2 break-all text-sm text-muted-foreground">{order.public_id}</p><dl className="mt-6 grid gap-4 rounded-lg border p-4 sm:grid-cols-3"><div><dt className="text-xs text-muted-foreground">Status</dt><dd className="font-semibold capitalize">{order.status.replaceAll("_", " ")}</dd></div><div><dt className="text-xs text-muted-foreground">Placed</dt><dd className="font-semibold">{new Intl.DateTimeFormat("en-TH", { dateStyle: "medium" }).format(new Date(order.created_at))}</dd></div><div><dt className="text-xs text-muted-foreground">Total</dt><dd className="font-semibold">{formatTHB(order.total)}</dd></div></dl>{error ? <p className="mt-4 rounded-md bg-destructive/10 p-4 text-sm text-destructive" role="alert">{error}</p> : null}<h2 className="mt-8 text-xl font-semibold">Items</h2><div className="mt-3 divide-y rounded-lg border">{order.items.map((item) => <div className="flex justify-between gap-4 p-4" key={item.sku}><span><span className="block font-medium">{item.product_name}</span><span className="text-sm text-muted-foreground">{item.option_name} · Qty {item.quantity}</span></span><span className="font-semibold">{formatTHB(item.line_total)}</span></div>)}</div><h2 className="mt-8 text-xl font-semibold">Delivery address</h2><address className="mt-3 not-italic text-sm leading-6 text-muted-foreground">{order.shipping_address.full_name}<br />{order.shipping_address.address_line_1}<br />{order.shipping_address.address_line_2 ? <>{order.shipping_address.address_line_2}<br /></> : null}{order.shipping_address.subdistrict}, {order.shipping_address.district}<br />{order.shipping_address.province} {order.shipping_address.postal_code}<br />{order.shipping_address.phone}</address>{order.status === "awaiting_payment" || order.status === "confirmed" ? <div className="mt-8 border-t pt-6"><Button variant="outline" disabled={busy} onClick={() => void cancelOrder()}>{busy ? "Cancelling…" : order.status === "confirmed" ? "Cancel and refund" : "Cancel order"}</Button></div> : null}</section>;
}
