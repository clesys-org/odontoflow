"""Unit tests — Insurance (TISS) domain models."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import ValidationError
from odontoflow.insurance.domain.models import (
    InsuranceProvider,
    TISSItem,
    TISSRequest,
    TISSStatus,
)


class TestTISSItem:
    def test_create_frozen_vo(self):
        item = TISSItem(
            tuss_code="81000065",
            description="Restauracao em resina",
            tooth_number=14,
            quantity=2,
        )
        assert item.tuss_code == "81000065"
        assert item.tooth_number == 14
        assert item.quantity == 2
        assert item.authorized_quantity is None

    def test_frozen_immutability(self):
        item = TISSItem(tuss_code="81000065", description="Restauracao")
        with pytest.raises(AttributeError):
            item.tuss_code = "changed"


class TestInsuranceProvider:
    def test_create_provider(self):
        provider = InsuranceProvider(
            tenant_id=uuid4(),
            name="Amil Dental",
            ans_code="326305",
        )
        assert provider.name == "Amil Dental"
        assert provider.ans_code == "326305"
        assert provider.active is True

    def test_deactivate(self):
        provider = InsuranceProvider(
            tenant_id=uuid4(),
            name="Amil Dental",
            ans_code="326305",
        )
        provider.deactivate()
        assert provider.active is False

    def test_activate(self):
        provider = InsuranceProvider(
            tenant_id=uuid4(),
            name="Amil Dental",
            ans_code="326305",
            active=False,
        )
        provider.activate()
        assert provider.active is True


class TestTISSRequest:
    def _make_request(self, **kwargs) -> TISSRequest:
        defaults = dict(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            provider_id=uuid4(),
            insurance_provider_id=uuid4(),
            items=[
                TISSItem(
                    tuss_code="81000065",
                    description="Restauracao em resina",
                    tooth_number=14,
                ),
            ],
        )
        defaults.update(kwargs)
        return TISSRequest(**defaults)

    # --- Submit ---

    def test_submit(self):
        req = self._make_request()
        req.submit()
        assert req.submitted_at is not None

    def test_submit_no_items_raises(self):
        req = self._make_request(items=[])
        with pytest.raises(ValidationError, match="ao menos um item"):
            req.submit()

    def test_submit_not_pending_raises(self):
        req = self._make_request(status=TISSStatus.AUTHORIZED)
        with pytest.raises(ValidationError, match="nao pode ser enviada"):
            req.submit()

    # --- Authorize ---

    def test_authorize(self):
        req = self._make_request()
        req.authorize("AUTH-123456")
        assert req.status == TISSStatus.AUTHORIZED
        assert req.authorization_number == "AUTH-123456"
        assert req.authorized_at is not None

    def test_authorize_empty_number_raises(self):
        req = self._make_request()
        with pytest.raises(ValidationError, match="autorizacao e obrigatorio"):
            req.authorize("")

    def test_authorize_wrong_status_raises(self):
        req = self._make_request(status=TISSStatus.BILLED)
        with pytest.raises(ValidationError, match="nao pode ser autorizada"):
            req.authorize("AUTH-123")

    # --- Deny ---

    def test_deny(self):
        req = self._make_request()
        req.deny("Procedimento nao coberto")
        assert req.status == TISSStatus.DENIED
        assert req.denied_reason == "Procedimento nao coberto"

    def test_deny_empty_reason_raises(self):
        req = self._make_request()
        with pytest.raises(ValidationError, match="Motivo da negativa"):
            req.deny("")

    def test_deny_wrong_status_raises(self):
        req = self._make_request(status=TISSStatus.AUTHORIZED)
        with pytest.raises(ValidationError, match="nao pode ser negada"):
            req.deny("Motivo")

    # --- Bill ---

    def test_bill(self):
        req = self._make_request(status=TISSStatus.AUTHORIZED)
        req.bill()
        assert req.status == TISSStatus.BILLED
        assert req.billed_at is not None

    def test_bill_wrong_status_raises(self):
        req = self._make_request()
        with pytest.raises(ValidationError, match="precisa estar AUTHORIZED"):
            req.bill()

    # --- Payment ---

    def test_record_payment_full(self):
        req = self._make_request(status=TISSStatus.BILLED)
        req.record_payment(paid_amount_centavos=50000)
        assert req.status == TISSStatus.PAID
        assert req.paid_amount_centavos == 50000
        assert req.paid_at is not None
        assert req.glosa_amount_centavos == 0

    def test_record_payment_with_glosa(self):
        req = self._make_request(status=TISSStatus.BILLED)
        req.record_payment(
            paid_amount_centavos=30000,
            glosa_amount_centavos=20000,
            glosa_reason="Procedimento duplicado",
        )
        assert req.status == TISSStatus.GLOSA
        assert req.paid_amount_centavos == 30000
        assert req.glosa_amount_centavos == 20000
        assert req.glosa_reason == "Procedimento duplicado"

    def test_record_payment_negative_raises(self):
        req = self._make_request(status=TISSStatus.BILLED)
        with pytest.raises(ValidationError, match="nao pode ser negativo"):
            req.record_payment(paid_amount_centavos=-100)

    def test_record_payment_wrong_status_raises(self):
        req = self._make_request(status=TISSStatus.AUTHORIZED)
        with pytest.raises(ValidationError, match="precisa estar BILLED"):
            req.record_payment(paid_amount_centavos=50000)

    # --- Full State Machine Flow ---

    def test_full_flow_pending_to_paid(self):
        req = self._make_request()
        req.submit()
        req.authorize("AUTH-001")
        req.bill()
        req.record_payment(paid_amount_centavos=50000)
        assert req.status == TISSStatus.PAID

    def test_full_flow_pending_to_glosa(self):
        req = self._make_request()
        req.submit()
        req.authorize("AUTH-002")
        req.bill()
        req.record_payment(
            paid_amount_centavos=30000,
            glosa_amount_centavos=20000,
            glosa_reason="Valor acima da tabela",
        )
        assert req.status == TISSStatus.GLOSA

    def test_full_flow_pending_to_denied(self):
        req = self._make_request()
        req.submit()
        req.deny("Carencia nao cumprida")
        assert req.status == TISSStatus.DENIED
