"""Unit tests — Staff application commands."""
from __future__ import annotations

import pytest
from datetime import date
from uuid import uuid4

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.staff.application.commands.manage_staff import (
    CommissionRuleInput,
    CreateStaffCommand,
    UpdateStaffCommand,
)
from odontoflow.staff.application.commands.record_production import RecordProductionCommand
from odontoflow.staff.domain.models import CommissionRule, CommissionType
from odontoflow.staff.infrastructure.in_memory_staff_repo import (
    InMemoryProductionRepository,
    InMemoryStaffRepository,
)


@pytest.fixture
def staff_repo():
    return InMemoryStaffRepository()


@pytest.fixture
def production_repo():
    return InMemoryProductionRepository()


class TestCreateStaffCommand:
    @pytest.mark.asyncio
    async def test_create_staff(self, staff_repo):
        cmd = CreateStaffCommand(
            tenant_id=uuid4(),
            user_id=uuid4(),
            full_name="Dr. Ana Silva",
            cro_number="SP-12345",
            specialty="Ortodontia",
            commission_rules=[
                CommissionRuleInput(
                    procedure_category=None,
                    commission_type="PERCENTAGE",
                    value=30,
                )
            ],
        )
        member = await cmd.execute(staff_repo)
        assert member.full_name == "Dr. Ana Silva"
        assert member.cro_number == "SP-12345"
        assert len(member.commission_rules) == 1
        assert member.commission_rules[0].value == 30

    @pytest.mark.asyncio
    async def test_create_without_rules(self, staff_repo):
        cmd = CreateStaffCommand(
            tenant_id=uuid4(),
            user_id=uuid4(),
            full_name="Dr. Carlos",
        )
        member = await cmd.execute(staff_repo)
        assert member.commission_rules == []


class TestUpdateStaffCommand:
    @pytest.mark.asyncio
    async def test_update_name(self, staff_repo):
        create = CreateStaffCommand(
            tenant_id=uuid4(),
            user_id=uuid4(),
            full_name="Dr. Ana",
        )
        member = await create.execute(staff_repo)

        update = UpdateStaffCommand(
            staff_id=member.id,
            full_name="Dr. Ana Silva",
        )
        updated = await update.execute(staff_repo)
        assert updated.full_name == "Dr. Ana Silva"

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises(self, staff_repo):
        cmd = UpdateStaffCommand(staff_id=uuid4(), full_name="Dr. X")
        with pytest.raises(NotFoundError):
            await cmd.execute(staff_repo)

    @pytest.mark.asyncio
    async def test_deactivate_via_update(self, staff_repo):
        create = CreateStaffCommand(
            tenant_id=uuid4(),
            user_id=uuid4(),
            full_name="Dr. Ana",
        )
        member = await create.execute(staff_repo)

        update = UpdateStaffCommand(staff_id=member.id, active=False)
        updated = await update.execute(staff_repo)
        assert updated.active is False


class TestRecordProductionCommand:
    @pytest.mark.asyncio
    async def test_record_with_commission(self, staff_repo, production_repo):
        create = CreateStaffCommand(
            tenant_id=uuid4(),
            user_id=uuid4(),
            full_name="Dr. Ana",
            commission_rules=[
                CommissionRuleInput(
                    procedure_category=None,
                    commission_type="PERCENTAGE",
                    value=30,
                )
            ],
        )
        member = await create.execute(staff_repo)

        cmd = RecordProductionCommand(
            staff_id=member.id,
            tenant_id=member.tenant_id,
            procedure_description="Restauracao",
            revenue_centavos=50000,
            patient_name="Joao",
            date=date(2026, 3, 28),
        )
        entry = await cmd.execute(staff_repo, production_repo)
        assert entry.revenue_centavos == 50000
        assert entry.commission_centavos == 15000  # 30% de 50000

    @pytest.mark.asyncio
    async def test_record_nonexistent_staff_raises(self, staff_repo, production_repo):
        cmd = RecordProductionCommand(
            staff_id=uuid4(),
            tenant_id=uuid4(),
            procedure_description="Limpeza",
            revenue_centavos=10000,
            patient_name="Maria",
            date=date.today(),
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(staff_repo, production_repo)
