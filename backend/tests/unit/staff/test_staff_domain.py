"""Unit tests — Staff domain models."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.staff.domain.models import (
    CommissionRule,
    CommissionType,
    ProductionEntry,
    StaffMember,
)


class TestCommissionRule:
    def test_percentage_commission(self):
        rule = CommissionRule(
            procedure_category=None,
            commission_type=CommissionType.PERCENTAGE,
            value=30,
        )
        assert rule.calculate_commission(100000) == 30000

    def test_fixed_commission(self):
        rule = CommissionRule(
            procedure_category="ortodontia",
            commission_type=CommissionType.FIXED,
            value=5000,
        )
        assert rule.calculate_commission(100000) == 5000

    def test_zero_percentage(self):
        rule = CommissionRule(
            commission_type=CommissionType.PERCENTAGE,
            value=0,
        )
        assert rule.calculate_commission(100000) == 0


class TestStaffMember:
    def _make_member(self, **kwargs) -> StaffMember:
        defaults = dict(
            tenant_id=uuid4(),
            user_id=uuid4(),
            full_name="Dr. Ana Silva",
            cro_number="SP-12345",
            specialty="Ortodontia",
        )
        defaults.update(kwargs)
        return StaffMember(**defaults)

    def test_create_staff(self):
        member = self._make_member()
        assert member.full_name == "Dr. Ana Silva"
        assert member.cro_number == "SP-12345"
        assert member.active is True
        assert member.commission_rules == []

    def test_deactivate(self):
        member = self._make_member()
        member.deactivate()
        assert member.active is False

    def test_deactivate_already_inactive_raises(self):
        member = self._make_member(active=False)
        with pytest.raises(ValueError, match="ja esta inativo"):
            member.deactivate()

    def test_activate(self):
        member = self._make_member(active=False)
        member.activate()
        assert member.active is True

    def test_activate_already_active_raises(self):
        member = self._make_member()
        with pytest.raises(ValueError, match="ja esta ativo"):
            member.activate()

    def test_add_commission_rule(self):
        member = self._make_member()
        rule = CommissionRule(
            commission_type=CommissionType.PERCENTAGE,
            value=30,
        )
        member.add_commission_rule(rule)
        assert len(member.commission_rules) == 1

    def test_get_commission_general(self):
        member = self._make_member()
        member.add_commission_rule(CommissionRule(
            procedure_category=None,
            commission_type=CommissionType.PERCENTAGE,
            value=25,
        ))
        assert member.get_commission_for("qualquer", 100000) == 25000

    def test_get_commission_specific_overrides_general(self):
        member = self._make_member()
        member.add_commission_rule(CommissionRule(
            procedure_category=None,
            commission_type=CommissionType.PERCENTAGE,
            value=25,
        ))
        member.add_commission_rule(CommissionRule(
            procedure_category="ortodontia",
            commission_type=CommissionType.PERCENTAGE,
            value=40,
        ))
        assert member.get_commission_for("ortodontia", 100000) == 40000
        assert member.get_commission_for("clinica", 100000) == 25000

    def test_get_commission_no_rules_returns_zero(self):
        member = self._make_member()
        assert member.get_commission_for(None, 100000) == 0


class TestProductionEntry:
    def test_create_entry(self):
        entry = ProductionEntry(
            staff_id=uuid4(),
            tenant_id=uuid4(),
            procedure_description="Limpeza",
            revenue_centavos=15000,
            commission_centavos=4500,
            patient_name="Joao Silva",
        )
        assert entry.revenue_centavos == 15000
        assert entry.commission_centavos == 4500
