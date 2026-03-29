"""Shared Kernel — Enums e tipos compartilhados entre bounded contexts."""

from enum import Enum


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    NOT_INFORMED = "NOT_INFORMED"


class MaritalStatus(str, Enum):
    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"
    OTHER = "OTHER"


class ContactChannel(str, Enum):
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    EMAIL = "EMAIL"
    PHONE = "PHONE"


class PaymentMethod(str, Enum):
    PIX = "PIX"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    CASH = "CASH"
    BOLETO = "BOLETO"
    INSURANCE = "INSURANCE"


class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class PlanTier(str, Enum):
    FREE = "FREE"
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class UserRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    DENTIST = "DENTIST"
    RECEPTIONIST = "RECEPTIONIST"
    ASSISTANT = "ASSISTANT"
    PATIENT = "PATIENT"


class PatientStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class ToothStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    IMPLANT = "IMPLANT"
    DECIDUOUS = "DECIDUOUS"
    ROOT_REMNANT = "ROOT_REMNANT"


class SurfacePosition(str, Enum):
    MESIAL = "MESIAL"
    DISTAL = "DISTAL"
    OCLUSAL = "OCLUSAL"
    VESTIBULAR = "VESTIBULAR"
    LINGUAL = "LINGUAL"
    INCISAL = "INCISAL"


class SurfaceCondition(str, Enum):
    HEALTHY = "HEALTHY"
    CARIES = "CARIES"
    RESTORATION = "RESTORATION"
    FRACTURE = "FRACTURE"
    SEALANT = "SEALANT"
    CROWN = "CROWN"
    VENEER = "VENEER"


class NoteType(str, Enum):
    EVOLUTION = "EVOLUTION"
    PROCEDURE = "PROCEDURE"
    OBSERVATION = "OBSERVATION"


class TreatmentPlanStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class InstallmentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
