import type {
  Material,
  MaterialListResponse,
  MovementType,
  StockMovement,
  Supplier,
  SupplierListResponse,
} from "@/lib/types/inventory";

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

/* ---- Materials ---- */

export async function fetchMaterials(params?: {
  low_stock_only?: boolean;
}): Promise<MaterialListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.low_stock_only) searchParams.set("low_stock_only", "true");

  const qs = searchParams.toString();
  return apiFetch<MaterialListResponse>(
    `/api/v1/inventory/materials${qs ? `?${qs}` : ""}`
  );
}

export async function createMaterial(data: {
  name: string;
  description?: string;
  category?: string;
  unit: string;
  current_stock: number;
  min_stock: number;
  cost_centavos: number;
  supplier_id?: string;
}): Promise<Material> {
  return apiFetch<Material>("/api/v1/inventory/materials", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function recordStockMovement(
  materialId: string,
  data: {
    movement_type: MovementType;
    quantity: number;
    reason?: string;
  }
): Promise<Material> {
  return apiFetch<Material>(
    `/api/v1/inventory/materials/${materialId}/movement`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

/* ---- Suppliers ---- */

export async function fetchSuppliers(): Promise<SupplierListResponse> {
  return apiFetch<SupplierListResponse>("/api/v1/inventory/suppliers");
}

export async function createSupplier(data: {
  name: string;
  cnpj?: string;
  phone?: string;
  email?: string;
}): Promise<Supplier> {
  return apiFetch<Supplier>("/api/v1/inventory/suppliers", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
