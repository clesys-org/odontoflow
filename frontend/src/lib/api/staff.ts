import type {
  StaffMember,
  StaffListResponse,
  ProductionReport,
  ProductionEntry,
} from "@/lib/types/staff";

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

/* ---- Staff ---- */

export async function fetchStaff(): Promise<StaffListResponse> {
  return apiFetch<StaffListResponse>("/api/v1/staff");
}

export async function fetchStaffMember(id: string): Promise<StaffMember> {
  return apiFetch<StaffMember>(`/api/v1/staff/${id}`);
}

export async function createStaff(data: {
  full_name: string;
  cro_number?: string;
  specialty?: string;
  commission_rules?: {
    procedure_category: string | null;
    commission_type: string;
    value: number;
  }[];
}): Promise<StaffMember> {
  return apiFetch<StaffMember>("/api/v1/staff", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateStaff(
  id: string,
  data: {
    full_name?: string;
    cro_number?: string;
    specialty?: string;
    active?: boolean;
    commission_rules?: {
      procedure_category: string | null;
      commission_type: string;
      value: number;
    }[];
  }
): Promise<StaffMember> {
  return apiFetch<StaffMember>(`/api/v1/staff/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/* ---- Production ---- */

export async function fetchProductionReport(
  staffId: string,
  params?: { start_date?: string; end_date?: string }
): Promise<ProductionReport> {
  const searchParams = new URLSearchParams();
  if (params?.start_date) searchParams.set("start_date", params.start_date);
  if (params?.end_date) searchParams.set("end_date", params.end_date);

  const qs = searchParams.toString();
  return apiFetch<ProductionReport>(
    `/api/v1/staff/${staffId}/production${qs ? `?${qs}` : ""}`
  );
}

export async function recordProduction(
  staffId: string,
  data: {
    procedure_description: string;
    revenue_centavos: number;
    patient_name: string;
    date: string;
    treatment_item_id?: string;
    procedure_category?: string;
  }
): Promise<ProductionEntry> {
  return apiFetch<ProductionEntry>(`/api/v1/staff/${staffId}/production`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}
