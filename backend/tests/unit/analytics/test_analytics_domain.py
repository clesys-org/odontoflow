"""Unit tests — Analytics domain models and KPI computation."""
from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from odontoflow.analytics.domain.models import ClinicReport, KPIType, KPIValue


class TestKPIValue:
    def test_create_kpi(self):
        kpi = KPIValue(
            kpi_type=KPIType.PATIENTS_ACTIVE,
            value=150,
            label="Pacientes Ativos",
            formatted_value="150",
            trend="up",
        )
        assert kpi.kpi_type == KPIType.PATIENTS_ACTIVE
        assert kpi.value == 150
        assert kpi.formatted_value == "150"
        assert kpi.trend == "up"

    def test_kpi_is_frozen(self):
        kpi = KPIValue(
            kpi_type=KPIType.REVENUE_MONTH,
            value=500000,
            label="Faturamento",
            formatted_value="R$ 5.000,00",
        )
        # frozen=True — nao pode alterar
        try:
            kpi.value = 999
            assert False, "Should have raised"
        except AttributeError:
            pass


class TestClinicReport:
    def test_create_report(self):
        kpis = [
            KPIValue(KPIType.PATIENTS_ACTIVE, 100, "Pacientes", "100"),
            KPIValue(KPIType.REVENUE_MONTH, 800000, "Receita", "R$ 8.000,00"),
        ]
        report = ClinicReport(
            tenant_id=uuid4(),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            kpis=kpis,
        )
        assert len(report.kpis) == 2
        assert report.period_start == date(2026, 3, 1)

    def test_get_kpi(self):
        kpis = [
            KPIValue(KPIType.PATIENTS_ACTIVE, 100, "Pacientes", "100"),
            KPIValue(KPIType.ATTENDANCE_RATE, 85.5, "Comparecimento", "85.5%"),
        ]
        report = ClinicReport(
            tenant_id=uuid4(),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            kpis=kpis,
        )
        kpi = report.get_kpi(KPIType.ATTENDANCE_RATE)
        assert kpi is not None
        assert kpi.value == 85.5

    def test_get_kpi_not_found(self):
        report = ClinicReport(
            tenant_id=uuid4(),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            kpis=[],
        )
        assert report.get_kpi(KPIType.REVENUE_MONTH) is None

    def test_kpi_types_enum(self):
        assert KPIType.PATIENTS_ACTIVE.value == "PATIENTS_ACTIVE"
        assert KPIType.CANCELLATION_RATE.value == "CANCELLATION_RATE"
        assert len(KPIType) == 8
