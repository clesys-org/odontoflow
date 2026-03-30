"""Unit tests — Treatment application commands."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.events import TreatmentItemCompleted, TreatmentPlanApproved
from odontoflow.shared.domain.types import TreatmentPlanStatus
from odontoflow.treatment.application.commands.approve_plan import ApprovePlanCommand
from odontoflow.treatment.application.commands.create_treatment_plan import (
    CreateTreatmentPlanCommand,
    TreatmentItemInput,
)
from odontoflow.treatment.application.commands.execute_item import ExecuteItemCommand
from odontoflow.treatment.domain.models import ItemStatus
from odontoflow.treatment.infrastructure.in_memory_treatment_repo import (
    InMemoryTreatmentPlanRepository,
)


@pytest.fixture
def repo():
    return InMemoryTreatmentPlanRepository()


class TestCreateTreatmentPlanCommand:
    @pytest.mark.asyncio
    async def test_create_plan(self, repo):
        cmd = CreateTreatmentPlanCommand(
            patient_id=uuid4(),
            provider_id=uuid4(),
            tenant_id=uuid4(),
            title="Tratamento endodontico",
            items=[
                TreatmentItemInput(
                    tuss_code="81000111",
                    description="Tratamento de canal",
                    unit_price_centavos=80000,
                ),
            ],
        )

        plan = await cmd.execute(repo)

        assert plan.title == "Tratamento endodontico"
        assert plan.status == TreatmentPlanStatus.DRAFT
        assert len(plan.items) == 1
        assert plan.items[0].tuss_code == "81000111"

        # Verifica persistencia
        saved = await repo.get_by_id(plan.id)
        assert saved is not None
        assert saved.id == plan.id

    @pytest.mark.asyncio
    async def test_create_plan_empty_title_raises(self, repo):
        from odontoflow.shared.domain.errors import ValidationError

        cmd = CreateTreatmentPlanCommand(
            patient_id=uuid4(),
            provider_id=uuid4(),
            tenant_id=uuid4(),
            title="",
        )
        with pytest.raises(ValidationError, match="Titulo"):
            await cmd.execute(repo)


class TestApprovePlanCommand:
    @pytest.mark.asyncio
    async def test_approve_plan_publishes_event(self, repo):
        # Setup: create plan first
        create_cmd = CreateTreatmentPlanCommand(
            patient_id=uuid4(),
            provider_id=uuid4(),
            tenant_id=uuid4(),
            title="Plano completo",
            items=[
                TreatmentItemInput(
                    tuss_code="81000065",
                    description="Restauracao",
                    unit_price_centavos=15000,
                ),
            ],
        )
        plan = await create_cmd.execute(repo)

        # Execute: approve
        approve_cmd = ApprovePlanCommand(
            plan_id=plan.id,
            approved_by="Paciente Joao",
        )
        approved_plan = await approve_cmd.execute(repo)

        assert approved_plan.status == TreatmentPlanStatus.APPROVED
        assert approved_plan.approved_by == "Paciente Joao"

        events = approved_plan.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TreatmentPlanApproved)
        assert events[0].plan_id == plan.id

    @pytest.mark.asyncio
    async def test_approve_nonexistent_raises(self, repo):
        from odontoflow.shared.domain.errors import NotFoundError

        cmd = ApprovePlanCommand(plan_id=uuid4(), approved_by="X")
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)


class TestExecuteItemCommand:
    @pytest.mark.asyncio
    async def test_execute_item_publishes_event(self, repo):
        # Setup: create and approve plan
        create_cmd = CreateTreatmentPlanCommand(
            patient_id=uuid4(),
            provider_id=uuid4(),
            tenant_id=uuid4(),
            title="Plano",
            items=[
                TreatmentItemInput(
                    tuss_code="81000065",
                    description="Restauracao",
                    unit_price_centavos=15000,
                ),
            ],
        )
        plan = await create_cmd.execute(repo)
        item_id = plan.items[0].id

        # Execute item
        exec_cmd = ExecuteItemCommand(
            plan_id=plan.id,
            item_id=item_id,
            executed_by="Dr. Silva",
        )
        updated_plan = await exec_cmd.execute(repo)

        executed = next(i for i in updated_plan.items if i.id == item_id)
        assert executed.status == ItemStatus.COMPLETED
        assert executed.executed_by == "Dr. Silva"

        events = updated_plan.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TreatmentItemCompleted)
        assert events[0].item_id == item_id
        assert events[0].procedure_code == "81000065"
