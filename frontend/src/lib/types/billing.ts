export interface Installment {
  id: string;
  number: number;
  due_date: string;
  amount_centavos: number;
  payment_method: string | null;
  status: string;
  paid_at: string | null;
}

export interface Invoice {
  id: string;
  patient_id: string;
  patient_name: string;
  treatment_plan_id: string | null;
  description: string;
  total_centavos: number;
  status: string;
  installments: Installment[];
  amount_paid_centavos: number;
  amount_remaining_centavos: number;
  created_at: string;
}

export interface InvoiceListResponse {
  invoices: Invoice[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FinanceDashboard {
  total_revenue_centavos: number;
  total_receivable_centavos: number;
  total_overdue_centavos: number;
  invoices_count: number;
  paid_count: number;
  pending_count: number;
  overdue_count: number;
  recent_payments: {
    patient_name: string;
    amount_centavos: number;
    paid_at: string;
    method: string;
  }[];
}
