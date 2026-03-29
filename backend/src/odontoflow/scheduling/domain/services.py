"""Scheduling Domain Service — slot availability + conflict detection."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from odontoflow.scheduling.domain.models import (
    Appointment,
    ProviderSchedule,
    TimeSlot,
)
from odontoflow.shared.domain.types import AppointmentStatus


class SchedulingService:
    """Calcula slots disponiveis e detecta conflitos."""

    @staticmethod
    def get_available_slots(
        schedule: ProviderSchedule,
        existing_appointments: list[Appointment],
        target_date: date,
        duration: int = 30,
    ) -> list[TimeSlot]:
        """Retorna todos os slots disponiveis para um provider em uma data."""
        # Find working hours for this day of week
        day_of_week = target_date.weekday()
        day_hours = [wh for wh in schedule.working_hours if wh.day_of_week == day_of_week]

        if not day_hours:
            return []

        available = []

        for wh in day_hours:
            # Generate all possible slots
            slot_start = datetime.combine(target_date, wh.start_time, tzinfo=timezone.utc)
            day_end = datetime.combine(target_date, wh.end_time, tzinfo=timezone.utc)

            while slot_start + timedelta(minutes=duration) <= day_end:
                slot = TimeSlot(
                    start=slot_start,
                    end=slot_start + timedelta(minutes=duration),
                )

                # Check breaks
                in_break = False
                for brk in schedule.breaks:
                    break_start = datetime.combine(target_date, brk.start_time, tzinfo=timezone.utc)
                    break_end = datetime.combine(target_date, brk.end_time, tzinfo=timezone.utc)
                    break_slot = TimeSlot(start=break_start, end=break_end)
                    if slot.overlaps(break_slot):
                        in_break = True
                        break

                # Check blocked slots
                in_blocked = False
                if not in_break:
                    for blocked in schedule.blocked_slots:
                        if blocked.start_at and blocked.end_at:
                            blocked_slot = TimeSlot(start=blocked.start_at, end=blocked.end_at)
                            if slot.overlaps(blocked_slot):
                                in_blocked = True
                                break

                # Check existing appointments
                has_conflict = False
                if not in_break and not in_blocked:
                    has_conflict = SchedulingService.check_conflict(
                        existing_appointments, slot, schedule.overbooking_limit,
                    )

                if not in_break and not in_blocked and not has_conflict:
                    available.append(slot)

                slot_start += timedelta(minutes=wh.slot_duration or duration)

        return available

    @staticmethod
    def check_conflict(
        existing: list[Appointment],
        new_slot: TimeSlot,
        overbooking_limit: int = 0,
    ) -> bool:
        """Retorna True se ha conflito (slot ocupado alem do limite)."""
        active_statuses = {
            AppointmentStatus.SCHEDULED,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.IN_PROGRESS,
            AppointmentStatus.WAITING,
        }
        overlapping = [
            a for a in existing
            if a.time_slot and a.time_slot.overlaps(new_slot) and a.status in active_statuses
        ]
        return len(overlapping) > overbooking_limit
