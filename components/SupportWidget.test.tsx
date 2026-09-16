import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import SupportWidget from "@/components/SupportWidget";
import { sendSupportMessage } from "@/lib/api/support";

vi.mock("@/lib/api/support", () => ({
  sendSupportMessage: vi.fn(),
  SupportRequestError: class SupportRequestError extends Error {},
}));

describe("SupportWidget", () => {
  beforeEach(() => {
    vi.mocked(sendSupportMessage).mockReset().mockResolvedValue({
      conversation_token: "fictional-token",
      conversation_id: 7,
      message_id: 11,
      ticket_id: null,
      answer: "Standard delivery takes 3 to 5 business days.",
      citations: ["BeanCo Shipping And Orders (data/knowledge_beanco/shipping_and_orders.md)"],
      confidence: "high",
      needs_escalation: false,
      escalation_reason: null,
    });
  });

  it("opens an accessible support panel and sends a suggested question", async () => {
    const user = userEvent.setup();
    render(<SupportWidget />);

    await user.click(screen.getByRole("button", { name: "Ask BeanCO" }));
    expect(screen.getByRole("complementary", { name: "BeanCO support chat" })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "How long does delivery take?" }));

    expect(await screen.findByText("Standard delivery takes 3 to 5 business days.")).toBeVisible();
    expect(sendSupportMessage).toHaveBeenCalledWith({ message: "How long does delivery take?" });
    expect(screen.getByText(/Source: BeanCo Shipping And Orders/)).toBeVisible();
    expect(screen.queryByText(/data\/knowledge_beanco/)).not.toBeInTheDocument();
  });

  it("keeps conversation credentials in component state for follow-up messages", async () => {
    const user = userEvent.setup();
    const storageSpy = vi.spyOn(Storage.prototype, "setItem");
    vi.mocked(sendSupportMessage)
      .mockResolvedValueOnce({
        conversation_token: "fictional-token",
        conversation_id: 7,
        message_id: 11,
        ticket_id: null,
        answer: "Standard delivery takes 3 to 5 business days.",
        citations: ["BeanCo Shipping And Orders (data/knowledge_beanco/shipping_and_orders.md)"],
        confidence: "high",
        needs_escalation: false,
        escalation_reason: null,
      })
      .mockResolvedValueOnce({
        conversation_token: null,
        conversation_id: 7,
        message_id: 12,
        ticket_id: 3,
        answer: "A support ticket has been created.",
        citations: [],
        confidence: "low",
        needs_escalation: true,
        escalation_reason: "Human review required.",
      });
    render(<SupportWidget />);
    await user.click(screen.getByRole("button", { name: "Ask BeanCO" }));
    await user.type(screen.getByLabelText("Message BeanCO support"), "Where is my order?");
    await user.click(screen.getByRole("button", { name: "Send support message" }));
    await screen.findByText("Standard delivery takes 3 to 5 business days.");

    await user.type(screen.getByLabelText("Message BeanCO support"), "Can I cancel it?");
    await user.click(screen.getByRole("button", { name: "Send support message" }));

    expect(sendSupportMessage).toHaveBeenLastCalledWith({
      message: "Can I cancel it?",
      conversation_id: 7,
      conversation_token: "fictional-token",
    });
    expect(storageSpy).not.toHaveBeenCalled();
  });
});
