import type {
  InsuranceProvider,
  InsuranceProviderListResponse,
  TISSRequest,
  TISSRequestListResponse,
  TISSStatus,
} from "@/lib/types/insurance";

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

/* ---- Insurance Providers ---- */

export async function fetchInsuranceProviders(): Promise<InsuranceProviderListResponse> {
  return apiFetch<InsuranceProviderListResponse>("/api/v1/insurance/providers");
}

export async function createInsuranceProvider(data: {
  name: string;
  ans_code: string;
  contact_phone?: string;
  contact_email?: string;
}): Promise<InsuranceProvider> {
  return apiFetch<InsuranceProvider>("/api/v1/insurance/providers", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/* ---- TISS Requests ---- */

export async function fetchTISSRequests(params?: {
  status?: TISSStatus;
  patient_id?: string;
}): Promise<TISSRequestListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.patient_id) searchParams.set("patient_id", params.patient_id);

  const qs = searchParams.toString();
  return apiFetch<TISSRequestListResponse>(
    `/api/v1/insurance/tiss${qs ? `?${qs}` : ""}`
  );
}

export async function createTISSRequest(data: {
  patient_id: string;
  insurance_provider_id: string;
  tuss_code: string;
  procedure_description: string;
  tooth_number?: number;
  requested_amount_centavos: number;
}): Promise<TISSRequest> {
  return apiFetch<TISSRequest>("/api/v1/insurance/tiss", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTISSStatus(
  id: string,
  status: TISSStatus,
  data?: { authorization_code?: string; denial_reason?: string; approved_amount_centavos?: number }
): Promise<TISSRequest> {
  return apiFetch<TISSRequest>(`/api/v1/insurance/tiss/${id}/status`, {
    method: "PUT",
    body: JSON.stringify({ status, ...data }),
  });
}
