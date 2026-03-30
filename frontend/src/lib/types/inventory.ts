export type MovementType = "ENTRADA" | "SAIDA" | "AJUSTE";

export interface Material {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  category: string | null;
  unit: string;
  current_stock: number;
  min_stock: number;
  cost_centavos: number;
  supplier_id: string | null;
  supplier_name: string | null;
  is_low_stock: boolean;
  active: boolean;
  created_at: string;
}

export interface StockMovement {
  id: string;
  material_id: string;
  movement_type: MovementType;
  quantity: number;
  reason: string | null;
  created_at: string;
}

export interface Supplier {
  id: string;
  tenant_id: string;
  name: string;
  cnpj: string | null;
  phone: string | null;
  email: string | null;
  created_at: string;
}

export interface MaterialListResponse {
  materials: Material[];
  total: number;
}

export interface SupplierListResponse {
  suppliers: Supplier[];
  total: number;
}
