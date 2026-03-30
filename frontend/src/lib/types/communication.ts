export interface MessageTemplate {
  id: string;
  name: string;
  message_type: string;
  channel: string;
  content: string;
  active: boolean;
}

export interface Message {
  id: string;
  patient_id: string;
  patient_name?: string;
  channel: string;
  message_type: string;
  content: string;
  status: string;
  sent_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface Campaign {
  id: string;
  name: string;
  message_type: string;
  channel: string;
  template_id: string;
  status: string;
  messages_total: number;
  messages_sent: number;
  messages_failed: number;
  scheduled_at: string | null;
  created_at: string;
}

export interface MessageListResponse {
  messages: Message[];
  total: number;
}

export interface TemplateListResponse {
  templates: MessageTemplate[];
  total: number;
}

export interface CampaignListResponse {
  campaigns: Campaign[];
  total: number;
}
