"""Unit tests — Inventory application commands."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import NotFoundError, ValidationError
from odontoflow.inventory.application.commands.manage_material import ManageMaterialCommand
from odontoflow.inventory.application.commands.record_stock_movement import (
    RecordStockMovementCommand,
)
from odontoflow.inventory.domain.models import StockMovementType
from odontoflow.inventory.infrastructure.in_memory_inventory_repo import (
    InMemoryMaterialRepository,
)


@pytest.fixture
def repo():
    return InMemoryMaterialRepository()


class TestManageMaterialCommand:
    @pytest.mark.asyncio
    async def test_create_material(self, repo):
        cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            name="Resina Composta Z350",
            category="Restauracao",
            unit="un",
            min_stock=5,
            cost_centavos=15000,
            supplier="Dental Cremer",
        )

        material = await cmd.execute(repo)

        assert material.name == "Resina Composta Z350"
        assert material.category == "Restauracao"
        assert material.min_stock == 5
        assert material.current_stock == 0

        # Verifica persistencia
        saved = await repo.get_by_id(material.id)
        assert saved is not None
        assert saved.id == material.id

    @pytest.mark.asyncio
    async def test_create_material_empty_name_raises(self, repo):
        cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            name="",
        )
        with pytest.raises(ValidationError, match="Nome"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_update_material(self, repo):
        # Create first
        create_cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            name="Resina Composta",
            unit="un",
        )
        material = await create_cmd.execute(repo)

        # Update
        update_cmd = ManageMaterialCommand(
            tenant_id=material.tenant_id,
            material_id=material.id,
            name="Resina Composta Z350 XT",
            unit="un",
            min_stock=10,
            cost_centavos=18000,
        )
        updated = await update_cmd.execute(repo)

        assert updated.name == "Resina Composta Z350 XT"
        assert updated.min_stock == 10
        assert updated.cost_centavos == 18000

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises(self, repo):
        cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            material_id=uuid4(),
            name="Inexistente",
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)


class TestRecordStockMovementCommand:
    @pytest.mark.asyncio
    async def test_entry_movement(self, repo):
        # Create material
        create_cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            name="Luvas descartaveis",
            unit="cx",
        )
        material = await create_cmd.execute(repo)
        assert material.current_stock == 0

        # Add stock
        move_cmd = RecordStockMovementCommand(
            material_id=material.id,
            movement_type=StockMovementType.ENTRY,
            quantity=50,
            reason="Compra mensal",
            created_by=uuid4(),
        )
        updated, movement = await move_cmd.execute(repo)

        assert updated.current_stock == 50
        assert movement.movement_type == StockMovementType.ENTRY
        assert movement.quantity == 50

    @pytest.mark.asyncio
    async def test_exit_movement(self, repo):
        # Create material with stock
        create_cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            name="Luvas descartaveis",
            unit="cx",
        )
        material = await create_cmd.execute(repo)

        # Add stock first
        await RecordStockMovementCommand(
            material_id=material.id,
            movement_type=StockMovementType.ENTRY,
            quantity=50,
            reason="Compra",
            created_by=uuid4(),
        ).execute(repo)

        # Remove stock
        move_cmd = RecordStockMovementCommand(
            material_id=material.id,
            movement_type=StockMovementType.EXIT,
            quantity=10,
            reason="Uso em procedimento",
            created_by=uuid4(),
        )
        updated, movement = await move_cmd.execute(repo)

        assert updated.current_stock == 40
        assert movement.movement_type == StockMovementType.EXIT

    @pytest.mark.asyncio
    async def test_adjustment_movement(self, repo):
        create_cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            name="Agulhas",
            unit="un",
        )
        material = await create_cmd.execute(repo)

        # Add some stock
        await RecordStockMovementCommand(
            material_id=material.id,
            movement_type=StockMovementType.ENTRY,
            quantity=100,
            reason="Compra",
            created_by=uuid4(),
        ).execute(repo)

        # Adjust to 85 (found fewer in count)
        move_cmd = RecordStockMovementCommand(
            material_id=material.id,
            movement_type=StockMovementType.ADJUSTMENT,
            quantity=85,
            reason="Contagem fisica mensal",
            created_by=uuid4(),
        )
        updated, movement = await move_cmd.execute(repo)

        assert updated.current_stock == 85
        assert movement.movement_type == StockMovementType.ADJUSTMENT
        assert movement.quantity == -15  # diff from 100

    @pytest.mark.asyncio
    async def test_exit_insufficient_stock_raises(self, repo):
        create_cmd = ManageMaterialCommand(
            tenant_id=uuid4(),
            name="Fio de sutura",
            unit="un",
        )
        material = await create_cmd.execute(repo)

        move_cmd = RecordStockMovementCommand(
            material_id=material.id,
            movement_type=StockMovementType.EXIT,
            quantity=10,
            reason="Uso",
            created_by=uuid4(),
        )
        with pytest.raises(ValidationError, match="Estoque insuficiente"):
            await move_cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_movement_nonexistent_material_raises(self, repo):
        cmd = RecordStockMovementCommand(
            material_id=uuid4(),
            movement_type=StockMovementType.ENTRY,
            quantity=10,
            reason="Compra",
            created_by=uuid4(),
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)
