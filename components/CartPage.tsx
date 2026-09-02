"use client";

import Link from "next/link";
import { Minus, Plus, ShoppingBag, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import Button from "@/components/Button";
import ButtonLink from "@/components/ButtonLink";
import { getCart, removeCartItem, updateCartItem } from "@/lib/api/commerce";
import { ApiRequestError } from "@/lib/api/client";
import { formatTHB } from "@/lib/format";
import type { Cart } from "@/lib/types/api";

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pendingItem, setPendingItem] = useState<string | null>(null);
  const [error, setError] = useState("");

  const loadCart = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      setCart(await getCart());
    } catch (caught) {
      setError(
        caught instanceof ApiRequestError
          ? caught.message
          : "We could not load your cart. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCart();
  }, [loadCart]);

  async function changeQuantity(publicId: string, quantity: number) {
    if (pendingItem || quantity < 1 || quantity > 99) return;
    setPendingItem(publicId);
    setError("");
    try {
      setCart(await updateCartItem(publicId, quantity));
    } catch (caught) {
      setError(
        caught instanceof ApiRequestError
          ? caught.message
          : "We could not update that item. Please try again.",
      );
    } finally {
      setPendingItem(null);
    }
  }

  async function removeItem(publicId: string) {
    if (pendingItem) return;
    setPendingItem(publicId);
    setError("");
    try {
      await removeCartItem(publicId);
      setCart(await getCart());
    } catch (caught) {
      setError(
        caught instanceof ApiRequestError
          ? caught.message
          : "We could not remove that item. Please try again.",
      );
    } finally {
      setPendingItem(null);
    }
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border bg-card p-8 text-center" role="status">
        <p className="text-sm text-muted-foreground">Loading your cart…</p>
      </div>
    );
  }

  if (!cart) {
    return (
      <div className="rounded-xl border bg-card p-8 text-center">
        <h2 className="text-xl font-semibold">Your cart could not be loaded</h2>
        <p className="mt-2 text-sm text-muted-foreground">{error}</p>
        <Button type="button" className="mt-5" onClick={() => void loadCart()}>
          Try again
        </Button>
      </div>
    );
  }

  if (!cart.items.length) {
    return (
      <div className="rounded-xl border bg-card p-8 text-center shadow-sm">
        <ShoppingBag className="mx-auto h-9 w-9 text-primary" aria-hidden="true" />
        <h2 className="mt-4 text-xl font-semibold">Your cart is empty</h2>
        <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
          Explore the collection and choose an available size or grind to begin your order.
        </p>
        <ButtonLink href="/products" className="mt-6">
          Browse collection
        </ButtonLink>
      </div>
    );
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <section aria-labelledby="cart-items-heading">
        <h2 id="cart-items-heading" className="sr-only">
          Cart items
        </h2>
        <ul className="space-y-4">
          {cart.items.map((item) => {
            const isPending = pendingItem === item.public_id;
            return (
              <li key={item.public_id} className="rounded-xl border bg-card p-5 shadow-sm">
                <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <h3 className="font-semibold text-card-foreground">{item.product_name}</h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {item.option_name || item.variant_sku}
                    </p>
                    <p className="mt-2 text-sm font-medium text-primary">
                      {formatTHB(item.unit_price)} each
                    </p>
                  </div>
                  <div className="flex flex-wrap items-center justify-between gap-4 sm:justify-end">
                    <div className="inline-flex items-center rounded-md border" aria-label="Quantity controls">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-10 w-10 px-0"
                        disabled={isPending || item.quantity <= 1}
                        aria-label={`Decrease ${item.product_name} quantity`}
                        onClick={() => void changeQuantity(item.public_id, item.quantity - 1)}
                      >
                        <Minus className="h-4 w-4" aria-hidden="true" />
                      </Button>
                      <output
                        className="min-w-10 text-center text-sm font-semibold"
                        aria-label={`${item.product_name} quantity`}
                      >
                        {isPending ? "…" : item.quantity}
                      </output>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-10 w-10 px-0"
                        disabled={isPending || item.quantity >= 99}
                        aria-label={`Increase ${item.product_name} quantity`}
                        onClick={() => void changeQuantity(item.public_id, item.quantity + 1)}
                      >
                        <Plus className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    </div>
                    <p className="min-w-24 text-right font-semibold">{formatTHB(item.line_total)}</p>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                      disabled={isPending}
                      aria-label={`Remove ${item.product_name} from cart`}
                      onClick={() => void removeItem(item.public_id)}
                    >
                      <Trash2 className="h-4 w-4" aria-hidden="true" />
                    </Button>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
        {error ? (
          <p className="commerce-status mt-4 rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}
        <Link href="/products" className="mt-5 inline-block text-sm font-semibold text-primary underline-offset-4 hover:underline">
          Continue shopping
        </Link>
      </section>

      <aside className="h-fit rounded-xl border bg-card p-6 shadow-sm" aria-labelledby="summary-heading">
        <h2 id="summary-heading" className="text-lg font-semibold">Order summary</h2>
        <dl className="mt-5 space-y-3 text-sm">
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Subtotal</dt>
            <dd>{formatTHB(cart.subtotal)}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Standard delivery</dt>
            <dd>{cart.shipping_total === "0.00" ? "Free" : formatTHB(cart.shipping_total)}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Additional tax</dt>
            <dd>{formatTHB(cart.tax_total)}</dd>
          </div>
          <div className="flex justify-between gap-4 border-t pt-4 text-base font-semibold">
            <dt>Total</dt>
            <dd>{formatTHB(cart.total)}</dd>
          </div>
        </dl>
        <ButtonLink href="/checkout" size="lg" className="mt-6 w-full">
          Continue to checkout
        </ButtonLink>
        <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
          Current prices and stock are confirmed again before your order is created.
        </p>
      </aside>
    </div>
  );
}
