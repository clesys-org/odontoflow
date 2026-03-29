export interface PatientAddress {
  street: string;
  number: string;
  complement: string;
  neighborhood: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface PatientResponsible {
  name: string;
  cpf: string;
  relationship: string;
  phone: string;
}

export interface PatientInsurance {
  provider_name: string;
  plan_name: string;
  card_number: string;
  valid_until: string | null;
}

export interface Patient {
  id: string;
  full_name: string;
  cpf: string | null;
  cpf_formatted: string | null;
  birth_date: string | null;
  age: number | null;
  gender: string;
  marital_status: string | null;
  profession: string | null;
  phone: string | null;
  phone_formatted: string | null;
  whatsapp: string | null;
  email: string | null;
  preferred_channel: string;
  address: PatientAddress | null;
  responsible: PatientResponsible | null;
  insurance_info: PatientInsurance | null;
  referral_source: string | null;
  tags: string[];
  notes: string | null;
  status: string;
  is_minor: boolean;
  created_at: string;
  updated_at: string;
}

export interface PatientListResponse {
  patients: Patient[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AddressFromCEP {
  street: string;
  neighborhood: string;
  city: string;
  state: string;
  zip_code: string;
}
