export type TISSStatus =
  | "PENDING"
  | "AUTHORIZED"
  | "DENIED"
  | "BILLED"
  | "PAID"
  | "GLOSA";

export interface InsuranceProvider {
  id: string;
  tenant_id: string;
  name: string;
  ans_code: string;
  contact_phone: string | null;
  contact_email: string | null;
  active: boolean;
  created_at: string;
}

export interface TISSRequest {
  id: string;
  tenant_id: string;
  patient_id: string;
  patient_name: string;
  insurance_provider_id: string;
  insurance_provider_name: string;
  guide_number: string;
  tuss_code: string;
  procedure_description: string;
  tooth_number: number | null;
  requested_amount_centavos: number;
  approved_amount_centavos: number | null;
  status: TISSStatus;
  authorization_code: string | null;
  denial_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface InsuranceProviderListResponse {
  providers: InsuranceProvider[];
  total: number;
}

export interface TISSRequestListResponse {
  requests: TISSRequest[];
  total: number;
}
