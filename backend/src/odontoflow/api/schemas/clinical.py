"""Pydantic v2 schemas for Clinical Record endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class CreateAnamnesisRequest(BaseModel):
    chief_complaint: str = Field(min_length=2, max_length=2000)
    medical_history: dict = Field(default_factory=dict)
    dental_history: dict = Field(default_factory=dict)


class ToothSurfaceRequest(BaseModel):
    position: str  # SurfacePosition enum value
    condition: str = "HEALTHY"  # SurfaceCondition enum value


class UpdateToothRequest(BaseModel):
    status: str = "PRESENT"  # ToothStatus enum value
    surfaces: list[ToothSurfaceRequest] = []
    notes: Optional[str] = None


class CreateClinicalNoteRequest(BaseModel):
    note_type: str = "EVOLUTION"  # NoteType enum value
    content: str = Field(min_length=1, max_length=10000)
    tooth_references: list[int] = []
    attachments: list[dict] = []
    sign_immediately: bool = False


class PrescriptionItemRequest(BaseModel):
    medication_name: str = Field(min_length=1, max_length=255)
    dosage: str = ""
    frequency: str = ""
    duration: str = ""
    instructions: str = ""


class CreatePrescriptionRequest(BaseModel):
    items: list[PrescriptionItemRequest] = Field(min_length=1)


class CreateConsentRequest(BaseModel):
    form_type: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=50000)
    patient_signature: Optional[str] = None  # base64


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class AnamnesisResponse(BaseModel):
    id: str
    chief_complaint: str
    medical_history: dict
    dental_history: dict
    created_by: Optional[str] = None
    created_at: str
    signed_at: Optional[str] = None


class ToothSurfaceResponse(BaseModel):
    position: str
    condition: str


class ToothResponse(BaseModel):
    id: str
    tooth_number: int
    status: str
    surfaces: list[ToothSurfaceResponse]
    notes: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None


class ClinicalNoteResponse(BaseModel):
    id: str
    note_type: str
    content: str
    tooth_references: list[int]
    attachments: list[dict]
    is_signed: bool
    created_by: Optional[str] = None
    created_at: str
    signed_at: Optional[str] = None


class PrescriptionItemResponse(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str


class PrescriptionResponse(BaseModel):
    id: str
    items: list[PrescriptionItemResponse]
    created_by: Optional[str] = None
    created_at: str


class ConsentFormResponse(BaseModel):
    id: str
    form_type: str
    content: str
    signed_at: Optional[str] = None


class PatientRecordResponse(BaseModel):
    id: str
    patient_id: str
    anamnesis: Optional[AnamnesisResponse] = None
    teeth_count: int = 0
    notes_count: int = 0
    prescriptions_count: int = 0
    consent_forms_count: int = 0
    created_at: str


class OdontogramResponse(BaseModel):
    teeth: list[ToothResponse]
    total: int


class NotesListResponse(BaseModel):
    notes: list[ClinicalNoteResponse]
    total: int


class PrescriptionsListResponse(BaseModel):
    prescriptions: list[PrescriptionResponse]
    total: int


class TimelineEntryResponse(BaseModel):
    type: str
    id: Optional[str] = None
    summary: Optional[str] = None
    note_type: Optional[str] = None
    is_signed: Optional[bool] = None
    signed: Optional[bool] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None


class TimelineResponse(BaseModel):
    entries: list[TimelineEntryResponse]
    total: int
    page: int
    page_size: int
