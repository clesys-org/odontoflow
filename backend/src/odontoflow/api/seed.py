"""Seed de dados demo — popula repos in-memory na inicializacao.

Roda automaticamente quando APP_ENV=development.
Cria: 1 clinica, 1 dentista, 10 pacientes, consultas, prontuario,
tratamentos, faturas, estoque, templates de comunicacao.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4

logger = logging.getLogger(__name__)

# IDs fixos para referencia cruzada
TENANT_ID = uuid4()
USER_ID = uuid4()
PROVIDER_ID = uuid4()


async def seed_demo_data() -> None:
    """Popula todos os repos com dados demo."""
    from odontoflow.api import deps

    logger.info("Seeding demo data...")

    await _seed_iam(deps)
    patient_ids = await _seed_patients(deps)
    await _seed_provider_schedule(deps)
    await _seed_appointments(deps, patient_ids)
    await _seed_clinical_records(deps, patient_ids)
    await _seed_procedures(deps)
    await _seed_treatments(deps, patient_ids)
    await _seed_invoices(deps, patient_ids)
    await _seed_inventory(deps)
    await _seed_staff(deps)
    await _seed_communication(deps)
    await _seed_website(deps)

    logger.info("Demo data seeded successfully! User: demo@odontoflow.com / demo1234")


async def _seed_iam(deps) -> None:
    from odontoflow.iam.domain.models import Tenant, TenantMembership, TenantStatus, User
    from odontoflow.iam.domain.services import PasswordService
    from odontoflow.shared.domain.types import PlanTier, UserRole

    user = User(
        id=USER_ID,
        email="demo@odontoflow.com",
        password_hash=PasswordService.hash_password("demo1234"),
        full_name="Dr. Carlos Silva",
    )
    await deps._user_repo.save(user)

    tenant = Tenant(
        id=TENANT_ID,
        slug="clinica-demo",
        name="Clinica Sorriso Demo",
        cnpj="12.345.678/0001-90",
        phone="11999990000",
        email="contato@clinicasorriso.com.br",
        plan_tier=PlanTier.PROFESSIONAL,
        schema_name="tenant_clinica_demo",
        status=TenantStatus.ACTIVE,
    )
    await deps._tenant_repo.save(tenant)

    membership = TenantMembership(
        user_id=USER_ID, tenant_id=TENANT_ID, role=UserRole.OWNER,
    )
    await deps._membership_repo.save(membership)


async def _seed_patients(deps) -> list:
    from odontoflow.patient.domain.models import Address, LGPDConsent, Patient, Responsible
    from odontoflow.shared.domain.types import ContactChannel, Gender, PatientStatus

    patients_data = [
        {"full_name": "Maria Oliveira Santos", "cpf": "52998224725", "birth_date": date(1985, 3, 15), "gender": Gender.FEMALE, "phone": "11987654321", "email": "maria.oliveira@email.com"},
        {"full_name": "Joao Pedro Almeida", "cpf": "11144477735", "birth_date": date(1990, 7, 22), "gender": Gender.MALE, "phone": "11976543210", "email": "joao.pedro@email.com"},
        {"full_name": "Ana Carolina Ferreira", "cpf": "98765432100", "birth_date": date(1978, 11, 8), "gender": Gender.FEMALE, "phone": "11965432109"},
        {"full_name": "Lucas Gabriel Silva", "cpf": "45678912300", "birth_date": date(2000, 1, 30), "gender": Gender.MALE, "phone": "11954321098", "email": "lucas.g@email.com"},
        {"full_name": "Beatriz Costa Lima", "cpf": "32165498700", "birth_date": date(1995, 5, 12), "gender": Gender.FEMALE, "phone": "11943210987"},
        {"full_name": "Rafael Souza Mendes", "cpf": "65432198700", "birth_date": date(1982, 9, 3), "gender": Gender.MALE, "phone": "11932109876", "email": "rafael.sm@email.com"},
        {"full_name": "Julia Santos Rodrigues", "cpf": "78912345600", "birth_date": date(2015, 4, 20), "gender": Gender.FEMALE, "phone": "11921098765"},
        {"full_name": "Pedro Henrique Barbosa", "cpf": "14725836900", "birth_date": date(1970, 12, 1), "gender": Gender.MALE, "phone": "11910987654"},
        {"full_name": "Camila Rocha Pereira", "cpf": "25836914700", "birth_date": date(1988, 6, 18), "gender": Gender.FEMALE, "phone": "11909876543", "email": "camila.rp@email.com"},
        {"full_name": "Gabriel Martins Neto", "cpf": "36914725800", "birth_date": date(1998, 2, 28), "gender": Gender.MALE, "phone": "11898765432"},
    ]

    ids = []
    now = datetime.now(timezone.utc)
    for i, data in enumerate(patients_data):
        p = Patient(
            tenant_id=TENANT_ID,
            full_name=data["full_name"],
            cpf=data["cpf"],
            birth_date=data["birth_date"],
            gender=data["gender"],
            phone=data["phone"],
            whatsapp=data["phone"],
            email=data.get("email"),
            preferred_channel=ContactChannel.WHATSAPP,
            address=Address(
                street=f"Rua das Flores, {100 + i * 10}",
                number=str(100 + i),
                neighborhood="Centro",
                city="Sao Paulo",
                state="SP",
                zip_code="01001000",
            ),
            responsible=Responsible(
                name="Helena Santos", cpf="99988877766", relationship="Mae", phone="11999887766",
            ) if data["birth_date"].year > 2008 else None,
            lgpd_consent=LGPDConsent(consented_at=now, consent_type="registration"),
            status=PatientStatus.ACTIVE,
            created_at=now - timedelta(days=30 - i * 3),
        )
        await deps._patient_repo.save(p)
        ids.append(p.id)

    return ids


async def _seed_provider_schedule(deps) -> None:
    from odontoflow.scheduling.domain.models import BreakPeriod, ProviderSchedule, WorkingHours

    schedule = ProviderSchedule(
        provider_id=PROVIDER_ID,
        tenant_id=TENANT_ID,
        provider_name="Dr. Carlos Silva",
        cro_number="SP-12345",
        specialty="Clinica Geral",
        color="#0d9488",
        working_hours=[
            WorkingHours(day_of_week=d, start_time=time(8, 0), end_time=time(12, 0), slot_duration=30)
            for d in range(5)  # Seg-Sex manha
        ] + [
            WorkingHours(day_of_week=d, start_time=time(14, 0), end_time=time(18, 0), slot_duration=30)
            for d in range(5)  # Seg-Sex tarde
        ],
        breaks=[BreakPeriod(start_time=time(10, 0), end_time=time(10, 15))],
    )
    await deps._provider_schedule_repo.save(schedule)


async def _seed_appointments(deps, patient_ids: list) -> None:
    from odontoflow.scheduling.domain.models import Appointment, AppointmentType, TimeSlot
    from odontoflow.shared.domain.types import AppointmentStatus

    today = date.today()
    types = [
        AppointmentType(name="Consulta", default_duration=30, color="#3b82f6"),
        AppointmentType(name="Retorno", default_duration=20, color="#22c55e"),
        AppointmentType(name="Avaliacao", default_duration=45, color="#f59e0b"),
        AppointmentType(name="Urgencia", default_duration=30, color="#ef4444"),
    ]
    statuses = [
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.COMPLETED,
    ]

    for i, pid in enumerate(patient_ids[:8]):
        day_offset = i % 5
        hour = 8 + (i % 8)
        apt_date = today + timedelta(days=day_offset - 2)
        start = datetime.combine(apt_date, time(hour, 0), tzinfo=timezone.utc)

        apt = Appointment(
            tenant_id=TENANT_ID,
            patient_id=pid,
            provider_id=PROVIDER_ID,
            time_slot=TimeSlot(start=start, end=start + timedelta(minutes=30)),
            status=statuses[i % len(statuses)],
            appointment_type=types[i % len(types)],
            patient_name=f"Paciente {i + 1}",
            provider_name="Dr. Carlos Silva",
        )
        await deps._appointment_repo.save(apt)


async def _seed_clinical_records(deps, patient_ids: list) -> None:
    from odontoflow.clinical.domain.models import (
        Anamnesis, ClinicalNote, PatientRecord, Prescription, PrescriptionItem, Tooth, ToothSurface,
    )
    from odontoflow.shared.domain.types import NoteType, SurfaceCondition, SurfacePosition, ToothStatus

    for i, pid in enumerate(patient_ids[:5]):
        record = PatientRecord(patient_id=pid, tenant_id=TENANT_ID)

        record.set_anamnesis(Anamnesis(
            patient_record_id=record.id,
            chief_complaint="Dor ao mastigar" if i % 2 == 0 else "Limpeza de rotina",
            medical_history={"allergies": ["Dipirona"] if i == 0 else [], "conditions": [], "medications": []},
            dental_history={"previous_treatments": ["Restauracao", "Limpeza"], "last_visit": "2025-06-15"},
            created_by=USER_ID,
        ))

        # Odontogram — alguns dentes com problemas
        conditions = [
            (11, ToothStatus.PRESENT, [(SurfacePosition.VESTIBULAR, SurfaceCondition.RESTORATION)]),
            (16, ToothStatus.PRESENT, [(SurfacePosition.OCLUSAL, SurfaceCondition.CARIES)]),
            (26, ToothStatus.PRESENT, [(SurfacePosition.MESIAL, SurfaceCondition.RESTORATION), (SurfacePosition.OCLUSAL, SurfaceCondition.RESTORATION)]),
            (36, ToothStatus.ABSENT, []),
            (46, ToothStatus.PRESENT, [(SurfacePosition.OCLUSAL, SurfaceCondition.CROWN)]),
        ]
        for tooth_num, status, surfaces in conditions:
            record.update_tooth(
                tooth_number=tooth_num,
                status=status,
                surfaces=[ToothSurface(position=pos, condition=cond) for pos, cond in surfaces],
                notes=None,
                updated_by=USER_ID,
            )

        record.add_note(ClinicalNote(
            patient_record_id=record.id,
            note_type=NoteType.EVOLUTION,
            content=f"Paciente apresentou-se para avaliacao. Exame clinico realizado. Odontograma atualizado.",
            tooth_references=[16, 26],
            created_by=USER_ID,
        ))

        if i < 3:
            record.add_prescription(Prescription(
                patient_record_id=record.id,
                items=[
                    PrescriptionItem(medication_name="Ibuprofeno 600mg", dosage="1 comprimido", frequency="8/8h", duration="3 dias", instructions="Tomar apos refeicoes"),
                    PrescriptionItem(medication_name="Amoxicilina 500mg", dosage="1 capsula", frequency="8/8h", duration="7 dias", instructions=""),
                ],
                created_by=USER_ID,
            ))

        await deps._clinical_repo.save_record(record)


async def _seed_procedures(deps) -> None:
    from odontoflow.treatment.domain.models import ProcedureCatalog

    procedures = [
        ("81000030", "Consulta odontologica", "Consulta", 15000),
        ("81000065", "Urgencia/emergencia", "Consulta", 20000),
        ("82000034", "Restauracao resina 1 face", "Restauracao", 18000),
        ("82000042", "Restauracao resina 2 faces", "Restauracao", 25000),
        ("82000050", "Restauracao resina 3 faces", "Restauracao", 30000),
        ("83000031", "Exodontia simples", "Cirurgia", 25000),
        ("84000038", "Tratamento endodontico 1 canal", "Endodontia", 80000),
        ("84000046", "Tratamento endodontico 2 canais", "Endodontia", 100000),
        ("85000035", "Raspagem sub-gengival", "Periodontia", 15000),
        ("85000043", "Profilaxia (limpeza)", "Prevencao", 12000),
        ("86000032", "Coroa metaloceramica", "Protese", 120000),
        ("87000028", "Protese total", "Protese", 250000),
        ("88000025", "Clareamento dental", "Estetica", 80000),
        ("89000022", "Aplicacao de fluor", "Prevencao", 8000),
        ("90000019", "Radiografia periapical", "Diagnostico", 5000),
    ]

    for tuss, desc, cat, price in procedures:
        proc = ProcedureCatalog(
            tuss_code=tuss, description=desc, category=cat,
            default_price_centavos=price, active=True,
        )
        await deps._procedure_catalog_repo.save(proc)


async def _seed_treatments(deps, patient_ids: list) -> None:
    from odontoflow.treatment.domain.models import TreatmentItem, TreatmentPlan
    from odontoflow.shared.domain.types import TreatmentPlanStatus

    now = datetime.now(timezone.utc)

    # Plano 1: aprovado, em andamento
    plan1 = TreatmentPlan(
        patient_id=patient_ids[0],
        provider_id=PROVIDER_ID,
        tenant_id=TENANT_ID,
        title="Tratamento restaurador completo",
        status=TreatmentPlanStatus.IN_PROGRESS,
        approved_at=now - timedelta(days=15),
        approved_by="Maria Oliveira Santos",
    )
    plan1.add_item(TreatmentItem(
        plan_id=plan1.id, phase_number=1, phase_name="Fase 1 - Restauracoes",
        tuss_code="82000034", description="Restauracao resina 1 face - dente 16",
        tooth_number=16, quantity=1, unit_price_centavos=18000,
    ))
    plan1.add_item(TreatmentItem(
        plan_id=plan1.id, phase_number=1, phase_name="Fase 1 - Restauracoes",
        tuss_code="82000042", description="Restauracao resina 2 faces - dente 26",
        tooth_number=26, quantity=1, unit_price_centavos=25000,
    ))
    plan1.add_item(TreatmentItem(
        plan_id=plan1.id, phase_number=2, phase_name="Fase 2 - Prevencao",
        tuss_code="85000043", description="Profilaxia (limpeza)",
        quantity=1, unit_price_centavos=12000,
    ))
    await deps._treatment_plan_repo.save(plan1)

    # Plano 2: proposto, aguardando aprovacao
    plan2 = TreatmentPlan(
        patient_id=patient_ids[1],
        provider_id=PROVIDER_ID,
        tenant_id=TENANT_ID,
        title="Tratamento endodontico + coroa",
        status=TreatmentPlanStatus.PROPOSED,
    )
    plan2.add_item(TreatmentItem(
        plan_id=plan2.id, phase_number=1, phase_name="Fase 1 - Endodontia",
        tuss_code="84000038", description="Tratamento de canal - dente 46",
        tooth_number=46, quantity=1, unit_price_centavos=80000,
    ))
    plan2.add_item(TreatmentItem(
        plan_id=plan2.id, phase_number=2, phase_name="Fase 2 - Protese",
        tuss_code="86000032", description="Coroa metaloceramica - dente 46",
        tooth_number=46, quantity=1, unit_price_centavos=120000,
    ))
    await deps._treatment_plan_repo.save(plan2)


async def _seed_invoices(deps, patient_ids: list) -> None:
    from odontoflow.billing.domain.models import Installment, Invoice
    from odontoflow.shared.domain.types import InstallmentStatus, InvoiceStatus, PaymentMethod

    now = datetime.now(timezone.utc)
    today = date.today()

    # Fatura 1: parcialmente paga
    inv1 = Invoice(
        patient_id=patient_ids[0], tenant_id=TENANT_ID,
        description="Tratamento restaurador - Maria Oliveira",
        total_centavos=55000,
        status=InvoiceStatus.PARTIAL,
    )
    inv1.add_installment(Installment(
        invoice_id=inv1.id, number=1, due_date=today - timedelta(days=15),
        amount_centavos=18334, status=InstallmentStatus.PAID,
        payment_method=PaymentMethod.PIX, paid_at=now - timedelta(days=14),
    ))
    inv1.add_installment(Installment(
        invoice_id=inv1.id, number=2, due_date=today + timedelta(days=15),
        amount_centavos=18333, status=InstallmentStatus.PENDING,
    ))
    inv1.add_installment(Installment(
        invoice_id=inv1.id, number=3, due_date=today + timedelta(days=45),
        amount_centavos=18333, status=InstallmentStatus.PENDING,
    ))
    await deps._invoice_repo.save(inv1)

    # Fatura 2: paga
    inv2 = Invoice(
        patient_id=patient_ids[2], tenant_id=TENANT_ID,
        description="Profilaxia - Ana Carolina",
        total_centavos=12000,
        status=InvoiceStatus.PAID,
    )
    inv2.add_installment(Installment(
        invoice_id=inv2.id, number=1, due_date=today - timedelta(days=5),
        amount_centavos=12000, status=InstallmentStatus.PAID,
        payment_method=PaymentMethod.CREDIT_CARD, paid_at=now - timedelta(days=5),
    ))
    await deps._invoice_repo.save(inv2)


async def _seed_inventory(deps) -> None:
    from odontoflow.inventory.domain.models import Material, Supplier

    materials = [
        ("Resina composta A2", "Restauracao", "un", 50, 10, 4500),
        ("Resina composta A3", "Restauracao", "un", 30, 10, 4500),
        ("Anestesico Lidocaina 2%", "Anestesia", "cx", 20, 5, 8000),
        ("Agulha Gengival curta", "Anestesia", "cx", 15, 5, 3500),
        ("Luva procedimento M", "Descartavel", "cx", 8, 3, 2500),
        ("Mascara descartavel", "Descartavel", "cx", 12, 5, 1800),
        ("Sugador descartavel", "Descartavel", "pct", 25, 10, 1200),
        ("Fio de sutura 4-0", "Cirurgia", "un", 40, 15, 800),
        ("Pasta profilatica", "Prevencao", "un", 10, 3, 3200),
        ("Fluor gel", "Prevencao", "un", 8, 3, 2800),
    ]

    for name, cat, unit, stock, min_stock, cost in materials:
        m = Material(
            tenant_id=TENANT_ID, name=name, category=cat, unit=unit,
            current_stock=stock, min_stock=min_stock, cost_centavos=cost,
        )
        await deps._material_repo.save(m)

    supplier = Supplier(
        tenant_id=TENANT_ID, name="Dental Cremer",
        phone="08007011818", email="vendas@dentalcremer.com.br",
        notes="Fornecedor principal - entrega em 3 dias uteis",
    )
    await deps._supplier_repo.save(supplier)


async def _seed_staff(deps) -> None:
    from odontoflow.staff.domain.models import CommissionRule, CommissionType, StaffMember

    staff = StaffMember(
        tenant_id=TENANT_ID, user_id=USER_ID,
        full_name="Dr. Carlos Silva",
        cro_number="SP-12345", specialty="Clinica Geral",
        commission_rules=[
            CommissionRule(procedure_category=None, commission_type=CommissionType.PERCENTAGE, value=40),
        ],
    )
    await deps._staff_repo.save(staff)


async def _seed_communication(deps) -> None:
    from odontoflow.communication.domain.models import MessageChannel, MessageTemplate, MessageType

    templates = [
        ("Lembrete de Consulta", MessageType.APPOINTMENT_REMINDER, MessageChannel.WHATSAPP,
         "Ola {{patient_name}}! Lembramos que sua consulta esta marcada para {{date}} as {{time}}. Clinica Sorriso Demo."),
        ("Confirmacao de Consulta", MessageType.APPOINTMENT_CONFIRMATION, MessageChannel.WHATSAPP,
         "{{patient_name}}, sua consulta foi confirmada para {{date}} as {{time}}. Ate la! Clinica Sorriso Demo."),
        ("Aniversario", MessageType.BIRTHDAY_GREETING, MessageChannel.WHATSAPP,
         "Feliz aniversario, {{patient_name}}! A Clinica Sorriso Demo deseja um dia cheio de sorrisos! 🎂"),
        ("Recall Retorno", MessageType.RECALL_CHECKUP, MessageChannel.WHATSAPP,
         "Ola {{patient_name}}, ja faz 6 meses desde sua ultima consulta. Que tal agendar um retorno? Ligue: (11) 99999-0000"),
    ]

    for name, msg_type, channel, content in templates:
        t = MessageTemplate(
            tenant_id=TENANT_ID, name=name, message_type=msg_type,
            channel=channel, content=content,
        )
        await deps._message_template_repo.save(t)


async def _seed_website(deps) -> None:
    from odontoflow.website.domain.models import ClinicWebsite, ServiceItem

    website = ClinicWebsite(
        tenant_id=TENANT_ID,
        clinic_name="Clinica Sorriso Demo",
        slug="clinica-demo",
        tagline="Seu sorriso e nossa prioridade",
        description="Clinica odontologica completa com atendimento humanizado. Mais de 15 anos de experiencia.",
        phone="11999990000",
        whatsapp="11999990000",
        email="contato@clinicasorriso.com.br",
        address="Rua das Flores, 100 - Centro - Sao Paulo/SP",
        primary_color="#0d9488",
        services=[
            ServiceItem(name="Clinica Geral", description="Restauracoes, limpezas e check-ups"),
            ServiceItem(name="Endodontia", description="Tratamento de canal"),
            ServiceItem(name="Protese", description="Coroas, pontes e proteses"),
            ServiceItem(name="Estetica", description="Clareamento e facetas"),
            ServiceItem(name="Cirurgia", description="Exodontias e implantes"),
            ServiceItem(name="Ortodontia", description="Aparelhos fixos e alinhadores"),
        ],
        working_hours_text="Seg-Sex 8h-18h | Sab 8h-12h",
        social_links={"instagram": "@clinicasorriso", "facebook": "clinicasorrisodemo"},
        seo_title="Clinica Sorriso Demo - Dentista em Sao Paulo",
        seo_description="Clinica odontologica completa em SP. Restauracoes, canal, protese, estetica. Agende sua consulta!",
        booking_enabled=True,
        published=True,
    )
    await deps._website_repo.save(website)
