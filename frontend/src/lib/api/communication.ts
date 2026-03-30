import type {
  MessageTemplate,
  Message,
  Campaign,
  MessageListResponse,
  TemplateListResponse,
  CampaignListResponse,
} from "@/lib/types/communication";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...init?.headers,
    },
  });

  if (res.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
    throw new Error("Sessao expirada");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Erro ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

/* ---- Templates ---- */

export async function fetchTemplates(): Promise<TemplateListResponse> {
  return apiFetch<TemplateListResponse>("/api/v1/communication/templates");
}

export async function createTemplate(data: {
  name: string;
  message_type: string;
  channel: string;
  content: string;
}): Promise<MessageTemplate> {
  return apiFetch<MessageTemplate>("/api/v1/communication/templates", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/* ---- Messages ---- */

export async function sendMessage(data: {
  patient_id: string;
  channel: string;
  template_id?: string;
  content?: string;
}): Promise<Message> {
  return apiFetch<Message>("/api/v1/communication/messages", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function fetchMessages(params?: {
  status?: string;
  channel?: string;
}): Promise<MessageListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.channel) searchParams.set("channel", params.channel);

  const qs = searchParams.toString();
  return apiFetch<MessageListResponse>(
    `/api/v1/communication/messages${qs ? `?${qs}` : ""}`
  );
}

/* ---- Campaigns ---- */

export async function fetchCampaigns(): Promise<CampaignListResponse> {
  return apiFetch<CampaignListResponse>("/api/v1/communication/campaigns");
}

export async function createCampaign(data: {
  name: string;
  message_type: string;
  channel: string;
  template_id: string;
  scheduled_at?: string;
}): Promise<Campaign> {
  return apiFetch<Campaign>("/api/v1/communication/campaigns", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function executeCampaign(id: string): Promise<Campaign> {
  return apiFetch<Campaign>(`/api/v1/communication/campaigns/${id}/execute`, {
    method: "POST",
  });
}
