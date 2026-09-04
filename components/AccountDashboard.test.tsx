import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AccountDashboard from "@/components/AccountDashboard";
import { getAccount, getAccountOrders, getSavedAddresses, updateProfile } from "@/lib/api/account";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }) }));
vi.mock("@/lib/api/account", () => ({
  createSavedAddress: vi.fn(), deleteSavedAddress: vi.fn(), getAccount: vi.fn(),
  getAccountOrders: vi.fn(), getSavedAddresses: vi.fn(), logout: vi.fn(),
  updateProfile: vi.fn(), updateSavedAddress: vi.fn(),
}));

describe("AccountDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getAccount).mockResolvedValue({ email: "buyer@example.test", first_name: "Mali", last_name: "Example", email_verified: true });
    vi.mocked(getSavedAddresses).mockResolvedValue([]);
    vi.mocked(getAccountOrders).mockResolvedValue({ count: 1, next: null, previous: null, results: [{ public_id: "order-owned", status: "confirmed", currency: "THB", total: "850.00", created_at: "2026-09-02T10:00:00Z", updated_at: "2026-09-02T10:01:00Z" }] });
    vi.mocked(updateProfile).mockResolvedValue({ email: "buyer@example.test", first_name: "Mali", last_name: "Customer", email_verified: true });
  });

  it("loads owned orders and updates the customer profile", async () => {
    const user = userEvent.setup(); render(<AccountDashboard />);
    expect(await screen.findByText("buyer@example.test")).toBeVisible();
    expect(screen.getByText("order-owned")).toBeVisible();
    const lastName = screen.getByLabelText("Last name");
    await user.clear(lastName); await user.type(lastName, "Customer");
    await user.click(screen.getByRole("button", { name: "Save profile" }));
    expect(updateProfile).toHaveBeenCalledWith(expect.objectContaining({ last_name: "Customer" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Profile updated");
  });
});
