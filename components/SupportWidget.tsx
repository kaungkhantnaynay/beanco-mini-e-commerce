"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Coffee, MessageCircle, Send, ShieldCheck, X } from "lucide-react";
import { sendSupportMessage, SupportRequestError } from "@/lib/api/support";

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  text: string;
  citations?: string[];
  ticketId?: number | null;
  escalated?: boolean;
};

const initialMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  text: "Hi, I’m BeanCO support. Ask me about delivery, products, checkout, or your account. I’ll bring in a person when a private detail needs review.",
};

const suggestedQuestions = [
  "How long does delivery take?",
  "Can I cancel an order?",
  "How do I ask about wholesale?",
];

function customerFacingAnswer(answer: string): string {
  return answer.replace(/\s+Source:\s+[\s\S]+$/, "").trim();
}

function customerFacingCitation(citation: string): string {
  return citation.replace(/\s+\([^)]*\)$/, "").trim();
}

export default function SupportWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([initialMessage]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [conversationId, setConversationId] = useState<number>();
  const [conversationToken, setConversationToken] = useState<string>();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const transcriptRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) inputRef.current?.focus();
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const transcript = transcriptRef.current;
    if (transcript) transcript.scrollTop = transcript.scrollHeight;
  }, [isOpen, messages, pending]);

  useEffect(() => {
    if (!isOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [isOpen]);

  async function submitMessage(message: string) {
    const trimmed = message.trim();
    if (trimmed.length < 2 || pending) return;

    setMessages((current) => [
      ...current,
      { id: `user-${Date.now()}`, role: "user", text: trimmed },
    ]);
    setDraft("");
    setError("");
    setPending(true);

    try {
      const response = await sendSupportMessage({
        message: trimmed,
        ...(conversationId ? { conversation_id: conversationId } : {}),
        ...(conversationToken ? { conversation_token: conversationToken } : {}),
      });
      setConversationId(response.conversation_id);
      setConversationToken(response.conversation_token ?? conversationToken);
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${response.message_id}`,
          role: "assistant",
          text: customerFacingAnswer(response.answer),
          citations: response.citations.map(customerFacingCitation),
          ticketId: response.ticket_id,
          escalated: response.needs_escalation,
        },
      ]);
    } catch (caught) {
      setError(
        caught instanceof SupportRequestError
          ? caught.message
          : "BeanCO support is temporarily unavailable.",
      );
    } finally {
      setPending(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitMessage(draft);
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 sm:bottom-6 sm:right-6">
      {isOpen ? (
        <aside
          id="beanco-support-panel"
          aria-label="BeanCO support chat"
          className="flex h-[min(42rem,calc(100dvh-2rem))] w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl bg-card shadow-[0_24px_70px_rgba(47,33,22,0.24)] sm:h-[38rem] sm:w-[24rem]"
        >
          <header className="flex items-center justify-between gap-4 bg-primary px-5 py-4 text-primary-foreground">
            <div className="flex min-w-0 items-center gap-3">
              <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-primary-foreground/10" aria-hidden="true">
                <Coffee className="h-5 w-5" />
              </span>
              <div>
                <h2 className="font-semibold leading-tight">BeanCO support</h2>
                <p className="mt-1 text-xs text-primary-foreground/75">Answers from our store guide</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              aria-label="Close support chat"
              className="grid h-10 w-10 shrink-0 place-items-center rounded-full text-primary-foreground/80 transition-colors hover:bg-primary-foreground/10 hover:text-primary-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-foreground"
            >
              <X className="h-5 w-5" aria-hidden="true" />
            </button>
          </header>

          <div ref={transcriptRef} className="min-h-0 flex-1 space-y-4 overflow-y-auto bg-background px-4 py-5" aria-live="polite">
            {messages.map((message) => (
              <article
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`max-w-[88%] ${message.role === "user" ? "rounded-2xl rounded-br-md bg-primary px-4 py-3 text-primary-foreground" : "text-foreground"}`}>
                  <p className="text-sm leading-6">{message.text}</p>
                  {message.citations?.length ? (
                    <p className="mt-2 text-xs text-muted-foreground">
                      Source: {message.citations.join(" · ")}
                    </p>
                  ) : null}
                  {message.escalated ? (
                    <p className="mt-3 flex items-center gap-2 text-xs font-medium text-primary">
                      <ShieldCheck className="h-4 w-4 shrink-0" aria-hidden="true" />
                      Sent to the BeanCO team{message.ticketId ? ` · Ticket #${message.ticketId}` : ""}
                    </p>
                  ) : null}
                </div>
              </article>
            ))}

            {messages.length === 1 ? (
              <div className="flex flex-wrap gap-2" aria-label="Suggested questions">
                {suggestedQuestions.map((question) => (
                  <button
                    key={question}
                    type="button"
                    onClick={() => void submitMessage(question)}
                    className="rounded-full bg-secondary px-3 py-2 text-left text-xs font-medium text-secondary-foreground transition-colors hover:bg-secondary/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    {question}
                  </button>
                ))}
              </div>
            ) : null}

            {pending ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
                <span className="support-pulse h-2 w-2 rounded-full bg-accent" aria-hidden="true" />
                Checking the store guide…
              </div>
            ) : null}

            {error ? (
              <div className="rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
                {error} Your message was not saved; please send it again.
              </div>
            ) : null}
          </div>

          <form onSubmit={onSubmit} className="bg-card p-4">
            <label htmlFor="beanco-support-message" className="sr-only">Message BeanCO support</label>
            <div className="flex items-end gap-2 rounded-2xl bg-muted p-2 focus-within:ring-2 focus-within:ring-ring">
              <textarea
                ref={inputRef}
                id="beanco-support-message"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    event.currentTarget.form?.requestSubmit();
                  }
                }}
                rows={1}
                maxLength={2000}
                placeholder="Ask about your BeanCO order…"
                className="max-h-28 min-h-10 flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-5 outline-none placeholder:text-muted-foreground"
              />
              <button
                type="submit"
                disabled={pending || draft.trim().length < 2}
                aria-label="Send support message"
                className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground transition-[background-color,transform] hover:bg-primary/90 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40 motion-reduce:transform-none"
              >
                <Send className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
            <p className="mt-2 px-1 text-[11px] leading-4 text-muted-foreground">
              Don’t share passwords, payment details, or verification links.
            </p>
          </form>
        </aside>
      ) : (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          aria-expanded="false"
          aria-controls="beanco-support-panel"
          className="group flex h-14 items-center gap-3 rounded-full bg-primary px-5 text-sm font-semibold text-primary-foreground shadow-[0_12px_36px_rgba(47,33,22,0.22)] transition-[background-color,transform] hover:-translate-y-0.5 hover:bg-primary/95 active:translate-y-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 motion-reduce:transform-none"
        >
          <MessageCircle className="h-5 w-5" aria-hidden="true" />
          Ask BeanCO
        </button>
      )}
    </div>
  );
}
