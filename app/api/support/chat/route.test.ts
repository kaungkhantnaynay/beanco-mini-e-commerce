import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "@/app/api/support/chat/route";

describe("support chat proxy", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("keeps the support service URL on the server and forwards conversation credentials", async () => {
    vi.stubEnv("SUPPORT_API_BASE_URL", "http://support.internal:8001/");
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
      expect.objectContaining({ method: "POST", cache: "no-store" }),
    );
    expect(await response.json()).toEqual(expect.objectContaining({ answer: "Grounded answer" }));
  });

  it("fails safely when support is not configured", async () => {
    vi.stubEnv("SUPPORT_API_BASE_URL", "");
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
