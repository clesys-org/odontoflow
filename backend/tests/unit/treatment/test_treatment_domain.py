"""Unit tests — Treatment domain models."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import ValidationError
from odontoflow.shared.domain.events import TreatmentItemCompleted, TreatmentPlanApproved
from odontoflow.shared.domain.types import TreatmentPlanStatus
from odontoflow.treatment.domain.models import (
    ItemStatus,
    ProcedureCatalog,
    TreatmentItem,
    TreatmentPlan,
)


class TestTreatmentPlan:
    def _make_plan(self, **kwargs) -> TreatmentPlan:
        defaults = dict(
            patient_id=uuid4(),
            provider_id=uuid4(),
            tenant_id=uuid4(),
            title="Tratamento ortodontico",
        )
        defaults.update(kwargs)
        return TreatmentPlan(**defaults)

    def _make_item(self, **kwargs) -> TreatmentItem:
        defaults = dict(
            tuss_code="81000065",
            description="Restauracao em resina",
            quantity=1,
            unit_price_centavos=15000,
        )
        defaults.update(kwargs)
        return TreatmentItem(**defaults)

    def test_create_plan(self):
        plan = self._make_plan()
        assert plan.title == "Tratamento ortodontico"
        assert plan.status == TreatmentPlanStatus.DRAFT
        assert plan.items == []
        assert plan.discount_centavos == 0

    def test_add_item(self):
        plan = self._make_plan()
        item = self._make_item()
        plan.add_item(item)

        assert len(plan.items) == 1
        assert plan.items[0].plan_id == plan.id

    def test_total_value_centavos(self):
        plan = self._make_plan(discount_centavos=5000)
        plan.add_item(self._make_item(unit_price_centavos=15000, quantity=2))
        plan.add_item(self._make_item(unit_price_centavos=10000, quantity=1))

        # (15000 * 2) + (10000 * 1) - 5000 = 35000
        assert plan.total_value_centavos == 35000

    def test_approve_from_draft(self):
        plan = self._make_plan()
        plan.approve(by="Dr. Silva")

        assert plan.status == TreatmentPlanStatus.APPROVED
        assert plan.approved_by == "Dr. Silva"
        assert plan.approved_at is not None

        events = plan.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TreatmentPlanApproved)
        assert events[0].plan_id == plan.id

    def test_approve_from_proposed(self):
        plan = self._make_plan(status=TreatmentPlanStatus.PROPOSED)
        plan.approve(by="Paciente")
        assert plan.status == TreatmentPlanStatus.APPROVED

    def test_approve_invalid_status(self):
        plan = self._make_plan(status=TreatmentPlanStatus.IN_PROGRESS)
        with pytest.raises(ValidationError):
            plan.approve(by="Dr. Silva")

    def test_start(self):
        plan = self._make_plan(status=TreatmentPlanStatus.APPROVED)
        plan.start()
        assert plan.status == TreatmentPlanStatus.IN_PROGRESS

    def test_start_invalid_status(self):
        plan = self._make_plan()
        with pytest.raises(ValidationError):
            plan.start()

    def test_complete_all_items_done(self):
        plan = self._make_plan(status=TreatmentPlanStatus.IN_PROGRESS)
        item = self._make_item(status=ItemStatus.COMPLETED)
        plan.add_item(item)

        plan.complete()
        assert plan.status == TreatmentPlanStatus.COMPLETED

    def test_complete_with_cancelled_items(self):
        plan = self._make_plan(status=TreatmentPlanStatus.IN_PROGRESS)
        plan.add_item(self._make_item(status=ItemStatus.COMPLETED))
        plan.add_item(self._make_item(status=ItemStatus.CANCELLED))

        plan.complete()
        assert plan.status == TreatmentPlanStatus.COMPLETED

    def test_complete_pending_items_raises(self):
        plan = self._make_plan(status=TreatmentPlanStatus.IN_PROGRESS)
        plan.add_item(self._make_item(status=ItemStatus.COMPLETED))
        plan.add_item(self._make_item(status=ItemStatus.PENDING))

        with pytest.raises(ValidationError, match="nao finalizados"):
            plan.complete()

    def test_cancel(self):
        plan = self._make_plan()
        plan.cancel()
        assert plan.status == TreatmentPlanStatus.CANCELLED

    def test_cancel_completed_raises(self):
        plan = self._make_plan(status=TreatmentPlanStatus.COMPLETED)
        with pytest.raises(ValidationError, match="concluido"):
            plan.cancel()

    def test_execute_item(self):
        plan = self._make_plan(status=TreatmentPlanStatus.IN_PROGRESS)
        item = self._make_item()
        plan.add_item(item)

        result = plan.execute_item(item.id, "Dr. Silva")

        assert result.status == ItemStatus.COMPLETED
        assert result.executed_by == "Dr. Silva"
        assert result.executed_at is not None

        events = plan.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], TreatmentItemCompleted)
        assert events[0].item_id == item.id

    def test_execute_item_not_found(self):
        plan = self._make_plan()
        with pytest.raises(ValidationError, match="nao encontrado"):
            plan.execute_item(uuid4(), "Dr. Silva")

    def test_execute_already_completed(self):
        plan = self._make_plan()
        item = self._make_item(status=ItemStatus.COMPLETED)
        plan.add_item(item)

        with pytest.raises(ValidationError, match="nao pode ser executado"):
            plan.execute_item(item.id, "Dr. Silva")

    def test_remove_item(self):
        plan = self._make_plan()
        item = self._make_item()
        plan.add_item(item)
        assert len(plan.items) == 1

        plan.remove_item(item.id)
        assert len(plan.items) == 0

    def test_remove_completed_item_raises(self):
        plan = self._make_plan()
        item = self._make_item(status=ItemStatus.COMPLETED)
        plan.add_item(item)

        with pytest.raises(ValidationError, match="ja executado"):
            plan.remove_item(item.id)


class TestProcedureCatalog:
    def test_create(self):
        proc = ProcedureCatalog(
            tuss_code="81000065",
            description="Restauracao em resina composta",
            category="Dentistica",
            default_price_centavos=15000,
        )
        assert proc.tuss_code == "81000065"
        assert proc.active is True

    def test_deactivate(self):
        proc = ProcedureCatalog(
            tuss_code="81000065",
            description="Restauracao em resina composta",
            category="Dentistica",
            default_price_centavos=15000,
        )
        proc.deactivate()
        assert proc.active is False
