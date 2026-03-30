import type { ClinicWebsite } from "@/lib/types/website";

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

/* ---- Website ---- */

export async function fetchWebsite(): Promise<ClinicWebsite> {
  return apiFetch<ClinicWebsite>("/api/v1/website");
}

export async function updateWebsite(
  data: Partial<Omit<ClinicWebsite, "id" | "slug">>
): Promise<ClinicWebsite> {
  return apiFetch<ClinicWebsite>("/api/v1/website", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function togglePublish(): Promise<ClinicWebsite> {
  return apiFetch<ClinicWebsite>("/api/v1/website/toggle-publish", {
    method: "POST",
  });
}
