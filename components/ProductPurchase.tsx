"use client";

import Link from "next/link";
import { ShoppingBag } from "lucide-react";
import { useMemo, useState } from "react";
import Button from "@/components/Button";
import { addCartItem } from "@/lib/api/commerce";
import { ApiRequestError } from "@/lib/api/client";
import { formatTHB } from "@/lib/format";
import type { ProductVariant } from "@/lib/types/api";

const selectClass =
  "h-11 w-full rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

export default function ProductPurchase({
  productName,
  variants,
}: {
  productName: string;
  variants: ProductVariant[];
}) {
  const availableVariants = useMemo(() => variants.filter((variant) => variant.available), [variants]);
  const [selectedSku, setSelectedSku] = useState(availableVariants[0]?.sku ?? "");
  const [quantity, setQuantity] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{ kind: "success" | "error"; message: string } | null>(null);
  const selectedVariant = availableVariants.find((variant) => variant.sku === selectedSku);

  async function handleAddToCart() {
    if (!selectedVariant || isSubmitting) return;
    setIsSubmitting(true);
    setResult(null);
    try {
      const cart = await addCartItem(selectedVariant.sku, quantity);
      setResult({
        kind: "success",
        message: `${quantity} × ${productName} added. Cart total ${formatTHB(cart.total)}.`,
      });
    } catch (error) {
      setResult({
        kind: "error",
        message:
          error instanceof ApiRequestError
            ? error.message
            : "We could not add this product. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!availableVariants.length) {
    return (
      <div className="rounded-xl border bg-muted/50 p-5 text-sm text-muted-foreground">
        Retail purchase options are currently unavailable. Contact us for future availability.
      </div>
    );
  }

  return (
    <section className="rounded-xl border bg-card p-5 shadow-sm" aria-labelledby="purchase-heading">
      <h2 id="purchase-heading" className="text-lg font-semibold text-card-foreground">
        Add to cart
      </h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-[minmax(0,1fr)_7rem]">
        <div className="space-y-2">
          <label htmlFor="variant" className="text-sm font-medium">
            Option
          </label>
          <select
            id="variant"
            className={selectClass}
            value={selectedSku}
            onChange={(event) => {
              setSelectedSku(event.target.value);
              setResult(null);
            }}
          >
            {availableVariants.map((variant) => (
              <option key={variant.sku} value={variant.sku}>
                {variant.option_name || variant.sku} — {formatTHB(variant.price)}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <label htmlFor="quantity" className="text-sm font-medium">
            Quantity
          </label>
          <input
            id="quantity"
            className={selectClass}
            type="number"
            inputMode="numeric"
            min={1}
            max={Math.min(99, selectedVariant?.available_quantity ?? 1)}
            value={quantity}
            onChange={(event) => {
              const next = Number(event.target.value);
              setQuantity(Number.isFinite(next) ? Math.max(1, Math.min(99, next)) : 1);
              setResult(null);
            }}
          />
        </div>
      </div>
      <p className="mt-3 text-xs text-muted-foreground">
        {selectedVariant?.available_quantity ?? 0} currently available. Price and stock are
        confirmed again at checkout.
      </p>

      {result ? (
        <div
          className={
            result.kind === "success"
              ? "commerce-status mt-4 rounded-md bg-secondary px-4 py-3 text-sm text-secondary-foreground"
              : "commerce-status mt-4 rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive"
          }
          role={result.kind === "error" ? "alert" : "status"}
          aria-live="polite"
        >
          {result.message}
          {result.kind === "success" ? (
            <Link href="/cart" className="ml-2 font-semibold underline underline-offset-4">
              View cart
            </Link>
          ) : null}
        </div>
      ) : null}

      <Button
        type="button"
        size="lg"
        className="mt-5 w-full"
        disabled={isSubmitting || !selectedVariant}
        aria-busy={isSubmitting}
        onClick={() => void handleAddToCart()}
      >
        <ShoppingBag className="mr-2 h-5 w-5" aria-hidden="true" />
        {isSubmitting ? "Adding…" : "Add to cart"}
      </Button>
    </section>
  );
}
