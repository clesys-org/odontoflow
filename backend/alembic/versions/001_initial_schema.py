"""Initial schema — tabelas globais (public) e tenant.

Revision ID: 001
Revises: None
Create Date: 2026-03-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ══════════════════════════════════════════════════════════
    # PUBLIC SCHEMA — Tabelas globais (multi-tenant management)
    # ══════════════════════════════════════════════════════════

    # ── Tenants (clinicas) ─────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(63), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("cnpj", sa.String(18)),
        sa.Column("phone", sa.String(20)),
        sa.Column("email", sa.String(255)),
        sa.Column("schema_name", sa.String(63), unique=True, nullable=False),
        sa.Column("plan_tier", sa.String(20), nullable=False, server_default="trial"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )

    # ── Users (global) ─────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("mfa_secret", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )

    # ── Tenant Memberships ─────────────────────────────────
    op.create_table(
        "tenant_memberships",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("public.users.id"), nullable=False),
        sa.Column("tenant_id", sa.UUID, sa.ForeignKey("public.tenants.id"), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("permissions", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "tenant_id"),
        schema="public",
    )

    # ── Audit Log (global, imutavel) ───────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.UUID, nullable=False),
        sa.Column("user_id", sa.UUID),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100)),
        sa.Column("entity_id", sa.UUID),
        sa.Column("changes", sa.JSON),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )
    op.create_index("idx_audit_tenant", "audit_log", ["tenant_id"], schema="public")
    op.create_index("idx_audit_created", "audit_log", ["created_at"], schema="public")

    # ══════════════════════════════════════════════════════════
    # TENANT SCHEMA — Tabelas por clinica
    # (executadas no search_path do tenant ativo)
    # ══════════════════════════════════════════════════════════

    # ── Patients ───────────────────────────────────────────
    op.create_table(
        "patients",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("cpf", sa.String(14), unique=True),
        sa.Column("birth_date", sa.Date),
        sa.Column("gender", sa.String(20)),
        sa.Column("phone", sa.String(20)),
        sa.Column("whatsapp", sa.String(20)),
        sa.Column("email", sa.String(255)),
        sa.Column("address", sa.JSON),
        sa.Column("responsible", sa.JSON),
        sa.Column("insurance_info", sa.JSON),
        sa.Column("referral_source", sa.String(100)),
        sa.Column("tags", sa.ARRAY(sa.Text)),
        sa.Column("lgpd_consent", sa.JSON, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_patients_name", "patients", ["full_name"])
    op.create_index("idx_patients_cpf", "patients", ["cpf"])

    # ── Providers (dentistas/profissionais) ────────────────
    op.create_table(
        "providers",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("cro_number", sa.String(20)),
        sa.Column("specialty", sa.String(100)),
        sa.Column("color", sa.String(7)),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── Provider Schedules ─────────────────────────────────
    op.create_table(
        "provider_schedules",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_id", sa.UUID, sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("working_hours", sa.JSON, nullable=False),
        sa.Column("breaks", sa.JSON, server_default="[]"),
        sa.Column("overbooking_limit", sa.SmallInteger, server_default="0"),
    )

    # ── Blocked Slots ──────────────────────────────────────
    op.create_table(
        "blocked_slots",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_id", sa.UUID, sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(255)),
    )

    # ── Appointments ───────────────────────────────────────
    op.create_table(
        "appointments",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", sa.UUID, sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("provider_id", sa.UUID, sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.SmallInteger, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="scheduled"),
        sa.Column("appointment_type", sa.String(50), nullable=False),
        sa.Column("type_color", sa.String(7)),
        sa.Column("procedures_planned", sa.JSON, server_default="[]"),
        sa.Column("notes", sa.Text),
        sa.Column("source", sa.String(30), server_default="receptionist"),
        sa.Column("cancellation_reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_appointments_provider_date", "appointments", ["provider_id", "start_at"])
    op.create_index("idx_appointments_patient", "appointments", ["patient_id"])
    op.create_index("idx_appointments_status", "appointments", ["status"])

    # ── Patient Records (prontuario — aggregate root) ──────
    op.create_table(
        "patient_records",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", sa.UUID, sa.ForeignKey("patients.id"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── Anamnesis ──────────────────────────────────────────
    op.create_table(
        "anamnesis",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_record_id", sa.UUID, sa.ForeignKey("patient_records.id"), nullable=False),
        sa.Column("chief_complaint", sa.Text),
        sa.Column("medical_history", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("dental_history", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_by", sa.UUID, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("signed_at", sa.DateTime(timezone=True)),
        sa.Column("digital_signature", sa.JSON),
    )

    # ── Odontogram Teeth ───────────────────────────────────
    op.create_table(
        "odontogram_teeth",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_record_id", sa.UUID, sa.ForeignKey("patient_records.id"), nullable=False),
        sa.Column("tooth_number", sa.SmallInteger, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="present"),
        sa.Column("surfaces", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("notes", sa.Text),
        sa.Column("updated_by", sa.UUID, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("patient_record_id", "tooth_number"),
    )

    # ── Clinical Notes ─────────────────────────────────────
    op.create_table(
        "clinical_notes",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_record_id", sa.UUID, sa.ForeignKey("patient_records.id"), nullable=False),
        sa.Column("note_type", sa.String(30), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("tooth_references", sa.ARRAY(sa.SmallInteger)),
        sa.Column("attachments", sa.JSON, server_default="[]"),
        sa.Column("created_by", sa.UUID, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("digital_signature", sa.JSON),
    )
    op.create_index("idx_notes_record", "clinical_notes", ["patient_record_id"])

    # ── Prescriptions ──────────────────────────────────────
    op.create_table(
        "prescriptions",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_record_id", sa.UUID, sa.ForeignKey("patient_records.id"), nullable=False),
        sa.Column("items", sa.JSON, nullable=False),
        sa.Column("created_by", sa.UUID, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── Consent Forms ──────────────────────────────────────
    op.create_table(
        "consent_forms",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_record_id", sa.UUID, sa.ForeignKey("patient_records.id"), nullable=False),
        sa.Column("form_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("patient_signature", sa.Text),
        sa.Column("signed_at", sa.DateTime(timezone=True)),
    )

    # ── Procedure Catalog (TUSS) ───────────────────────────
    op.create_table(
        "procedure_catalog",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tuss_code", sa.String(20), nullable=False, unique=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("default_price", sa.Numeric(10, 2)),
        sa.Column("active", sa.Boolean, server_default="true"),
    )

    # ── Treatment Plans ────────────────────────────────────
    op.create_table(
        "treatment_plans",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", sa.UUID, sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("provider_id", sa.UUID, sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("discount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("approved_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── Treatment Items ────────────────────────────────────
    op.create_table(
        "treatment_items",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("plan_id", sa.UUID, sa.ForeignKey("treatment_plans.id"), nullable=False),
        sa.Column("phase_number", sa.SmallInteger, nullable=False, server_default="1"),
        sa.Column("phase_name", sa.String(100)),
        sa.Column("procedure_id", sa.UUID, sa.ForeignKey("procedure_catalog.id")),
        sa.Column("tuss_code", sa.String(20)),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("tooth_number", sa.SmallInteger),
        sa.Column("surface", sa.String(20)),
        sa.Column("quantity", sa.SmallInteger, server_default="1"),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("executed_at", sa.DateTime(timezone=True)),
        sa.Column("executed_by", sa.UUID),
        sa.Column("sort_order", sa.SmallInteger, server_default="0"),
    )

    # ── Invoices ───────────────────────────────────────────
    op.create_table(
        "invoices",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", sa.UUID, sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("treatment_plan_id", sa.UUID, sa.ForeignKey("treatment_plans.id")),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── Installments ───────────────────────────────────────
    op.create_table(
        "installments",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("invoice_id", sa.UUID, sa.ForeignKey("invoices.id"), nullable=False),
        sa.Column("installment_number", sa.SmallInteger, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_method", sa.String(30)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
    )

    # ── Patient Timeline View (CQRS read model) ───────────
    op.create_table(
        "patient_timeline_view",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", sa.UUID, nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_id", sa.UUID, nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("provider_name", sa.String(255)),
        sa.Column("metadata", sa.JSON),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_timeline_patient", "patient_timeline_view", ["patient_id", "occurred_at"])


def downgrade() -> None:
    # Tenant tables
    op.drop_table("patient_timeline_view")
    op.drop_table("installments")
    op.drop_table("invoices")
    op.drop_table("treatment_items")
    op.drop_table("treatment_plans")
    op.drop_table("procedure_catalog")
    op.drop_table("consent_forms")
    op.drop_table("prescriptions")
    op.drop_table("clinical_notes")
    op.drop_table("odontogram_teeth")
    op.drop_table("anamnesis")
    op.drop_table("patient_records")
    op.drop_table("appointments")
    op.drop_table("blocked_slots")
    op.drop_table("provider_schedules")
    op.drop_table("providers")
    op.drop_table("patients")
    # Public tables
    op.drop_table("audit_log", schema="public")
    op.drop_table("tenant_memberships", schema="public")
    op.drop_table("users", schema="public")
    op.drop_table("tenants", schema="public")
