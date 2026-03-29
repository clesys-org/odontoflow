"""API Router: Scheduling endpoints."""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import (
    get_appointment_repo,
    get_current_user,
    get_event_bus,
    get_provider_schedule_repo,
)
from odontoflow.api.schemas.scheduling import (
    AppointmentResponse,
    AvailableSlotResponse,
    BookAppointmentRequest,
    DayScheduleResponse,
    ProviderResponse,
    ProviderScheduleRequest,
    UpdateStatusRequest,
)
from odontoflow.scheduling.application.commands.book_appointment import BookAppointmentCommand
from odontoflow.scheduling.application.commands.update_appointment_status import (
    UpdateAppointmentStatusCommand,
)
from odontoflow.scheduling.application.queries.get_available_slots import GetAvailableSlotsQuery
from odontoflow.scheduling.application.queries.get_day_schedule import GetDayScheduleQuery
from odontoflow.scheduling.domain.models import (
    Appointment,
    BreakPeriod,
    ProviderSchedule,
    WorkingHours,
)
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError
from odontoflow.shared.event_bus import EventBus

router = APIRouter(prefix="/api/v1", tags=["scheduling"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _appointment_to_response(appt: Appointment) -> AppointmentResponse:
    return AppointmentResponse(
        id=str(appt.id),
        patient_id=str(appt.patient_id),
        patient_name=appt.patient_name,
        provider_id=str(appt.provider_id),
        provider_name=appt.provider_name,
        start_at=appt.time_slot.start.isoformat() if appt.time_slot else "",
        end_at=appt.time_slot.end.isoformat() if appt.time_slot else "",
        duration_minutes=appt.time_slot.duration_minutes if appt.time_slot else 0,
        status=appt.status.value,
        appointment_type=appt.appointment_type.name,
        type_color=appt.appointment_type.color,
        notes=appt.notes,
        source=appt.source.value,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at.isoformat(),
    )


def _slot_to_response(slot) -> AvailableSlotResponse:
    return AvailableSlotResponse(
        start=slot.start.isoformat(),
        end=slot.end.isoformat(),
        duration_minutes=slot.duration_minutes,
    )


def _schedule_to_provider_response(schedule: ProviderSchedule) -> ProviderResponse:
    return ProviderResponse(
        id=str(schedule.provider_id),
        name=schedule.provider_name,
        cro_number=schedule.cro_number,
        specialty=schedule.specialty,
        color=schedule.color,
        active=True,
    )


# ---------------------------------------------------------------------------
# Appointment Endpoints
# ---------------------------------------------------------------------------


@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
async def book_appointment(
    req: BookAppointmentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
    schedule_repo=Depends(get_provider_schedule_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Agenda nova consulta."""
    try:
        start_at = datetime.fromisoformat(req.start_at)
    except ValueError:
        raise HTTPException(422, "start_at deve ser ISO 8601 valido")

    cmd = BookAppointmentCommand(
        tenant_id=current_user.tenant_id,
        patient_id=UUID(req.patient_id),
        provider_id=UUID(req.provider_id),
        start_at=start_at,
        duration_minutes=req.duration_minutes,
        appointment_type_name=req.appointment_type,
        appointment_type_color=req.type_color,
        notes=req.notes,
        procedures=req.procedures,
    )
    try:
        appointment = await cmd.execute(appointment_repo, schedule_repo, event_bus)
    except ConflictError as e:
        raise HTTPException(409, e.message)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _appointment_to_response(appointment)


@router.get("/appointments", response_model=list[AppointmentResponse])
async def list_appointments(
    date: str = Query(..., description="Data no formato YYYY-MM-DD"),
    provider_id: str | None = Query(None, description="Filtro por provider"),
    current_user: CurrentUser = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
    schedule_repo=Depends(get_provider_schedule_repo),
):
    """Lista agendamentos por data e provider."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(422, "Data deve ser YYYY-MM-DD")

    if provider_id:
        pid = UUID(provider_id)
        query = GetDayScheduleQuery(
            provider_id=pid,
            target_date=target_date,
        )
        result = await query.execute(appointment_repo, schedule_repo)
        return [_appointment_to_response(a) for a in result.appointments]

    # If no provider_id, get all providers and aggregate
    all_schedules = await schedule_repo.get_all()
    appointments = []
    for sched in all_schedules:
        query = GetDayScheduleQuery(
            provider_id=sched.provider_id,
            target_date=target_date,
        )
        result = await query.execute(appointment_repo, schedule_repo)
        appointments.extend(result.appointments)

    # Sort by start time
    appointments.sort(key=lambda a: a.time_slot.start if a.time_slot else a.created_at)
    return [_appointment_to_response(a) for a in appointments]


@router.get("/appointments/available-slots", response_model=list[AvailableSlotResponse])
async def get_available_slots(
    provider_id: str = Query(..., description="ID do provider"),
    date: str = Query(..., description="Data no formato YYYY-MM-DD"),
    duration: int = Query(30, description="Duracao em minutos"),
    current_user: CurrentUser = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
    schedule_repo=Depends(get_provider_schedule_repo),
):
    """Retorna slots disponiveis para agendamento."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(422, "Data deve ser YYYY-MM-DD")

    query = GetAvailableSlotsQuery(
        provider_id=UUID(provider_id),
        target_date=target_date,
        duration=duration,
    )
    slots = await query.execute(appointment_repo, schedule_repo)
    return [_slot_to_response(s) for s in slots]


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
):
    """Busca agendamento por ID."""
    appointment = await appointment_repo.get_by_id(appointment_id)
    if not appointment:
        raise HTTPException(404, "Agendamento nao encontrado")
    return _appointment_to_response(appointment)


@router.patch("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: UUID,
    req: UpdateStatusRequest,
    current_user: CurrentUser = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Atualiza status do agendamento (confirm, start, complete, cancel, no_show)."""
    cmd = UpdateAppointmentStatusCommand(
        appointment_id=appointment_id,
        action=req.action,
        reason=req.reason,
    )
    try:
        await cmd.execute(appointment_repo, event_bus)
    except NotFoundError:
        raise HTTPException(404, "Agendamento nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    # Return updated appointment
    appointment = await appointment_repo.get_by_id(appointment_id)
    return _appointment_to_response(appointment)


@router.delete("/appointments/{appointment_id}", status_code=204)
async def cancel_appointment(
    appointment_id: UUID,
    reason: str = Query("", description="Motivo do cancelamento"),
    current_user: CurrentUser = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Cancela agendamento com motivo."""
    cmd = UpdateAppointmentStatusCommand(
        appointment_id=appointment_id,
        action="cancel",
        reason=reason,
    )
    try:
        await cmd.execute(appointment_repo, event_bus)
    except NotFoundError:
        raise HTTPException(404, "Agendamento nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)


# ---------------------------------------------------------------------------
# Provider Endpoints
# ---------------------------------------------------------------------------


@router.get("/providers", response_model=list[ProviderResponse])
async def list_providers(
    current_user: CurrentUser = Depends(get_current_user),
    schedule_repo=Depends(get_provider_schedule_repo),
):
    """Lista todos os providers (dentistas)."""
    schedules = await schedule_repo.get_all()
    return [_schedule_to_provider_response(s) for s in schedules]


@router.get("/providers/{provider_id}/schedule")
async def get_provider_schedule(
    provider_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    schedule_repo=Depends(get_provider_schedule_repo),
):
    """Retorna configuracao de agenda do provider."""
    schedule = await schedule_repo.get_by_provider(provider_id)
    if not schedule:
        raise HTTPException(404, "Provider nao encontrado")

    return {
        "provider_id": str(schedule.provider_id),
        "provider_name": schedule.provider_name,
        "working_hours": [
            {
                "day_of_week": wh.day_of_week,
                "start_time": wh.start_time.isoformat(),
                "end_time": wh.end_time.isoformat(),
                "slot_duration": wh.slot_duration,
            }
            for wh in schedule.working_hours
        ],
        "breaks": [
            {
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
            }
            for b in schedule.breaks
        ],
        "overbooking_limit": schedule.overbooking_limit,
    }


@router.put("/providers/{provider_id}/schedule")
async def update_provider_schedule(
    provider_id: UUID,
    req: ProviderScheduleRequest,
    current_user: CurrentUser = Depends(get_current_user),
    schedule_repo=Depends(get_provider_schedule_repo),
):
    """Atualiza configuracao de agenda do provider."""
    from datetime import time as time_cls

    schedule = await schedule_repo.get_by_provider(provider_id)
    if not schedule:
        raise HTTPException(404, "Provider nao encontrado")

    # Parse working hours
    working_hours = []
    for wh in req.working_hours:
        working_hours.append(WorkingHours(
            day_of_week=wh["day_of_week"],
            start_time=time_cls.fromisoformat(wh["start_time"]),
            end_time=time_cls.fromisoformat(wh["end_time"]),
            slot_duration=wh.get("slot_duration", 30),
        ))

    # Parse breaks
    breaks = []
    for b in req.breaks:
        breaks.append(BreakPeriod(
            start_time=time_cls.fromisoformat(b["start_time"]),
            end_time=time_cls.fromisoformat(b["end_time"]),
        ))

    schedule.working_hours = working_hours
    schedule.breaks = breaks
    schedule.overbooking_limit = req.overbooking_limit

    await schedule_repo.update(schedule)

    return {"status": "ok", "provider_id": str(provider_id)}


# ---------------------------------------------------------------------------
# Day Schedule View
# ---------------------------------------------------------------------------


@router.get("/schedule/day/{date}", response_model=list[DayScheduleResponse])
async def get_day_view(
    date: str,
    current_user: CurrentUser = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
    schedule_repo=Depends(get_provider_schedule_repo),
):
    """Visao do dia para todos os providers."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(422, "Data deve ser YYYY-MM-DD")

    all_schedules = await schedule_repo.get_all()
    results = []

    for sched in all_schedules:
        query = GetDayScheduleQuery(
            provider_id=sched.provider_id,
            target_date=target_date,
        )
        result = await query.execute(appointment_repo, schedule_repo)
        results.append(DayScheduleResponse(
            date=str(target_date),
            provider_id=str(sched.provider_id),
            provider_name=sched.provider_name,
            appointments=[_appointment_to_response(a) for a in result.appointments],
            available_slots=[_slot_to_response(s) for s in result.available_slots],
        ))

    return results
