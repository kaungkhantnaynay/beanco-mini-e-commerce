import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "@/app/api/support/chat/route";

describe("support chat proxy", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("keeps the support service URL on the server and forwards conversation credentials", async () => {
    vi.stubEnv("SUPPORT_API_BASE_URL", "http://support.internal:8001/");
    vi.stubEnv("SUPPORT_API_TOKEN", "shared-test-token");
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({
      conversation_id: 4,
      conversation_token: "fictional-token",
      message_id: 8,
      ticket_id: null,
      answer: "Grounded answer",
      citations: [],
      confidence: "high",
      needs_escalation: false,
      escalation_reason: null,
    }), { status: 200, headers: { "Content-Type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await POST(new Request("http://localhost/api/support/chat", {
      method: "POST",
      body: JSON.stringify({
        message: "Can I cancel it?",
        conversation_id: 4,
        conversation_token: "fictional-token",
      }),
    }));

    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://support.internal:8001/chat",
      expect.objectContaining({
        method: "POST",
        cache: "no-store",
        headers: expect.objectContaining({ "X-Support-Token": "shared-test-token" }),
      }),
    );
    expect(await response.json()).toEqual(expect.objectContaining({ answer: "Grounded answer" }));
  });

  it("fails safely when support is not configured", async () => {
    vi.stubEnv("SUPPORT_API_BASE_URL", "");
    vi.stubEnv("SUPPORT_API_TOKEN", "");
    const response = await POST(new Request("http://localhost/api/support/chat", {
      method: "POST",
      body: JSON.stringify({ message: "Where is my order?" }),
    }));

    expect(response.status).toBe(503);
    await expect(response.json()).resolves.toEqual(expect.objectContaining({
      code: "support_not_configured",
    }));
  });

  it("fails safely when the server-only support token is missing", async () => {
    vi.stubEnv("SUPPORT_API_BASE_URL", "https://support.example.com");
    vi.stubEnv("SUPPORT_API_TOKEN", "");

    const response = await POST(new Request("http://localhost/api/support/chat", {
      method: "POST",
      body: JSON.stringify({ message: "Where is my order?" }),
    }));

    expect(response.status).toBe(503);
    await expect(response.json()).resolves.toEqual(expect.objectContaining({
      code: "support_not_configured",
    }));
  });
});
