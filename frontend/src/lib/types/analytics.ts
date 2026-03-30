export type KPIType =
  | "PATIENTS_ACTIVE"
  | "APPOINTMENTS_TODAY"
  | "REVENUE_MONTH"
  | "ATTENDANCE_RATE"
  | "TREATMENT_ACCEPTANCE"
  | "AVG_TICKET"
  | "NEW_PATIENTS_MONTH"
  | "CANCELLATION_RATE";

export interface KPI {
  kpi_type: KPIType;
  value: number;
  label: string;
  formatted_value: string;
  trend: "up" | "down" | "stable" | null;
}

export interface DashboardKPIs {
  kpis: KPI[];
}

export interface ClinicReport {
  tenant_id: string;
  period_start: string;
  period_end: string;
  kpis: KPI[];
  generated_at: string;
}
