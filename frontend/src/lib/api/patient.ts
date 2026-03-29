import type {
  Patient,
  PatientListResponse,
  AddressFromCEP,
} from "@/lib/types/patient";

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

export async function fetchPatients(params?: {
  q?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<PatientListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.q) searchParams.set("q", params.q);
  if (params?.status) searchParams.set("status", params.status);
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));

  const qs = searchParams.toString();
  return apiFetch<PatientListResponse>(
    `/api/v1/patients${qs ? `?${qs}` : ""}`
  );
}

export async function fetchPatient(id: string): Promise<Patient> {
  return apiFetch<Patient>(`/api/v1/patients/${id}`);
}

export async function createPatient(
  data: Partial<Patient>
): Promise<Patient> {
  return apiFetch<Patient>("/api/v1/patients", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updatePatient(
  id: string,
  data: Partial<Patient>
): Promise<Patient> {
  return apiFetch<Patient>(`/api/v1/patients/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deletePatient(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/patients/${id}`, {
    method: "DELETE",
  });
}

export async function fetchAddressFromCEP(
  cep: string
): Promise<AddressFromCEP | null> {
  const digits = cep.replace(/\D/g, "");
  if (digits.length !== 8) return null;

  try {
    const res = await fetch(`https://viacep.com.br/ws/${digits}/json/`);
    if (!res.ok) return null;
    const data = await res.json();
    if (data.erro) return null;
    return {
      street: data.logradouro || "",
      neighborhood: data.bairro || "",
      city: data.localidade || "",
      state: data.uf || "",
      zip_code: digits,
    };
  } catch {
    return null;
  }
}
