import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AccountAuth from "@/components/AccountAuth";
import { login, register } from "@/lib/api/account";

const push = vi.fn();
const refresh = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push, refresh }) }));
vi.mock("@/lib/api/account", () => ({
  confirmPasswordReset: vi.fn(), login: vi.fn(), register: vi.fn(),
  requestPasswordReset: vi.fn(), verifyEmail: vi.fn(),
}));

describe("AccountAuth", () => {
  beforeEach(() => { push.mockReset(); refresh.mockReset(); vi.clearAllMocks(); });

  it("signs in through the session API and opens the account", async () => {
    vi.mocked(login).mockResolvedValue({ email: "buyer@example.test", first_name: "", last_name: "", email_verified: true });
    const user = userEvent.setup(); render(<AccountAuth mode="login" />);
    await user.type(screen.getByLabelText("Email"), "buyer@example.test");
    await user.type(screen.getByLabelText("Password"), "Strong-Password-456!");
    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(login).toHaveBeenCalledWith("buyer@example.test", "Strong-Password-456!");
    expect(push).toHaveBeenCalledWith("/account");
  });

  it("shows the neutral registration response", async () => {
    vi.mocked(register).mockResolvedValue({ detail: "If registration is available for this address, check your email." });
    const user = userEvent.setup(); render(<AccountAuth mode="register" />);
    await user.type(screen.getByLabelText("Email"), "buyer@example.test");
    await user.type(screen.getByLabelText("Password"), "Strong-Password-456!");
    await user.click(screen.getByRole("button", { name: "Create your account" }));
    expect(await screen.findByRole("status")).toHaveTextContent("If registration is available");
  });
});
