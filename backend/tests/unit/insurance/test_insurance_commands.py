"""Unit tests — Insurance application commands."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import NotFoundError, ValidationError
from odontoflow.insurance.application.commands.authorize_tiss import AuthorizeTISSCommand
from odontoflow.insurance.application.commands.bill_tiss import BillTISSCommand
from odontoflow.insurance.application.commands.record_tiss_payment import RecordTISSPaymentCommand
from odontoflow.insurance.application.commands.submit_tiss import (
    SubmitTISSCommand,
    TISSItemInput,
)
from odontoflow.insurance.domain.models import TISSStatus
from odontoflow.insurance.infrastructure.in_memory_insurance_repo import (
    InMemoryTISSRequestRepository,
)


@pytest.fixture
def repo():
    return InMemoryTISSRequestRepository()


class TestSubmitTISSCommand:
    @pytest.mark.asyncio
    async def test_submit_tiss(self, repo):
        cmd = SubmitTISSCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            provider_id=uuid4(),
            insurance_provider_id=uuid4(),
            items=[
                TISSItemInput(
                    tuss_code="81000065",
                    description="Restauracao em resina",
                    tooth_number=14,
                ),
            ],
        )

        request = await cmd.execute(repo)

        assert request.status == TISSStatus.PENDING
        assert request.submitted_at is not None
        assert len(request.items) == 1
        assert request.items[0].tuss_code == "81000065"

        # Verifica persistencia
        saved = await repo.get_by_id(request.id)
        assert saved is not None
        assert saved.id == request.id

    @pytest.mark.asyncio
    async def test_submit_empty_items_raises(self, repo):
        cmd = SubmitTISSCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            provider_id=uuid4(),
            insurance_provider_id=uuid4(),
            items=[],
        )
        with pytest.raises(ValidationError, match="ao menos um item"):
            await cmd.execute(repo)


class TestAuthorizeTISSCommand:
    @pytest.mark.asyncio
    async def test_authorize_tiss(self, repo):
        # Setup: submit first
        submit_cmd = SubmitTISSCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            provider_id=uuid4(),
            insurance_provider_id=uuid4(),
            items=[
                TISSItemInput(
                    tuss_code="81000065",
                    description="Restauracao em resina",
                ),
            ],
        )
        request = await submit_cmd.execute(repo)

        # Authorize
        auth_cmd = AuthorizeTISSCommand(
            request_id=request.id,
            authorization_number="AUTH-123456",
        )
        authorized = await auth_cmd.execute(repo)

        assert authorized.status == TISSStatus.AUTHORIZED
        assert authorized.authorization_number == "AUTH-123456"
        assert authorized.authorized_at is not None

    @pytest.mark.asyncio
    async def test_authorize_nonexistent_raises(self, repo):
        cmd = AuthorizeTISSCommand(
            request_id=uuid4(),
            authorization_number="AUTH-001",
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)


class TestRecordTISSPaymentCommand:
    @pytest.mark.asyncio
    async def test_full_flow_to_payment(self, repo):
        # Submit
        submit_cmd = SubmitTISSCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            provider_id=uuid4(),
            insurance_provider_id=uuid4(),
            items=[
                TISSItemInput(
                    tuss_code="81000065",
                    description="Restauracao em resina",
                ),
            ],
        )
        request = await submit_cmd.execute(repo)

        # Authorize
        auth_cmd = AuthorizeTISSCommand(
            request_id=request.id,
            authorization_number="AUTH-789",
        )
        await auth_cmd.execute(repo)

        # Bill
        bill_cmd = BillTISSCommand(request_id=request.id)
        await bill_cmd.execute(repo)

        # Payment
        pay_cmd = RecordTISSPaymentCommand(
            request_id=request.id,
            paid_amount_centavos=50000,
        )
        paid = await pay_cmd.execute(repo)

        assert paid.status == TISSStatus.PAID
        assert paid.paid_amount_centavos == 50000
        assert paid.paid_at is not None

    @pytest.mark.asyncio
    async def test_payment_with_glosa(self, repo):
        # Submit + Authorize + Bill
        submit_cmd = SubmitTISSCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            provider_id=uuid4(),
            insurance_provider_id=uuid4(),
            items=[
                TISSItemInput(
                    tuss_code="81000065",
                    description="Restauracao em resina",
                ),
            ],
        )
        request = await submit_cmd.execute(repo)
        await AuthorizeTISSCommand(
            request_id=request.id,
            authorization_number="AUTH-999",
        ).execute(repo)
        await BillTISSCommand(request_id=request.id).execute(repo)

        # Payment with glosa
        pay_cmd = RecordTISSPaymentCommand(
            request_id=request.id,
            paid_amount_centavos=30000,
            glosa_amount_centavos=20000,
            glosa_reason="Valor acima da tabela",
        )
        result = await pay_cmd.execute(repo)

        assert result.status == TISSStatus.GLOSA
        assert result.paid_amount_centavos == 30000
        assert result.glosa_amount_centavos == 20000
        assert result.glosa_reason == "Valor acima da tabela"

    @pytest.mark.asyncio
    async def test_payment_nonexistent_raises(self, repo):
        cmd = RecordTISSPaymentCommand(
            request_id=uuid4(),
            paid_amount_centavos=10000,
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)
