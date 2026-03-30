"""Unit tests — Billing domain models."""
from __future__ import annotations

import pytest
from datetime import date
from uuid import uuid4

from odontoflow.billing.domain.models import Installment, Invoice
from odontoflow.shared.domain.errors import ValidationError
from odontoflow.shared.domain.events import InvoicePaid
from odontoflow.shared.domain.types import InstallmentStatus, InvoiceStatus, PaymentMethod


class TestInvoice:
    def _make_invoice(self, **kwargs) -> Invoice:
        defaults = dict(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            description="Tratamento ortodontico",
            total_centavos=100000,
            status=InvoiceStatus.SENT,
        )
        defaults.update(kwargs)
        return Invoice(**defaults)

    def _make_installment(self, **kwargs) -> Installment:
        defaults = dict(
            number=1,
            due_date=date(2026, 4, 15),
            amount_centavos=50000,
        )
        defaults.update(kwargs)
        return Installment(**defaults)

    def test_create_invoice(self):
        inv = self._make_invoice()
        assert inv.description == "Tratamento ortodontico"
        assert inv.total_centavos == 100000
        assert inv.status == InvoiceStatus.SENT
        assert inv.installments == []

    def test_add_installment(self):
        inv = self._make_invoice()
        inst = self._make_installment()
        inv.add_installment(inst)

        assert len(inv.installments) == 1
        assert inv.installments[0].invoice_id == inv.id

    def test_amount_paid_centavos(self):
        inv = self._make_invoice()
        inv.add_installment(
            self._make_installment(number=1, amount_centavos=50000, status=InstallmentStatus.PAID)
        )
        inv.add_installment(
            self._make_installment(number=2, amount_centavos=50000, status=InstallmentStatus.PENDING)
        )

        assert inv.amount_paid_centavos == 50000

    def test_amount_remaining_centavos(self):
        inv = self._make_invoice(total_centavos=100000)
        inv.add_installment(
            self._make_installment(number=1, amount_centavos=50000, status=InstallmentStatus.PAID)
        )
        inv.add_installment(
            self._make_installment(number=2, amount_centavos=50000, status=InstallmentStatus.PENDING)
        )

        assert inv.amount_remaining_centavos == 50000

    def test_pay_installment_partial(self):
        inv = self._make_invoice()
        inv.add_installment(self._make_installment(number=1, amount_centavos=50000))
        inv.add_installment(self._make_installment(number=2, amount_centavos=50000))

        result = inv.pay_installment(1, PaymentMethod.PIX)

        assert result.status == InstallmentStatus.PAID
        assert result.payment_method == PaymentMethod.PIX
        assert result.paid_at is not None
        assert inv.status == InvoiceStatus.PARTIAL

    def test_pay_all_installments_marks_paid(self):
        inv = self._make_invoice(total_centavos=100000)
        inv.add_installment(self._make_installment(number=1, amount_centavos=50000))
        inv.add_installment(self._make_installment(number=2, amount_centavos=50000))

        inv.pay_installment(1, PaymentMethod.PIX)
        inv.pay_installment(2, PaymentMethod.CREDIT_CARD)

        assert inv.status == InvoiceStatus.PAID

        events = inv.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], InvoicePaid)
        assert events[0].invoice_id == inv.id
        assert events[0].amount_centavos == 100000

    def test_pay_already_paid_raises(self):
        inv = self._make_invoice()
        inv.add_installment(
            self._make_installment(number=1, amount_centavos=50000, status=InstallmentStatus.PAID)
        )

        with pytest.raises(ValidationError, match="ja esta paga"):
            inv.pay_installment(1, PaymentMethod.PIX)

    def test_pay_nonexistent_installment_raises(self):
        inv = self._make_invoice()
        with pytest.raises(ValidationError, match="nao encontrada"):
            inv.pay_installment(99, PaymentMethod.PIX)

    def test_cancel(self):
        inv = self._make_invoice()
        inv.cancel()
        assert inv.status == InvoiceStatus.CANCELLED

    def test_cancel_paid_raises(self):
        inv = self._make_invoice(status=InvoiceStatus.PAID)
        with pytest.raises(ValidationError, match="nao pode ser cancelada"):
            inv.cancel()

    def test_cancel_already_cancelled_raises(self):
        inv = self._make_invoice(status=InvoiceStatus.CANCELLED)
        with pytest.raises(ValidationError, match="nao pode ser cancelada"):
            inv.cancel()

    def test_full_flow(self):
        """Fluxo completo: cria fatura, paga todas parcelas, verifica status PAID."""
        inv = self._make_invoice(total_centavos=90000)
        inv.add_installment(self._make_installment(number=1, amount_centavos=30000, due_date=date(2026, 4, 1)))
        inv.add_installment(self._make_installment(number=2, amount_centavos=30000, due_date=date(2026, 5, 1)))
        inv.add_installment(self._make_installment(number=3, amount_centavos=30000, due_date=date(2026, 6, 1)))

        assert inv.status == InvoiceStatus.SENT
        assert inv.amount_paid_centavos == 0
        assert inv.amount_remaining_centavos == 90000

        inv.pay_installment(1, PaymentMethod.PIX)
        assert inv.status == InvoiceStatus.PARTIAL
        assert inv.amount_paid_centavos == 30000

        inv.pay_installment(2, PaymentMethod.CREDIT_CARD)
        assert inv.status == InvoiceStatus.PARTIAL
        assert inv.amount_paid_centavos == 60000

        inv.pay_installment(3, PaymentMethod.CASH)
        assert inv.status == InvoiceStatus.PAID
        assert inv.amount_paid_centavos == 90000
        assert inv.amount_remaining_centavos == 0

        events = inv.collect_events()
        assert any(isinstance(e, InvoicePaid) for e in events)
