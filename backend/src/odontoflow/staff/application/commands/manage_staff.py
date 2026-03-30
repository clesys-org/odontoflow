"""Command — Gerenciar profissionais."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.staff.domain.models import CommissionRule, CommissionType, StaffMember
from odontoflow.staff.domain.repositories import StaffRepository


@dataclass
class CommissionRuleInput:
    procedure_category: Optional[str]
    commission_type: str
    value: int


@dataclass
class CreateStaffCommand:
    tenant_id: UUID
    user_id: UUID
    full_name: str
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    commission_rules: list[CommissionRuleInput] = None

    async def execute(self, repo: StaffRepository) -> StaffMember:
        rules = []
        if self.commission_rules:
            rules = [
                CommissionRule(
                    procedure_category=r.procedure_category,
                    commission_type=CommissionType(r.commission_type),
                    value=r.value,
                )
                for r in self.commission_rules
            ]

        member = StaffMember(
            id=uuid4(),
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            full_name=self.full_name,
            cro_number=self.cro_number,
            specialty=self.specialty,
            commission_rules=rules,
        )
        await repo.save(member)
        return member


@dataclass
class UpdateStaffCommand:
    staff_id: UUID
    full_name: Optional[str] = None
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    active: Optional[bool] = None
    commission_rules: Optional[list[CommissionRuleInput]] = None

    async def execute(self, repo: StaffRepository) -> StaffMember:
        member = await repo.get_by_id(self.staff_id)
        if not member:
            raise NotFoundError("StaffMember", str(self.staff_id))

        if self.full_name is not None:
            member.full_name = self.full_name
        if self.cro_number is not None:
            member.cro_number = self.cro_number
        if self.specialty is not None:
            member.specialty = self.specialty
        if self.active is not None:
            if self.active and not member.active:
                member.activate()
            elif not self.active and member.active:
                member.deactivate()
        if self.commission_rules is not None:
            member.commission_rules = [
                CommissionRule(
                    procedure_category=r.procedure_category,
                    commission_type=CommissionType(r.commission_type),
                    value=r.value,
                )
                for r in self.commission_rules
            ]

        await repo.update(member)
        return member
