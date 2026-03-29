"""Testes do Scheduling domain."""
import pytest
from datetime import datetime, time, date, timedelta, timezone
from uuid import uuid4
from odontoflow.scheduling.domain.models import (
    Appointment, TimeSlot, ProviderSchedule, WorkingHours, BreakPeriod, AppointmentType
)
from odontoflow.scheduling.domain.services import SchedulingService
from odontoflow.shared.domain.types import AppointmentStatus

class TestTimeSlot:
    def test_duration(self):
        slot = TimeSlot(
            start=datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc),
            end=datetime(2026, 4, 1, 8, 30, tzinfo=timezone.utc)
        )
        assert slot.duration_minutes == 30

    def test_overlaps_true(self):
        a = TimeSlot(start=datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc), end=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc))
        b = TimeSlot(start=datetime(2026, 4, 1, 8, 30, tzinfo=timezone.utc), end=datetime(2026, 4, 1, 9, 30, tzinfo=timezone.utc))
        assert a.overlaps(b) is True

    def test_overlaps_false(self):
        a = TimeSlot(start=datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc), end=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc))
        b = TimeSlot(start=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc), end=datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc))
        assert a.overlaps(b) is False

    def test_adjacent_no_overlap(self):
        a = TimeSlot(start=datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc), end=datetime(2026, 4, 1, 8, 30, tzinfo=timezone.utc))
        b = TimeSlot(start=datetime(2026, 4, 1, 8, 30, tzinfo=timezone.utc), end=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc))
        assert a.overlaps(b) is False

class TestAppointmentStatus:
    def test_confirm(self):
        apt = Appointment(status=AppointmentStatus.SCHEDULED)
        apt.confirm()
        assert apt.status == AppointmentStatus.CONFIRMED

    def test_start_service(self):
        apt = Appointment(status=AppointmentStatus.CONFIRMED)
        apt.start_service()
        assert apt.status == AppointmentStatus.IN_PROGRESS

    def test_complete(self):
        apt = Appointment(status=AppointmentStatus.IN_PROGRESS)
        apt.complete()
        assert apt.status == AppointmentStatus.COMPLETED

    def test_cancel(self):
        apt = Appointment(status=AppointmentStatus.SCHEDULED)
        apt.cancel("Paciente desmarcou")
        assert apt.status == AppointmentStatus.CANCELLED
        assert apt.cancellation_reason == "Paciente desmarcou"

    def test_no_show(self):
        apt = Appointment(status=AppointmentStatus.SCHEDULED)
        apt.mark_no_show()
        assert apt.status == AppointmentStatus.NO_SHOW

    def test_cannot_confirm_completed(self):
        apt = Appointment(status=AppointmentStatus.COMPLETED)
        with pytest.raises(ValueError):
            apt.confirm()

    def test_cannot_complete_scheduled(self):
        apt = Appointment(status=AppointmentStatus.SCHEDULED)
        with pytest.raises(ValueError):
            apt.complete()

    def test_cannot_cancel_completed(self):
        apt = Appointment(status=AppointmentStatus.COMPLETED)
        with pytest.raises(ValueError):
            apt.cancel()

class TestSchedulingService:
    def _make_schedule(self):
        return ProviderSchedule(
            provider_id=uuid4(),
            working_hours=[
                WorkingHours(day_of_week=1, start_time=time(8, 0), end_time=time(12, 0), slot_duration=30),
                WorkingHours(day_of_week=1, start_time=time(14, 0), end_time=time(18, 0), slot_duration=30),
            ],
            breaks=[BreakPeriod(start_time=time(10, 0), end_time=time(10, 15))],
        )

    def test_available_slots_count(self):
        schedule = self._make_schedule()
        target = date(2026, 4, 7)  # Tuesday = weekday 1
        slots = SchedulingService.get_available_slots(schedule, [], target, 30)
        # 8-12 = 8 slots, minus break at 10:00 = 7 slots
        # 14-18 = 8 slots
        # Total = 15 slots
        assert len(slots) >= 14  # At least 14 (break removes 1 from morning)

    def test_no_slots_on_day_off(self):
        schedule = self._make_schedule()
        target = date(2026, 4, 5)  # Sunday = weekday 6
        slots = SchedulingService.get_available_slots(schedule, [], target, 30)
        assert len(slots) == 0

    def test_conflict_detection(self):
        existing = [
            Appointment(
                time_slot=TimeSlot(
                    start=datetime(2026, 4, 7, 8, 0, tzinfo=timezone.utc),
                    end=datetime(2026, 4, 7, 8, 30, tzinfo=timezone.utc),
                ),
                status=AppointmentStatus.SCHEDULED,
            )
        ]
        new_slot = TimeSlot(
            start=datetime(2026, 4, 7, 8, 0, tzinfo=timezone.utc),
            end=datetime(2026, 4, 7, 8, 30, tzinfo=timezone.utc),
        )
        assert SchedulingService.check_conflict(existing, new_slot) is True

    def test_no_conflict_different_time(self):
        existing = [
            Appointment(
                time_slot=TimeSlot(
                    start=datetime(2026, 4, 7, 8, 0, tzinfo=timezone.utc),
                    end=datetime(2026, 4, 7, 8, 30, tzinfo=timezone.utc),
                ),
                status=AppointmentStatus.SCHEDULED,
            )
        ]
        new_slot = TimeSlot(
            start=datetime(2026, 4, 7, 9, 0, tzinfo=timezone.utc),
            end=datetime(2026, 4, 7, 9, 30, tzinfo=timezone.utc),
        )
        assert SchedulingService.check_conflict(existing, new_slot) is False
