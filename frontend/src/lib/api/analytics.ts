import type { DashboardKPIs, ClinicReport } from "@/lib/types/analytics";

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

/* ---- Dashboard KPIs ---- */

export async function fetchDashboardKPIs(): Promise<DashboardKPIs> {
  return apiFetch<DashboardKPIs>("/api/v1/analytics/dashboard");
}

/* ---- Period Report ---- */

export async function fetchPeriodReport(
  start: string,
  end: string
): Promise<ClinicReport> {
  return apiFetch<ClinicReport>(
    `/api/v1/analytics/report?start=${start}&end=${end}`
  );
}
