"use client";

import { useState, type FormEvent } from "react";
import Button from "@/components/Button";
import FieldError from "@/components/FieldError";
import { createPartnershipInquiry } from "@/lib/api/communications";
import { ApiRequestError } from "@/lib/api/client";
import type { ApiFieldErrors, InquiryType } from "@/lib/types/api";

const inputClass =
  "flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

export default function ContactForm() {
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
    void submitInquiry(form, data);
  }

  async function submitInquiry(form: HTMLFormElement, data: FormData) {
    try {
      const response = await createPartnershipInquiry({
        name: String(data.get("name") ?? ""),
        email: String(data.get("email") ?? ""),
        phone: String(data.get("phone") ?? ""),
        company: String(data.get("company") ?? ""),
        inquiry_type: String(data.get("inquiry_type") ?? "other") as InquiryType,
        requirements: String(data.get("requirements") ?? ""),
        consent: data.get("consent") === "on",
        website: String(data.get("website") ?? ""),
      });
      form.reset();
      setResult({ kind: "success", message: response.detail });
    } catch (error) {
      if (error instanceof ApiRequestError) {
        setFieldErrors(error.fields);
        setResult({ kind: "error", message: error.message });
      } else {
        setResult({ kind: "error", message: "We could not send your inquiry. Please try again." });
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      <div className="grid gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="name" className="text-sm font-medium">Name</label>
          <input className={`${inputClass} h-10`} id="name" name="name" autoComplete="name" required aria-describedby="name-error" />
          <FieldError id="name-error" messages={fieldErrors.name} />
        </div>
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">Email</label>
          <input className={`${inputClass} h-10`} id="email" name="email" type="email" autoComplete="email" required aria-describedby="email-error" />
          <FieldError id="email-error" messages={fieldErrors.email} />
        </div>
        <div className="space-y-2">
          <label htmlFor="company" className="text-sm font-medium">Company <span className="text-muted-foreground">(optional)</span></label>
          <input className={`${inputClass} h-10`} id="company" name="company" autoComplete="organization" aria-describedby="company-error" />
          <FieldError id="company-error" messages={fieldErrors.company} />
        </div>
        <div className="space-y-2">
          <label htmlFor="phone" className="text-sm font-medium">Phone <span className="text-muted-foreground">(optional)</span></label>
          <input className={`${inputClass} h-10`} id="phone" name="phone" type="tel" autoComplete="tel" aria-describedby="phone-error" />
          <FieldError id="phone-error" messages={fieldErrors.phone} />
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="inquiry_type" className="text-sm font-medium">Inquiry type</label>
        <select className={`${inputClass} h-10`} id="inquiry_type" name="inquiry_type" defaultValue="hospitality" aria-describedby="inquiry-type-error">
          <option value="hospitality">Hospitality</option>
          <option value="office">Office</option>
          <option value="event">Event</option>
          <option value="wholesale">Wholesale</option>
          <option value="other">Other</option>
        </select>
        <FieldError id="inquiry-type-error" messages={fieldErrors.inquiry_type} />
      </div>

      <div className="space-y-2">
        <label htmlFor="requirements" className="text-sm font-medium">Project details</label>
        <textarea
          className={`${inputClass} min-h-32 resize-y`}
          id="requirements"
          name="requirements"
          required
          minLength={20}
          aria-describedby="requirements-help requirements-error"
          placeholder="Tell us about volume, location, timeline, and the coffee experience you want to create."
        />
        <p id="requirements-help" className="text-xs text-muted-foreground">Please provide at least 20 characters.</p>
        <FieldError id="requirements-error" messages={fieldErrors.requirements} />
      </div>

      <div className="hidden" aria-hidden="true">
        <label htmlFor="website" className="hidden">Website</label>
        <input id="website" name="website" type="text" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden="true" />
      </div>

      <div className="space-y-2">
        <label className="flex items-start gap-3 text-sm text-muted-foreground">
          <input type="checkbox" name="consent" required className="mt-0.5 h-4 w-4 accent-primary" aria-describedby="consent-error" />
          <span>I agree that BeanCo may use these details to respond to this partnership inquiry.</span>
        </label>
        <FieldError id="consent-error" messages={fieldErrors.consent} />
      </div>

      {result ? (
        <p
          className={result.kind === "success" ? "rounded-md bg-secondary px-4 py-3 text-sm text-secondary-foreground" : "rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive"}
          role={result.kind === "error" ? "alert" : "status"}
          aria-live="polite"
        >
          {result.message}
        </p>
      ) : null}

      <Button type="submit" className="w-full" disabled={isSubmitting} aria-busy={isSubmitting}>
        {isSubmitting ? "Sending…" : "Send inquiry"}
      </Button>
    </form>
  );
}
