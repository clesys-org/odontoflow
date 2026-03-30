"""Use case — Gerenciar catalogo de procedimentos."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.shared.domain.errors import ConflictError, ValidationError
from odontoflow.treatment.domain.models import ProcedureCatalog
from odontoflow.treatment.domain.repositories import ProcedureCatalogRepository


@dataclass
class AddProcedureCommand:
    """Input data para adicionar procedimento ao catalogo."""

    tuss_code: str = ""
    description: str = ""
    category: str = ""
    default_price_centavos: int = 0

    async def execute(self, repo: ProcedureCatalogRepository) -> ProcedureCatalog:
        if not self.tuss_code or not self.tuss_code.strip():
            raise ValidationError("Codigo TUSS e obrigatorio.")
        if not self.description or not self.description.strip():
            raise ValidationError("Descricao e obrigatoria.")

        existing = await repo.get_by_tuss_code(self.tuss_code.strip())
        if existing:
            raise ConflictError(f"Procedimento com codigo TUSS {self.tuss_code} ja existe.")

        procedure = ProcedureCatalog(
            tuss_code=self.tuss_code.strip(),
            description=self.description.strip(),
            category=self.category.strip(),
            default_price_centavos=self.default_price_centavos,
        )

        await repo.save(procedure)
        return procedure
