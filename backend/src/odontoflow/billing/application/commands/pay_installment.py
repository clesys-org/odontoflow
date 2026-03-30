"""Use case — Pagar parcela de fatura."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.billing.domain.models import Invoice
from odontoflow.billing.domain.repositories import InvoiceRepository
from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.shared.domain.types import PaymentMethod


@dataclass
class PayInstallmentCommand:
    """Input data para pagamento de parcela."""

    invoice_id: UUID = field(default=None)
    installment_number: int = 1
    payment_method: PaymentMethod = PaymentMethod.PIX

    async def execute(self, repo: InvoiceRepository) -> Invoice:
        invoice = await repo.get_by_id(self.invoice_id)
        if not invoice:
            raise NotFoundError("Invoice", str(self.invoice_id))

        invoice.pay_installment(self.installment_number, self.payment_method)
        await repo.update(invoice)
        return invoice
