export interface AvailableSlot {
  start: string;
  end: string;
  duration_minutes: number;
}

export interface AppointmentResponse {
  id: string;
  patient_id: string;
  patient_name: string;
  provider_id: string;
  provider_name: string;
  start_at: string;
  end_at: string;
  duration_minutes: number;
  status: string;
  appointment_type: string;
  type_color: string;
  notes: string | null;
  source: string;
  cancellation_reason: string | null;
  created_at: string;
}

export interface DayScheduleResponse {
  date: string;
  provider_id: string;
  provider_name: string;
  appointments: AppointmentResponse[];
  available_slots: AvailableSlot[];
}

export interface ProviderResponse {
  id: string;
  name: string;
  cro_number: string | null;
  specialty: string | null;
  color: string;
  active: boolean;
}

export interface BookAppointmentRequest {
  patient_id: string;
  provider_id: string;
  start_at: string;
  duration_minutes: number;
  appointment_type: string;
  type_color: string;
  notes?: string;
  procedures?: Record<string, unknown>[];
}

export interface UpdateStatusRequest {
  action: "confirm" | "start" | "complete" | "cancel" | "no_show";
  reason?: string;
}
