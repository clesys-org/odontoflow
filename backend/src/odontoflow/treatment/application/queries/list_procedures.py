"""Query — Listar procedimentos do catalogo."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from odontoflow.treatment.domain.models import ProcedureCatalog
from odontoflow.treatment.domain.repositories import ProcedureCatalogRepository


@dataclass
class ListProceduresQuery:
    """Input data para listagem de procedimentos."""

    category: Optional[str] = None

    async def execute(self, repo: ProcedureCatalogRepository) -> list[ProcedureCatalog]:
        return await repo.get_all(category=self.category)
