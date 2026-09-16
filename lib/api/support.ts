import type { SupportChatRequest, SupportChatResponse } from "@/lib/types/support";

const SUPPORT_TIMEOUT_MS = 15_000;

export class SupportRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SupportRequestError";
  }
}

export async function sendSupportMessage(
  input: SupportChatRequest,
): Promise<SupportChatResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), SUPPORT_TIMEOUT_MS);

  try {
    const response = await fetch("/api/support/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
      cache: "no-store",
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => null) as
      | SupportChatResponse
      | { detail?: string }
      | null;

    if (!response.ok) {
      throw new SupportRequestError(
        payload && "detail" in payload && payload.detail
          ? payload.detail
          : "BeanCO support is temporarily unavailable.",
      );
    }
    return payload as SupportChatResponse;
  } catch (error) {
    if (error instanceof SupportRequestError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new SupportRequestError("Support took too long to respond. Please try again.");
    }
    throw new SupportRequestError("BeanCO support is temporarily unavailable.");
  } finally {
    clearTimeout(timeout);
  }
}
