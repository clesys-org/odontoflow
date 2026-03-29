#!/usr/bin/env python3
"""Provisiona um novo tenant (clinica) no sistema.

Cria o schema no PostgreSQL e executa todas as migrations do tenant.

Uso:
    python scripts/create_tenant.py <slug> <nome_clinica>
    python scripts/create_tenant.py demo "Clinica Demo"
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from uuid import uuid4

import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://odontoflow:odontoflow@localhost:5432/odontoflow",
)

# Converte URL do SQLAlchemy para asyncpg format
DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


def sanitize_slug(slug: str) -> str:
    """Normaliza slug para uso como nome de schema PostgreSQL."""
    slug = slug.lower().strip()
    slug = re.sub(r"[^a-z0-9_]", "_", slug)
    return f"tenant_{slug}"


async def create_tenant(slug: str, clinic_name: str) -> None:
    schema_name = sanitize_slug(slug)
    tenant_id = uuid4()

    conn = await asyncpg.connect(DSN)
    try:
        # Verifica se slug ja existe
        existing = await conn.fetchval(
            "SELECT id FROM public.tenants WHERE slug = $1", slug
        )
        if existing:
            print(f"Tenant com slug '{slug}' ja existe (id={existing})")
            sys.exit(1)

        # Cria schema
        await conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
        print(f"Schema '{schema_name}' criado.")

        # Registra tenant na tabela publica
        await conn.execute(
            """
            INSERT INTO public.tenants (id, slug, name, schema_name, plan_tier, status)
            VALUES ($1, $2, $3, $4, 'trial', 'active')
            """,
            tenant_id, slug, clinic_name, schema_name,
        )
        print(f"Tenant registrado: id={tenant_id}, slug={slug}, name={clinic_name}")

        # Executa DDL das tabelas do tenant no novo schema
        # Lê a migration e executa apenas as tabelas tenant (sem schema= prefix)
        await conn.execute(f'SET search_path TO "{schema_name}", public')

        # Tabelas do tenant — replica a estrutura da migration 001
        tenant_ddl = """
        CREATE TABLE IF NOT EXISTS patients (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name VARCHAR(255) NOT NULL,
            cpf VARCHAR(14) UNIQUE,
            birth_date DATE,
            gender VARCHAR(20),
            phone VARCHAR(20),
            whatsapp VARCHAR(20),
            email VARCHAR(255),
            address JSONB,
            responsible JSONB,
            insurance_info JSONB,
            referral_source VARCHAR(100),
            tags TEXT[],
            lgpd_consent JSONB NOT NULL DEFAULT '{}',
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS providers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            cro_number VARCHAR(20),
            specialty VARCHAR(100),
            color VARCHAR(7),
            active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS provider_schedules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            provider_id UUID NOT NULL REFERENCES providers(id),
            working_hours JSONB NOT NULL,
            breaks JSONB DEFAULT '[]',
            overbooking_limit SMALLINT DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id UUID NOT NULL REFERENCES patients(id),
            provider_id UUID NOT NULL REFERENCES providers(id),
            start_at TIMESTAMPTZ NOT NULL,
            end_at TIMESTAMPTZ NOT NULL,
            duration_minutes SMALLINT NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'scheduled',
            appointment_type VARCHAR(50) NOT NULL,
            type_color VARCHAR(7),
            procedures_planned JSONB DEFAULT '[]',
            notes TEXT,
            source VARCHAR(30) DEFAULT 'receptionist',
            cancellation_reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS patient_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id UUID NOT NULL REFERENCES patients(id) UNIQUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS anamnesis (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_record_id UUID NOT NULL REFERENCES patient_records(id),
            chief_complaint TEXT,
            medical_history JSONB NOT NULL DEFAULT '{}',
            dental_history JSONB NOT NULL DEFAULT '{}',
            created_by UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            signed_at TIMESTAMPTZ,
            digital_signature JSONB
        );

        CREATE TABLE IF NOT EXISTS odontogram_teeth (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_record_id UUID NOT NULL REFERENCES patient_records(id),
            tooth_number SMALLINT NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'present',
            surfaces JSONB NOT NULL DEFAULT '[]',
            notes TEXT,
            updated_by UUID NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE(patient_record_id, tooth_number)
        );

        CREATE TABLE IF NOT EXISTS clinical_notes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_record_id UUID NOT NULL REFERENCES patient_records(id),
            note_type VARCHAR(30) NOT NULL,
            content TEXT NOT NULL,
            tooth_references SMALLINT[],
            attachments JSONB DEFAULT '[]',
            created_by UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            digital_signature JSONB
        );

        CREATE TABLE IF NOT EXISTS prescriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_record_id UUID NOT NULL REFERENCES patient_records(id),
            items JSONB NOT NULL,
            created_by UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS procedure_catalog (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tuss_code VARCHAR(20) NOT NULL UNIQUE,
            description VARCHAR(500) NOT NULL,
            category VARCHAR(100),
            default_price NUMERIC(10,2),
            active BOOLEAN DEFAULT true
        );

        CREATE TABLE IF NOT EXISTS treatment_plans (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id UUID NOT NULL REFERENCES patients(id),
            provider_id UUID NOT NULL REFERENCES providers(id),
            title VARCHAR(255) NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'draft',
            discount NUMERIC(10,2) DEFAULT 0,
            approved_at TIMESTAMPTZ,
            approved_by VARCHAR(255),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS treatment_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            plan_id UUID NOT NULL REFERENCES treatment_plans(id),
            phase_number SMALLINT NOT NULL DEFAULT 1,
            phase_name VARCHAR(100),
            procedure_id UUID REFERENCES procedure_catalog(id),
            tuss_code VARCHAR(20),
            description VARCHAR(500) NOT NULL,
            tooth_number SMALLINT,
            surface VARCHAR(20),
            quantity SMALLINT DEFAULT 1,
            unit_price NUMERIC(10,2) NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'pending',
            executed_at TIMESTAMPTZ,
            executed_by UUID,
            sort_order SMALLINT DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id UUID NOT NULL REFERENCES patients(id),
            treatment_plan_id UUID REFERENCES treatment_plans(id),
            total NUMERIC(10,2) NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'draft',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS installments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            invoice_id UUID NOT NULL REFERENCES invoices(id),
            installment_number SMALLINT NOT NULL,
            due_date DATE NOT NULL,
            amount NUMERIC(10,2) NOT NULL,
            payment_method VARCHAR(30),
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            paid_at TIMESTAMPTZ
        );

        CREATE TABLE IF NOT EXISTS patient_timeline_view (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id UUID NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            event_id UUID NOT NULL,
            summary TEXT NOT NULL,
            provider_name VARCHAR(255),
            metadata JSONB,
            occurred_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
        await conn.execute(tenant_ddl)
        print(f"Tabelas do tenant criadas no schema '{schema_name}'.")

        # Cria indices
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_appointments_provider_date
            ON "{schema_name}".appointments(provider_id, start_at);

            CREATE INDEX IF NOT EXISTS idx_appointments_patient
            ON "{schema_name}".appointments(patient_id);

            CREATE INDEX IF NOT EXISTS idx_timeline_patient
            ON "{schema_name}".patient_timeline_view(patient_id, occurred_at DESC);
        """)
        print("Indices criados.")

        print(f"\nTenant '{clinic_name}' provisionado com sucesso!")
        print(f"  ID:     {tenant_id}")
        print(f"  Slug:   {slug}")
        print(f"  Schema: {schema_name}")

    finally:
        await conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python scripts/create_tenant.py <slug> <nome_clinica>")
        print("Ex:  python scripts/create_tenant.py demo 'Clinica Demo'")
        sys.exit(1)

    asyncio.run(create_tenant(sys.argv[1], sys.argv[2]))
