"""Clinical Records — Domain Services."""
from __future__ import annotations

from odontoflow.clinical.domain.models import PatientRecord, Tooth, ToothSurface
from odontoflow.shared.domain.types import SurfaceCondition, SurfacePosition, ToothStatus

# FDI permanent teeth: quadrants 1-4, teeth 1-8 each
_PERMANENT_TEETH = []
for _q in (10, 20, 30, 40):
    _PERMANENT_TEETH.extend(range(_q + 1, _q + 9))


class OdontogramService:
    """Servico de dominio para odontograma completo."""

    @staticmethod
    def get_full_odontogram(record: PatientRecord) -> list[Tooth]:
        """Retorna todos os 32 dentes permanentes.

        Dentes que ja existem no prontuario sao retornados como estao.
        Dentes ausentes no prontuario recebem status PRESENT com todas
        as superficies HEALTHY como default.
        """
        existing_map = {t.tooth_number: t for t in record.teeth}

        default_surfaces = [
            ToothSurface(position=SurfacePosition.MESIAL, condition=SurfaceCondition.HEALTHY),
            ToothSurface(position=SurfacePosition.DISTAL, condition=SurfaceCondition.HEALTHY),
            ToothSurface(position=SurfacePosition.OCLUSAL, condition=SurfaceCondition.HEALTHY),
            ToothSurface(position=SurfacePosition.VESTIBULAR, condition=SurfaceCondition.HEALTHY),
            ToothSurface(position=SurfacePosition.LINGUAL, condition=SurfaceCondition.HEALTHY),
        ]

        result: list[Tooth] = []
        for num in _PERMANENT_TEETH:
            if num in existing_map:
                result.append(existing_map[num])
            else:
                result.append(
                    Tooth(
                        patient_record_id=record.id,
                        tooth_number=num,
                        status=ToothStatus.PRESENT,
                        surfaces=list(default_surfaces),
                    )
                )
        return result
