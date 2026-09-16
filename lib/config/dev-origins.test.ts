import { describe, expect, it } from "vitest";

import {
  collectAllowedDevOrigins,
  getAllowedDevOrigins,
} from "./dev-origins";

describe("collectAllowedDevOrigins", () => {
  it("allows local LAN IPv4 addresses so the dev client can hydrate", () => {
    expect(
      collectAllowedDevOrigins({
        en0: [
          { address: "192.168.137.229", family: "IPv4", internal: false },
          { address: "fe80::1", family: "IPv6", internal: false },
        ],
        lo0: [{ address: "127.0.0.1", family: "IPv4", internal: true }],
      }),
    ).toEqual(["192.168.137.229"]);
  });

  it("merges, trims, and deduplicates configured hostnames", () => {
    expect(
      collectAllowedDevOrigins(
        {
          en0: [
            { address: "192.168.1.10", family: 4, internal: false },
          ],
        },
        " beanco.local,192.168.1.10, preview.internal ",
      ),
    ).toEqual(["192.168.1.10", "beanco.local", "preview.internal"]);
  });

  it("omits workstation addresses outside development", () => {
    expect(
      getAllowedDevOrigins(
        "production",
        {
          en0: [
            { address: "192.168.137.229", family: "IPv4", internal: false },
          ],
        },
        "beanco.local",
      ),
    ).toBeUndefined();
  });
});
