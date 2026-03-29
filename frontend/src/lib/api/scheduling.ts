import type {
  AppointmentResponse,
  BookAppointmentRequest,
  DayScheduleResponse,
  ProviderResponse,
  UpdateStatusRequest,
} from "@/lib/types/scheduling";

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

export async function fetchDaySchedule(
  providerId: string,
  date: string
): Promise<DayScheduleResponse> {
  return apiFetch<DayScheduleResponse>(
    `/api/v1/scheduling/providers/${providerId}/day?date=${date}`
  );
}

export async function fetchProviders(): Promise<ProviderResponse[]> {
  return apiFetch<ProviderResponse[]>("/api/v1/scheduling/providers");
}

export async function bookAppointment(
  data: BookAppointmentRequest
): Promise<AppointmentResponse> {
  return apiFetch<AppointmentResponse>("/api/v1/scheduling/appointments", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAppointmentStatus(
  appointmentId: string,
  data: UpdateStatusRequest
): Promise<void> {
  return apiFetch<void>(
    `/api/v1/scheduling/appointments/${appointmentId}/status`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    }
  );
}

export async function fetchAppointment(
  appointmentId: string
): Promise<AppointmentResponse> {
  return apiFetch<AppointmentResponse>(
    `/api/v1/scheduling/appointments/${appointmentId}`
  );
}
