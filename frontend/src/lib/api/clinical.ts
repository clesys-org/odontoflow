import type {
  PatientRecord,
  Anamnesis,
  OdontogramData,
  Tooth,
  ClinicalNote,
  Prescription,
  TimelineEntry,
} from "@/lib/types/clinical";

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

// ---- Patient Record ----

export async function fetchPatientRecord(
  patientId: string
): Promise<PatientRecord> {
  return apiFetch<PatientRecord>(
    `/api/v1/patients/${patientId}/clinical-record`
  );
}

// ---- Anamnesis ----

export async function createAnamnesis(
  patientId: string,
  data: {
    chief_complaint: string;
    medical_history: Record<string, unknown>;
    dental_history: Record<string, unknown>;
  }
): Promise<Anamnesis> {
  return apiFetch<Anamnesis>(
    `/api/v1/patients/${patientId}/clinical-record/anamnesis`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

// ---- Odontogram ----

export async function fetchOdontogram(
  patientId: string
): Promise<OdontogramData> {
  return apiFetch<OdontogramData>(
    `/api/v1/patients/${patientId}/clinical-record/odontogram`
  );
}

export async function updateTooth(
  patientId: string,
  toothNumber: number,
  data: {
    status?: string;
    surfaces?: { position: string; condition: string }[];
    notes?: string | null;
  }
): Promise<Tooth> {
  return apiFetch<Tooth>(
    `/api/v1/patients/${patientId}/clinical-record/odontogram/teeth/${toothNumber}`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    }
  );
}

// ---- Clinical Notes ----

export async function fetchNotes(
  patientId: string
): Promise<ClinicalNote[]> {
  return apiFetch<ClinicalNote[]>(
    `/api/v1/patients/${patientId}/clinical-record/notes`
  );
}

export async function createNote(
  patientId: string,
  data: {
    note_type: string;
    content: string;
    tooth_references?: number[];
  }
): Promise<ClinicalNote> {
  return apiFetch<ClinicalNote>(
    `/api/v1/patients/${patientId}/clinical-record/notes`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

// ---- Prescriptions ----

export async function fetchPrescriptions(
  patientId: string
): Promise<Prescription[]> {
  return apiFetch<Prescription[]>(
    `/api/v1/patients/${patientId}/clinical-record/prescriptions`
  );
}

export async function createPrescription(
  patientId: string,
  data: {
    items: {
      medication_name: string;
      dosage: string;
      frequency: string;
      duration: string;
      instructions: string;
    }[];
  }
): Promise<Prescription> {
  return apiFetch<Prescription>(
    `/api/v1/patients/${patientId}/clinical-record/prescriptions`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

// ---- Timeline ----

export interface TimelineResponse {
  entries: TimelineEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export async function fetchTimeline(
  patientId: string,
  page = 1,
  pageSize = 20
): Promise<TimelineResponse> {
  return apiFetch<TimelineResponse>(
    `/api/v1/patients/${patientId}/clinical-record/timeline?page=${page}&page_size=${pageSize}`
  );
}
