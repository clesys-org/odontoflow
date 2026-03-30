"""Unit tests — Inventory domain models."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import ValidationError
from odontoflow.inventory.domain.models import (
    Material,
    StockMovement,
    StockMovementType,
    Supplier,
)


class TestMaterial:
    def _make_material(self, **kwargs) -> Material:
        defaults = dict(
            tenant_id=uuid4(),
            name="Resina Composta Z350",
            category="Restauracao",
            unit="un",
            current_stock=10,
            min_stock=5,
            cost_centavos=15000,
        )
        defaults.update(kwargs)
        return Material(**defaults)

    def test_create_material(self):
        mat = self._make_material()
        assert mat.name == "Resina Composta Z350"
        assert mat.current_stock == 10
        assert mat.min_stock == 5
        assert mat.active is True

    def test_is_low_stock_false(self):
        mat = self._make_material(current_stock=10, min_stock=5)
        assert mat.is_low_stock is False

    def test_is_low_stock_true(self):
        mat = self._make_material(current_stock=3, min_stock=5)
        assert mat.is_low_stock is True

    def test_is_low_stock_equal_is_false(self):
        mat = self._make_material(current_stock=5, min_stock=5)
        assert mat.is_low_stock is False

    # --- Add Stock ---

    def test_add_stock(self):
        mat = self._make_material(current_stock=10)
        movement = mat.add_stock(5, "Compra fornecedor")
        assert mat.current_stock == 15
        assert isinstance(movement, StockMovement)
        assert movement.movement_type == StockMovementType.ENTRY
        assert movement.quantity == 5
        assert movement.reason == "Compra fornecedor"

    def test_add_stock_zero_raises(self):
        mat = self._make_material()
        with pytest.raises(ValidationError, match="maior que zero"):
            mat.add_stock(0, "Motivo")

    def test_add_stock_negative_raises(self):
        mat = self._make_material()
        with pytest.raises(ValidationError, match="maior que zero"):
            mat.add_stock(-1, "Motivo")

    def test_add_stock_empty_reason_raises(self):
        mat = self._make_material()
        with pytest.raises(ValidationError, match="Motivo"):
            mat.add_stock(5, "")

    # --- Remove Stock ---

    def test_remove_stock(self):
        mat = self._make_material(current_stock=10)
        movement = mat.remove_stock(3, "Uso em procedimento")
        assert mat.current_stock == 7
        assert movement.movement_type == StockMovementType.EXIT
        assert movement.quantity == 3

    def test_remove_stock_insufficient_raises(self):
        mat = self._make_material(current_stock=2)
        with pytest.raises(ValidationError, match="Estoque insuficiente"):
            mat.remove_stock(5, "Uso em procedimento")

    def test_remove_stock_zero_raises(self):
        mat = self._make_material()
        with pytest.raises(ValidationError, match="maior que zero"):
            mat.remove_stock(0, "Motivo")

    def test_remove_stock_empty_reason_raises(self):
        mat = self._make_material()
        with pytest.raises(ValidationError, match="Motivo"):
            mat.remove_stock(1, "")

    # --- Adjust Stock ---

    def test_adjust_stock_up(self):
        mat = self._make_material(current_stock=10)
        movement = mat.adjust_stock(15, "Contagem fisica")
        assert mat.current_stock == 15
        assert movement.movement_type == StockMovementType.ADJUSTMENT
        assert movement.quantity == 5  # diff

    def test_adjust_stock_down(self):
        mat = self._make_material(current_stock=10)
        movement = mat.adjust_stock(7, "Contagem fisica")
        assert mat.current_stock == 7
        assert movement.quantity == -3  # diff

    def test_adjust_stock_to_zero(self):
        mat = self._make_material(current_stock=10)
        movement = mat.adjust_stock(0, "Zerou estoque")
        assert mat.current_stock == 0
        assert movement.quantity == -10

    def test_adjust_stock_negative_raises(self):
        mat = self._make_material()
        with pytest.raises(ValidationError, match="nao pode ser negativa"):
            mat.adjust_stock(-1, "Motivo")

    def test_adjust_stock_empty_reason_raises(self):
        mat = self._make_material()
        with pytest.raises(ValidationError, match="Motivo"):
            mat.adjust_stock(10, "")

    # --- Deactivate ---

    def test_deactivate(self):
        mat = self._make_material()
        mat.deactivate()
        assert mat.active is False

    # --- Low stock alert after removal ---

    def test_low_stock_after_removal(self):
        mat = self._make_material(current_stock=6, min_stock=5)
        assert mat.is_low_stock is False
        mat.remove_stock(2, "Uso")
        assert mat.current_stock == 4
        assert mat.is_low_stock is True


class TestSupplier:
    def test_create_supplier(self):
        sup = Supplier(
            tenant_id=uuid4(),
            name="Dental Cremer",
            phone="11999999999",
            email="contato@dentalcremer.com.br",
            notes="Entrega em 3 dias uteis",
        )
        assert sup.name == "Dental Cremer"
        assert sup.phone == "11999999999"
        assert sup.email == "contato@dentalcremer.com.br"
