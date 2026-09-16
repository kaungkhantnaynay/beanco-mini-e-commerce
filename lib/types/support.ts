export interface SupportChatRequest {
  message: string;
  conversation_id?: number;
  conversation_token?: string;
}

export interface SupportChatResponse {
  conversation_token: string | null;
  conversation_id: number;
  message_id: number;
  ticket_id: number | null;
  answer: string;
  citations: string[];
  confidence: "high" | "medium" | "low";
  needs_escalation: boolean;
  escalation_reason: string | null;
}
