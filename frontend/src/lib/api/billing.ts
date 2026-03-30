import type {
  Invoice,
  InvoiceListResponse,
  FinanceDashboard,
} from "@/lib/types/billing";

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

/* ---- Invoices ---- */

export async function fetchInvoices(params?: {
  q?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<InvoiceListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.q) searchParams.set("q", params.q);
  if (params?.status) searchParams.set("status", params.status);
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size)
    searchParams.set("page_size", String(params.page_size));

  const qs = searchParams.toString();
  return apiFetch<InvoiceListResponse>(
    `/api/v1/invoices${qs ? `?${qs}` : ""}`
  );
}

export async function fetchInvoice(id: string): Promise<Invoice> {
  return apiFetch<Invoice>(`/api/v1/invoices/${id}`);
}

export async function createInvoice(data: {
  patient_id: string;
  treatment_plan_id?: string | null;
  description: string;
  total_centavos: number;
  installments_count?: number;
  first_due_date?: string;
}): Promise<Invoice> {
  return apiFetch<Invoice>("/api/v1/invoices", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function payInstallment(
  invoiceId: string,
  installmentNumber: number,
  method: string
): Promise<Invoice> {
  return apiFetch<Invoice>(
    `/api/v1/invoices/${invoiceId}/installments/${installmentNumber}/pay`,
    {
      method: "POST",
      body: JSON.stringify({ payment_method: method }),
    }
  );
}

export async function cancelInvoice(id: string): Promise<Invoice> {
  return apiFetch<Invoice>(`/api/v1/invoices/${id}/cancel`, {
    method: "POST",
  });
}

/* ---- Finance Dashboard ---- */

export async function fetchFinanceDashboard(): Promise<FinanceDashboard> {
  return apiFetch<FinanceDashboard>("/api/v1/finance/dashboard");
}
