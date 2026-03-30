export interface Procedure {
  id: string;
  tuss_code: string;
  description: string;
  category: string | null;
  default_price_centavos: number;
  active: boolean;
}

export interface TreatmentItem {
  id: string;
  phase_number: number;
  phase_name: string | null;
  tuss_code: string;
  description: string;
  tooth_number: number | null;
  surface: string | null;
  quantity: number;
  unit_price_centavos: number;
  status: string;
  executed_at: string | null;
}

export interface TreatmentPlan {
  id: string;
  patient_id: string;
  patient_name: string;
  provider_id: string;
  provider_name: string;
  title: string;
  status: string;
  items: TreatmentItem[];
  total_value_centavos: number;
  discount_centavos: number;
  approved_at: string | null;
  approved_by: string | null;
  created_at: string;
}

export interface TreatmentPlanListResponse {
  plans: TreatmentPlan[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
