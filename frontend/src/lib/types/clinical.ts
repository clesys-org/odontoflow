export interface ToothSurface {
  position: string; // MESIAL, DISTAL, OCLUSAL, VESTIBULAR, LINGUAL
  condition: string; // HEALTHY, CARIES, RESTORATION, FRACTURE, SEALANT, CROWN, VENEER
}

export interface Tooth {
  id: string;
  tooth_number: number;
  status: string; // PRESENT, ABSENT, IMPLANT, DECIDUOUS, ROOT_REMNANT
  surfaces: ToothSurface[];
  notes: string | null;
  updated_by: string | null;
  updated_at: string;
}

export interface Anamnesis {
  id: string;
  chief_complaint: string;
  medical_history: Record<string, unknown>;
  dental_history: Record<string, unknown>;
  created_by: string;
  created_at: string;
  signed_at: string | null;
}

export interface ClinicalNote {
  id: string;
  note_type: string; // EVOLUTION, PROCEDURE, OBSERVATION
  content: string;
  tooth_references: number[];
  attachments: Record<string, unknown>[];
  created_by: string;
  created_at: string;
  signed_at: string | null;
}

export interface PrescriptionItem {
  medication_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  instructions: string;
}

export interface Prescription {
  id: string;
  items: PrescriptionItem[];
  created_by: string;
  created_at: string;
}

export interface TimelineEntry {
  id: string;
  event_type: string;
  summary: string;
  provider_name: string | null;
  occurred_at: string;
  metadata: Record<string, unknown> | null;
}

export interface PatientRecord {
  id: string;
  patient_id: string;
  anamnesis: Anamnesis | null;
  teeth: Tooth[];
  notes: ClinicalNote[];
  prescriptions: Prescription[];
  created_at: string;
}

export interface OdontogramData {
  teeth: Tooth[];
  total_teeth: number;
}
