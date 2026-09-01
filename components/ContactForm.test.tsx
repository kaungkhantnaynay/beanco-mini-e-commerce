import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import ContactForm from "@/components/ContactForm";

async function completeForm() {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("Name"), "Arun Example");
  await user.type(screen.getByLabelText("Email"), "arun@example.test");
  await user.type(screen.getByLabelText("Company (optional)"), "Example Hotel");
  await user.type(screen.getByLabelText("Project details"), "Coffee service for a fictional hotel opening.");
  await user.click(screen.getByRole("checkbox", { name: /I agree that BeanCo/i }));
  return user;
}

describe("ContactForm", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("maps the form to the API, prevents duplicate submission, and shows success", async () => {
    let resolveRequest: ((response: Response) => void) | undefined;
    const fetchMock = vi.fn().mockReturnValue(
      new Promise<Response>((resolve) => {
        resolveRequest = resolve;
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<ContactForm />);
    const user = await completeForm();

    await user.click(screen.getByRole("button", { name: "Send inquiry" }));

    expect(screen.getByRole("button", { name: "Sending…" })).toBeDisabled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const request = fetchMock.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(request.body))).toEqual(
      expect.objectContaining({
        name: "Arun Example",
        email: "arun@example.test",
        company: "Example Hotel",
        inquiry_type: "hospitality",
        consent: true,
      }),
    );

    resolveRequest?.(
      new Response(JSON.stringify({ detail: "Your inquiry has been received." }), { status: 201 }),
    );
    expect(await screen.findByRole("status")).toHaveTextContent("Your inquiry has been received.");
  });

  it("shows field and request errors returned by the API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            code: "validation_error",
            detail: "One or more fields are invalid.",
            fields: { requirements: ["Please provide more detail."] },
          }),
          { status: 400 },
        ),
      ),
    );
    render(<ContactForm />);
    const user = await completeForm();

    await user.click(screen.getByRole("button", { name: "Send inquiry" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("One or more fields are invalid.");
    await waitFor(() => expect(screen.getByText("Please provide more detail.")).toBeVisible());
  });
});
