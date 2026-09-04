import { beforeEach, describe, expect, it, vi } from "vitest";
import { login, logout } from "@/lib/api/account";

describe("account API", () => {
  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://api.example.test/api/v1";
    document.cookie = "beanco_csrftoken=fictional-csrf-token; path=/";
    vi.restoreAllMocks();
  });

  it("uses credentialed CSRF-protected session requests without browser token storage", async () => {
    const storageSpy = vi.spyOn(Storage.prototype, "setItem");
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "CSRF cookie set." })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ email: "buyer@example.test", first_name: "", last_name: "", email_verified: true })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "CSRF cookie set." })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Signed out." })));

    await login("buyer@example.test", "not-stored-password");
    await logout();

    expect(fetchMock.mock.calls[1][1]).toEqual(expect.objectContaining({
      credentials: "include",
      method: "POST",
      headers: expect.objectContaining({ "X-CSRFToken": "fictional-csrf-token" }),
    }));
    expect(storageSpy).not.toHaveBeenCalled();
  });
});
