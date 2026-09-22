import { describe, expect, it } from "vitest";

import { SUPPORT_CLIENT_TIMEOUT_MS } from "@/lib/config/support-timeouts";

describe("support API client", () => {
  it("waits longer than the server proxy during a free-tier cold start", () => {
    expect(SUPPORT_CLIENT_TIMEOUT_MS).toBe(95_000);
  });
});
