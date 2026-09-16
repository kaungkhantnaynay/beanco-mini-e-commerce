import { NextResponse } from "next/server";

const SUPPORT_TIMEOUT_MS = 12_000;

type SupportProxyRequest = {
  message?: unknown;
  conversation_id?: unknown;
  conversation_token?: unknown;
};

function supportApiUrl(): string | null {
  const configured = process.env.SUPPORT_API_BASE_URL?.trim();
  return configured ? `${configured.replace(/\/+$/, "")}/chat` : null;
}

function invalidRequest(body: SupportProxyRequest): string | null {
  if (typeof body.message !== "string" || body.message.trim().length < 2) {
    return "Enter at least two characters so support can understand the question.";
  }
  if (body.message.length > 2000) return "Support messages cannot exceed 2,000 characters.";
  if (
    body.conversation_id !== undefined
    && (!Number.isInteger(body.conversation_id) || Number(body.conversation_id) < 1)
  ) {
    return "The support conversation is invalid. Start a new chat.";
  }
  if (
    body.conversation_token !== undefined
    && (typeof body.conversation_token !== "string" || body.conversation_token.length > 128)
  ) {
    return "The support conversation is invalid. Start a new chat.";
  }
  return null;
}

export async function POST(request: Request) {
  const url = supportApiUrl();
  if (!url) {
    return NextResponse.json(
      { code: "support_not_configured", detail: "BeanCO support is not configured yet." },
      { status: 503 },
    );
  }

  let body: SupportProxyRequest;
  try {
    body = await request.json() as SupportProxyRequest;
  } catch {
    return NextResponse.json(
      { code: "invalid_json", detail: "The support request was not valid JSON." },
      { status: 400 },
    );
  }

  const detail = invalidRequest(body);
  if (detail) {
    return NextResponse.json({ code: "invalid_request", detail }, { status: 422 });
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), SUPPORT_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => null);
    if (!payload) {
      return NextResponse.json(
        { code: "support_invalid_response", detail: "BeanCO support returned an invalid response." },
        { status: 502 },
      );
    }
    return NextResponse.json(payload, {
      status: response.status >= 500 ? 502 : response.status,
    });
  } catch {
    return NextResponse.json(
      { code: "support_unavailable", detail: "BeanCO support is temporarily unavailable." },
      { status: 502 },
    );
  } finally {
    clearTimeout(timeout);
  }
}
