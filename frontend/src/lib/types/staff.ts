export interface CommissionRule {
  procedure_category: string | null;
  commission_type: "PERCENTAGE" | "FIXED";
  value: number;
}

export interface StaffMember {
  id: string;
  tenant_id: string;
  user_id: string;
  full_name: string;
  cro_number: string | null;
  specialty: string | null;
  commission_rules: CommissionRule[];
  active: boolean;
  created_at: string;
}

export interface ProductionEntry {
  id: string;
  staff_id: string;
  procedure_description: string;
  revenue_centavos: number;
  commission_centavos: number;
  patient_name: string;
  date: string;
  created_at: string;
}

export interface StaffListResponse {
  staff: StaffMember[];
  total: number;
}

export interface ProductionReport {
  staff_id: string;
  start_date: string | null;
  end_date: string | null;
  total_revenue_centavos: number;
  total_commission_centavos: number;
  entries_count: number;
  entries: ProductionEntry[];
}
