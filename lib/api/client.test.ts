import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError, apiRequest } from "@/lib/api/client";

describe("apiRequest", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("maps successful JSON responses through the configured public API", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1/");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Accepted" }), {
        status: 202,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiRequest<{ detail: string }>("newsletter/subscriptions/"))
      .resolves.toEqual({ detail: "Accepted" });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/newsletter/subscriptions/",
      expect.objectContaining({ headers: expect.objectContaining({ Accept: "application/json" }) }),
    );
  });

  it("normalizes API validation errors", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            code: "validation_error",
            detail: "One or more fields are invalid.",
            fields: { email: ["Enter a valid email address."] },
          }),
          { status: 400 },
        ),
      ),
    );

    const error = await apiRequest("inquiries/", { method: "POST" }).catch((caught) => caught);

    expect(error).toBeInstanceOf(ApiRequestError);
    expect(error).toMatchObject({
      code: "validation_error",
      status: 400,
      fields: { email: ["Enter a valid email address."] },
    });
  });
});
