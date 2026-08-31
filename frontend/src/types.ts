export interface EmailTriageData {
  unread: boolean;
  message?: string;
  email_id?: string;
  subject?: string;
  sender?: string;
  recipient?: string;
  received_at?: string;
  category?: string;
  priority?: string;
  spam_score?: number;
  summary?: string;
  reasoning?: string;
  reply_needed?: boolean;
  draft_reply?: string | null;
  synced_to_notion?: boolean;
  notion_page_id?: string | null;
  draft_created?: boolean;
  draft_id?: string | null;
  preference_context_used?: boolean;
}

export interface FeedbackSubmission {
  email_id: string;
  sender: string;
  subject: string;
  predicted_priority: string;
  user_priority: string;
  predicted_category: string;
  user_category: string;
  feedback_reason: string;
}
