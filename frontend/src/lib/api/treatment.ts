import type {
  Procedure,
  TreatmentPlan,
  TreatmentPlanListResponse,
  TreatmentItem,
} from "@/lib/types/treatment";

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

/* ---- Procedures ---- */

export async function fetchProcedures(): Promise<Procedure[]> {
  return apiFetch<Procedure[]>("/api/v1/procedures");
}

export async function createProcedure(
  data: Omit<Procedure, "id">
): Promise<Procedure> {
  return apiFetch<Procedure>("/api/v1/procedures", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/* ---- Treatment Plans ---- */

export async function fetchPatientPlans(
  patientId: string
): Promise<TreatmentPlan[]> {
  return apiFetch<TreatmentPlan[]>(
    `/api/v1/patients/${patientId}/treatment-plans`
  );
}

export async function fetchPlans(params?: {
  q?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<TreatmentPlanListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.q) searchParams.set("q", params.q);
  if (params?.status) searchParams.set("status", params.status);
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size)
    searchParams.set("page_size", String(params.page_size));

  const qs = searchParams.toString();
  return apiFetch<TreatmentPlanListResponse>(
    `/api/v1/treatment-plans${qs ? `?${qs}` : ""}`
  );
}

export async function fetchPlan(planId: string): Promise<TreatmentPlan> {
  return apiFetch<TreatmentPlan>(`/api/v1/treatment-plans/${planId}`);
}

export async function createPlan(
  patientId: string,
  data: {
    title: string;
    items: {
      tuss_code: string;
      description: string;
      tooth_number?: number | null;
      surface?: string | null;
      quantity: number;
      unit_price_centavos: number;
      phase_number?: number;
      phase_name?: string | null;
    }[];
    discount_centavos?: number;
  }
): Promise<TreatmentPlan> {
  return apiFetch<TreatmentPlan>(
    `/api/v1/patients/${patientId}/treatment-plans`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

export async function approvePlan(
  planId: string,
  approvedBy: string
): Promise<TreatmentPlan> {
  return apiFetch<TreatmentPlan>(
    `/api/v1/treatment-plans/${planId}/approve`,
    {
      method: "POST",
      body: JSON.stringify({ approved_by: approvedBy }),
    }
  );
}

export async function executeItem(
  planId: string,
  itemId: string
): Promise<TreatmentItem> {
  return apiFetch<TreatmentItem>(
    `/api/v1/treatment-plans/${planId}/items/${itemId}/execute`,
    { method: "POST" }
  );
}

export async function cancelPlan(planId: string): Promise<TreatmentPlan> {
  return apiFetch<TreatmentPlan>(
    `/api/v1/treatment-plans/${planId}/cancel`,
    { method: "POST" }
  );
}
