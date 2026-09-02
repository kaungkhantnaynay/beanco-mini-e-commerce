"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import Button from "@/components/Button";
import ButtonLink from "@/components/ButtonLink";
import FieldError from "@/components/FieldError";
import { createOrder, getCart, previewCheckout } from "@/lib/api/commerce";
import { ApiRequestError } from "@/lib/api/client";
import { formatTHB } from "@/lib/format";
import type { ApiFieldErrors, Cart, CheckoutPreview, OrderCreateInput, ShippingAddress } from "@/lib/types/api";

const inputClass =
  "h-11 w-full rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2";

const initialAddress: ShippingAddress = {
  full_name: "",
  phone: "",
  address_line_1: "",
  address_line_2: "",
  subdistrict: "",
  district: "",
  province: "",
  postal_code: "",
  country_code: "TH",
};

type AddressField = Exclude<keyof ShippingAddress, "country_code">;

const addressFields: Array<{
  name: AddressField;
  label: string;
  autoComplete: string;
  optional?: boolean;
  inputMode?: "text" | "tel" | "numeric";
}> = [
  { name: "full_name", label: "Full name", autoComplete: "name" },
  { name: "phone", label: "Phone", autoComplete: "tel", inputMode: "tel" },
  { name: "address_line_1", label: "Address", autoComplete: "address-line1" },
  { name: "address_line_2", label: "Apartment, suite, etc.", autoComplete: "address-line2", optional: true },
  { name: "subdistrict", label: "Subdistrict", autoComplete: "address-level3" },
  { name: "district", label: "District", autoComplete: "address-level2" },
  { name: "province", label: "Province", autoComplete: "address-level1" },
  { name: "postal_code", label: "Postal code", autoComplete: "postal-code", inputMode: "numeric" },
];

function newIdempotencyKey() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `beanco-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function addressErrors(fields: ApiFieldErrors): Partial<Record<AddressField, string[]>> {
  const nested = (fields as unknown as Record<string, unknown>).shipping_address;
  if (!nested || typeof nested !== "object" || Array.isArray(nested)) return {};
  return nested as Partial<Record<AddressField, string[]>>;
}

export default function CheckoutFlow() {
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState(initialAddress);
  const [preview, setPreview] = useState<CheckoutPreview | null>(null);
  const [fields, setFields] = useState<ApiFieldErrors>({});
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [isOrdering, setIsOrdering] = useState(false);
  const idempotencyKey = useRef("");

  const loadCart = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      setCart(await getCart());
    } catch (caught) {
      setError(caught instanceof ApiRequestError ? caught.message : "We could not load your cart.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCart();
  }, [loadCart]);

  function invalidatePreview() {
    setPreview(null);
    setFields({});
    setError("");
    idempotencyKey.current = "";
  }

  async function handlePreview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isPreviewing || isOrdering) return;
    setIsPreviewing(true);
    setFields({});
    setError("");
    try {
      const result = await previewCheckout({ shipping_address: address, shipping_method: "standard_th" });
      setPreview(result);
      setCart(result.cart);
      idempotencyKey.current = newIdempotencyKey();
    } catch (caught) {
      if (caught instanceof ApiRequestError) {
        setFields(caught.fields);
        setError(caught.message);
      } else {
        setError("We could not review your order. Please try again.");
      }
    } finally {
      setIsPreviewing(false);
    }
  }

  async function handleOrder() {
    if (!preview || isOrdering) return;
    setIsOrdering(true);
    setFields({});
    setError("");
    const key = idempotencyKey.current || newIdempotencyKey();
    idempotencyKey.current = key;
    const input: OrderCreateInput = {
      customer_email: email,
      shipping_address: preview.shipping_address,
      shipping_method: "standard_th",
    };
    try {
      const order = await createOrder(input, key);
      router.push(`/orders/${order.public_id}`);
    } catch (caught) {
      if (caught instanceof ApiRequestError) {
        setFields(caught.fields);
        setError(caught.message);
      } else {
        setError("We could not create your order. You can safely try again.");
      }
      setIsOrdering(false);
    }
  }

  if (isLoading) {
    return <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground" role="status">Loading checkout…</div>;
  }

  if (!cart) {
    return (
      <div className="rounded-xl border bg-card p-8 text-center">
        <h2 className="text-xl font-semibold">Checkout could not be loaded</h2>
        <p className="mt-2 text-sm text-muted-foreground">{error}</p>
        <Button type="button" className="mt-5" onClick={() => void loadCart()}>Try again</Button>
      </div>
    );
  }

  if (!cart.items.length) {
    return (
      <div className="rounded-xl border bg-card p-8 text-center shadow-sm">
        <h2 className="text-xl font-semibold">Your cart is empty</h2>
        <p className="mt-2 text-sm text-muted-foreground">Add something from the collection before checking out.</p>
        <ButtonLink href="/products" className="mt-6">Browse collection</ButtonLink>
      </div>
    );
  }

  const nestedErrors = addressErrors(fields);

  return (
    <form className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem]" onSubmit={(event) => void handlePreview(event)} noValidate>
      <div className="space-y-8">
        <section className="rounded-xl border bg-card p-6 shadow-sm" aria-labelledby="contact-heading">
          <h2 id="contact-heading" className="text-xl font-semibold">Contact</h2>
          <div className="mt-5 space-y-2">
            <label htmlFor="customer_email" className="text-sm font-medium">Email</label>
            <input
              id="customer_email"
              className={inputClass}
              type="email"
              autoComplete="email"
              required
              value={email}
              aria-describedby={fields.customer_email ? "customer_email-error" : undefined}
              onChange={(event) => { setEmail(event.target.value); invalidatePreview(); }}
            />
            <FieldError id="customer_email-error" messages={fields.customer_email} />
            <p className="text-xs text-muted-foreground">We’ll use this for your order receipt and updates.</p>
          </div>
        </section>

        <section className="rounded-xl border bg-card p-6 shadow-sm" aria-labelledby="delivery-heading">
          <h2 id="delivery-heading" className="text-xl font-semibold">Delivery address</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {addressFields.map((field) => (
              <div key={field.name} className={`space-y-2 ${field.name.startsWith("address_line") ? "sm:col-span-2" : ""}`}>
                <label htmlFor={field.name} className="text-sm font-medium">
                  {field.label}{field.optional ? <span className="font-normal text-muted-foreground"> (optional)</span> : null}
                </label>
                <input
                  id={field.name}
                  className={inputClass}
                  type="text"
                  inputMode={field.inputMode}
                  autoComplete={field.autoComplete}
                  required={!field.optional}
                  value={address[field.name]}
                  aria-describedby={nestedErrors[field.name] ? `${field.name}-error` : undefined}
                  onChange={(event) => {
                    setAddress((current) => ({ ...current, [field.name]: event.target.value }));
                    invalidatePreview();
                  }}
                />
                <FieldError id={`${field.name}-error`} messages={nestedErrors[field.name]} />
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-md bg-muted p-4 text-sm">
            <p className="font-medium">Thailand</p>
            <p className="mt-1 text-muted-foreground">Standard delivery · 3–5 business days</p>
          </div>
          <FieldError id="shipping_method-error" messages={fields.shipping_method} />
        </section>
      </div>

      <aside className="h-fit rounded-xl border bg-card p-6 shadow-sm lg:sticky lg:top-24" aria-labelledby="checkout-summary-heading">
        <h2 id="checkout-summary-heading" className="text-lg font-semibold">Order summary</h2>
        <ul className="mt-5 space-y-4 border-b pb-5">
          {cart.items.map((item) => (
            <li key={item.public_id} className="flex justify-between gap-4 text-sm">
              <span><span className="font-medium">{item.product_name}</span><span className="block text-muted-foreground">{item.option_name || item.variant_sku} × {item.quantity}</span></span>
              <span className="font-medium">{formatTHB(item.line_total)}</span>
            </li>
          ))}
        </ul>
        <dl className="mt-5 space-y-3 text-sm">
          <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Subtotal</dt><dd>{formatTHB(cart.subtotal)}</dd></div>
          <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Delivery</dt><dd>{cart.shipping_total === "0.00" ? "Free" : formatTHB(cart.shipping_total)}</dd></div>
          <div className="flex justify-between gap-4"><dt className="text-muted-foreground">Additional tax</dt><dd>{formatTHB(cart.tax_total)}</dd></div>
          <div className="flex justify-between gap-4 border-t pt-4 text-base font-semibold"><dt>Total</dt><dd>{formatTHB(cart.total)}</dd></div>
        </dl>

        {error ? <p className="commerce-status mt-4 rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">{error}</p> : null}
        <FieldError id="cart-error" messages={fields.cart} />

        {!preview ? (
          <Button type="submit" size="lg" className="mt-6 w-full" disabled={isPreviewing} aria-busy={isPreviewing}>
            {isPreviewing ? "Reviewing…" : "Review order"}
          </Button>
        ) : (
          <div className="commerce-status mt-6">
            <div className="rounded-md bg-secondary p-4 text-sm text-secondary-foreground" role="status">
              <p className="font-semibold">Address and availability confirmed</p>
              <p className="mt-1">{preview.shipping_method.name} · {preview.shipping_method.minimum_business_days}–{preview.shipping_method.maximum_business_days} business days</p>
            </div>
            <Button type="button" size="lg" className="mt-4 w-full" disabled={isOrdering} aria-busy={isOrdering} onClick={() => void handleOrder()}>
              {isOrdering ? "Placing order…" : `Place order · ${formatTHB(preview.cart.total)}`}
            </Button>
          </div>
        )}
        <p className="mt-3 text-xs leading-relaxed text-muted-foreground">Placing the order reserves stock for 30 minutes while you complete secure Stripe payment.</p>
        <Link href="/cart" className="mt-4 inline-block text-sm font-semibold text-primary underline-offset-4 hover:underline">Return to cart</Link>
      </aside>
    </form>
  );
}
