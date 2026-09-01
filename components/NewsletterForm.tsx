"use client";

import { useState, type FormEvent } from "react";
import FieldError from "@/components/FieldError";
import { createNewsletterSubscription } from "@/lib/api/communications";
import { ApiRequestError } from "@/lib/api/client";
import type { ApiFieldErrors } from "@/lib/types/api";

export default function NewsletterForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<ApiFieldErrors>({});
  const [result, setResult] = useState<{ kind: "success" | "error"; message: string } | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmitting) return;

    const form = event.currentTarget;
    const data = new FormData(form);
    setIsSubmitting(true);
    setFieldErrors({});
    setResult(null);
    void submitSubscription(form, data);
  }

  async function submitSubscription(form: HTMLFormElement, data: FormData) {
    try {
      const response = await createNewsletterSubscription({
        email: String(data.get("newsletter_email") ?? ""),
        consent: data.get("newsletter_consent") === "on",
        consent_source: "storefront_footer",
        website: String(data.get("newsletter_website") ?? ""),
      });
      form.reset();
      setResult({ kind: "success", message: response.detail });
    } catch (error) {
      if (error instanceof ApiRequestError) {
        setFieldErrors(error.fields);
        setResult({ kind: "error", message: error.message });
      } else {
        setResult({ kind: "error", message: "We could not subscribe this address. Please try again." });
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3" noValidate>
      <div className="flex gap-2">
        <label htmlFor="newsletter_email" className="sr-only">Email address</label>
        <input
          id="newsletter_email"
          name="newsletter_email"
          type="email"
          autoComplete="email"
          required
          placeholder="Enter your email"
          aria-describedby="newsletter-email-error"
          className="min-w-0 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
        <button
          type="submit"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
          className="rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground transition-[background-color,transform] duration-150 active:scale-[0.97] motion-reduce:transform-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
        >
          {isSubmitting ? "Joining…" : "Subscribe"}
        </button>
      </div>
      <FieldError id="newsletter-email-error" messages={fieldErrors.email} />
      <label className="flex items-start gap-2 text-xs text-muted-foreground">
        <input
          type="checkbox"
          name="newsletter_consent"
          required
          className="mt-0.5 h-3.5 w-3.5 accent-primary"
          aria-describedby="newsletter-consent-error"
        />
        <span>I agree to receive BeanCo updates.</span>
      </label>
      <FieldError id="newsletter-consent-error" messages={fieldErrors.consent} />
      <div className="hidden" aria-hidden="true">
        <label htmlFor="newsletter_website" className="hidden">Website</label>
        <input id="newsletter_website" name="newsletter_website" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden="true" />
      </div>
      {result ? (
        <p
          className={result.kind === "success" ? "text-xs text-secondary-foreground" : "text-xs text-destructive"}
          role={result.kind === "error" ? "alert" : "status"}
          aria-live="polite"
        >
          {result.message}
        </p>
      ) : null}
    </form>
  );
}
