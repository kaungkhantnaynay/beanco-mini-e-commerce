import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import NewsletterForm from "@/components/NewsletterForm";

describe("NewsletterForm", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("submits consent and shows the privacy-safe response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "If eligible, this address is subscribed." }), {
        status: 202,
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<NewsletterForm />);
    const user = userEvent.setup();

    await user.type(screen.getByLabelText("Email address"), "news@example.test");
    await user.click(screen.getByRole("checkbox", { name: /receive BeanCo updates/i }));
    await user.click(screen.getByRole("button", { name: "Subscribe" }));

    const request = fetchMock.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(request.body))).toEqual({
      email: "news@example.test",
      consent: true,
      consent_source: "storefront_footer",
      website: "",
    });
    expect(await screen.findByRole("status")).toHaveTextContent(
      "If eligible, this address is subscribed.",
    );
  });
});
