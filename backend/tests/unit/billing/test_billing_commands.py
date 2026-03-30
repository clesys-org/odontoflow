"""Unit tests — Billing application commands."""
from __future__ import annotations

import pytest
from datetime import date
from uuid import uuid4

from odontoflow.billing.application.commands.cancel_invoice import CancelInvoiceCommand
from odontoflow.billing.application.commands.create_invoice import (
    CreateInvoiceCommand,
    InstallmentInput,
)
from odontoflow.billing.application.commands.pay_installment import PayInstallmentCommand
from odontoflow.billing.infrastructure.in_memory_billing_repo import InMemoryInvoiceRepository
from odontoflow.shared.domain.errors import NotFoundError, ValidationError
from odontoflow.shared.domain.events import InvoicePaid
from odontoflow.shared.domain.types import InvoiceStatus, PaymentMethod


@pytest.fixture
def repo():
    return InMemoryInvoiceRepository()


class TestCreateInvoiceCommand:
    @pytest.mark.asyncio
    async def test_create_invoice(self, repo):
        cmd = CreateInvoiceCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            description="Tratamento completo",
            total_centavos=200000,
            installments=[
                InstallmentInput(number=1, due_date=date(2026, 4, 15), amount_centavos=100000),
                InstallmentInput(number=2, due_date=date(2026, 5, 15), amount_centavos=100000),
            ],
        )

        invoice = await cmd.execute(repo)

        assert invoice.description == "Tratamento completo"
        assert invoice.total_centavos == 200000
        assert invoice.status == InvoiceStatus.SENT
        assert len(invoice.installments) == 2

        saved = await repo.get_by_id(invoice.id)
        assert saved is not None

    @pytest.mark.asyncio
    async def test_create_invoice_empty_description_raises(self, repo):
        cmd = CreateInvoiceCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            description="",
            total_centavos=10000,
        )
        with pytest.raises(ValidationError, match="Descricao"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_create_invoice_zero_total_raises(self, repo):
        cmd = CreateInvoiceCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            description="Teste",
            total_centavos=0,
        )
        with pytest.raises(ValidationError, match="maior que zero"):
            await cmd.execute(repo)


class TestPayInstallmentCommand:
    @pytest.mark.asyncio
    async def test_pay_installment_publishes_event_on_full_payment(self, repo):
        # Setup: create invoice with 1 installment
        create_cmd = CreateInvoiceCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            description="Fatura unica",
            total_centavos=50000,
            installments=[
                InstallmentInput(number=1, due_date=date(2026, 4, 15), amount_centavos=50000),
            ],
        )
        invoice = await create_cmd.execute(repo)

        # Pay
        pay_cmd = PayInstallmentCommand(
            invoice_id=invoice.id,
            installment_number=1,
            payment_method=PaymentMethod.PIX,
        )
        paid_invoice = await pay_cmd.execute(repo)

        assert paid_invoice.status == InvoiceStatus.PAID

        events = paid_invoice.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], InvoicePaid)
        assert events[0].amount_centavos == 50000

    @pytest.mark.asyncio
    async def test_pay_nonexistent_invoice_raises(self, repo):
        cmd = PayInstallmentCommand(
            invoice_id=uuid4(),
            installment_number=1,
            payment_method=PaymentMethod.PIX,
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)


class TestCancelInvoiceCommand:
    @pytest.mark.asyncio
    async def test_cancel_invoice(self, repo):
        create_cmd = CreateInvoiceCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            description="Fatura a cancelar",
            total_centavos=30000,
            installments=[
                InstallmentInput(number=1, due_date=date(2026, 4, 15), amount_centavos=30000),
            ],
        )
        invoice = await create_cmd.execute(repo)

        cancel_cmd = CancelInvoiceCommand(invoice_id=invoice.id)
        cancelled = await cancel_cmd.execute(repo)

        assert cancelled.status == InvoiceStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_raises(self, repo):
        cmd = CancelInvoiceCommand(invoice_id=uuid4())
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)
