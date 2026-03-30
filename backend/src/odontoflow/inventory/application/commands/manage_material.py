"""Use case — Criar/atualizar material."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.inventory.domain.models import Material
from odontoflow.inventory.domain.repositories import MaterialRepository
from odontoflow.shared.domain.errors import NotFoundError, ValidationError


@dataclass
class ManageMaterialCommand:
    """Input data para criacao/atualizacao de material."""

    tenant_id: UUID = field(default=None)
    material_id: Optional[UUID] = None  # None = criar novo
    name: str = ""
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "un"
    min_stock: int = 0
    cost_centavos: int = 0
    supplier: Optional[str] = None

    async def execute(self, repo: MaterialRepository) -> Material:
        if not self.name or not self.name.strip():
            raise ValidationError("Nome do material e obrigatorio")

        if self.material_id:
            # Update existing
            material = await repo.get_by_id(self.material_id)
            if not material:
                raise NotFoundError("Material", str(self.material_id))
            material.name = self.name.strip()
            material.description = self.description
            material.category = self.category
            material.unit = self.unit
            material.min_stock = self.min_stock
            material.cost_centavos = self.cost_centavos
            material.supplier = self.supplier
            await repo.update(material)
            return material

        # Create new
        material = Material(
            tenant_id=self.tenant_id,
            name=self.name.strip(),
            description=self.description,
            category=self.category,
            unit=self.unit,
            min_stock=self.min_stock,
            cost_centavos=self.cost_centavos,
            supplier=self.supplier,
        )
        await repo.save(material)
        return material
