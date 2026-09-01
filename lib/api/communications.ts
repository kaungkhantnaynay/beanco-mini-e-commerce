import { apiRequest } from "@/lib/api/client";
import type {
  NewsletterSubscriptionInput,
  PartnershipInquiryInput,
  SubmissionResponse,
} from "@/lib/types/api";

export function createPartnershipInquiry(
  input: PartnershipInquiryInput,
): Promise<SubmissionResponse> {
  return apiRequest<SubmissionResponse>("inquiries/", {
    method: "POST",
    body: JSON.stringify(input),
    cache: "no-store",
  });
}

export function createNewsletterSubscription(
  input: NewsletterSubscriptionInput,
): Promise<SubmissionResponse> {
  return apiRequest<SubmissionResponse>("newsletter/subscriptions/", {
    method: "POST",
    body: JSON.stringify(input),
    cache: "no-store",
  });
}
