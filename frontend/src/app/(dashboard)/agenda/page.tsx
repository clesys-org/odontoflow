"use client";

import { useState, useCallback, useMemo } from "react";
import { useApi } from "@/hooks/useApi";
import {
  fetchDaySchedule,
  fetchProviders,
  bookAppointment,
} from "@/lib/api/scheduling";
import type {
  AppointmentResponse,
  BookAppointmentRequest,
  ProviderResponse,
} from "@/lib/types/scheduling";
import AppointmentCard from "@/components/scheduling/AppointmentCard";
import BookingForm from "@/components/scheduling/BookingForm";

// --- helpers ---

function toDateString(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function formatDateBR(iso: string): string {
  const [y, m, d] = iso.split("-");
  const date = new Date(Number(y), Number(m) - 1, Number(d));
  return date.toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

function timeToMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

function minutesToTime(mins: number): string {
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

function isoToMinutes(iso: string): number {
  const d = new Date(iso);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

// --- constants ---

const GRID_START = 7 * 60; // 07:00
const GRID_END = 20 * 60; // 20:00
const SLOT_HEIGHT = 48; // px per 30min
const SLOT_INTERVAL = 30; // minutes

const STATUS_BG: Record<string, string> = {
  SCHEDULED: "bg-blue-50 border-blue-300",
  CONFIRMED: "bg-green-50 border-green-300",
  IN_PROGRESS: "bg-yellow-50 border-yellow-300",
  COMPLETED: "bg-gray-50 border-gray-300",
  CANCELLED: "bg-red-50 border-red-300",
  NO_SHOW: "bg-orange-50 border-orange-300",
  WAITING: "bg-purple-50 border-purple-300",
};

const LEGEND = [
  { status: "SCHEDULED", label: "Agendado", color: "bg-blue-400" },
  { status: "CONFIRMED", label: "Confirmado", color: "bg-green-400" },
  { status: "IN_PROGRESS", label: "Em Atendimento", color: "bg-yellow-400" },
  { status: "COMPLETED", label: "Concluido", color: "bg-gray-400" },
  { status: "CANCELLED", label: "Cancelado", color: "bg-red-400" },
  { status: "NO_SHOW", label: "Faltou", color: "bg-orange-400" },
];

// --- build time labels ---

function buildTimeLabels() {
  const labels: string[] = [];
  for (let m = GRID_START; m < GRID_END; m += SLOT_INTERVAL) {
    labels.push(minutesToTime(m));
  }
  return labels;
}

const TIME_LABELS = buildTimeLabels();

// --- component ---

export default function AgendaPage() {
  const today = toDateString(new Date());
  const [selectedDate, setSelectedDate] = useState(today);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [selectedApt, setSelectedApt] = useState<AppointmentResponse | null>(null);

  // Fetch providers
  const providersFetcher = useCallback(() => fetchProviders(), []);
  const {
    data: providers,
    loading: loadingProviders,
  } = useApi<ProviderResponse[]>(providersFetcher, []);

  // Auto-select first provider
  const activeProvider = selectedProvider || providers?.[0]?.id || "";

  // Fetch day schedule
  const scheduleFetcher = useCallback(() => {
    if (!activeProvider) return Promise.resolve(null);
    return fetchDaySchedule(activeProvider, selectedDate);
  }, [activeProvider, selectedDate]);

  const {
    data: schedule,
    loading: loadingSchedule,
    error,
    refetch,
  } = useApi(scheduleFetcher, [activeProvider, selectedDate]);

  // Navigate dates
  function changeDate(delta: number) {
    const d = new Date(selectedDate + "T00:00:00");
    d.setDate(d.getDate() + delta);
    setSelectedDate(toDateString(d));
  }

  function goToToday() {
    setSelectedDate(today);
  }

  // Appointments positioned on grid
  const positionedAppointments = useMemo(() => {
    if (!schedule?.appointments) return [];
    return schedule.appointments
      .filter((a) => a.status !== "CANCELLED")
      .map((a) => {
        const startMin = isoToMinutes(a.start_at);
        const endMin = isoToMinutes(a.end_at);
        const top = ((startMin - GRID_START) / SLOT_INTERVAL) * SLOT_HEIGHT;
        const height = ((endMin - startMin) / SLOT_INTERVAL) * SLOT_HEIGHT;
        return { ...a, top, height: Math.max(height, SLOT_HEIGHT / 2) };
      })
      .filter((a) => a.top >= 0);
  }, [schedule]);

  // Available slots
  const availableSlots = useMemo(() => {
    if (!schedule?.available_slots) return [];
    return schedule.available_slots.map((s) => {
      const startMin = isoToMinutes(s.start);
      const endMin = isoToMinutes(s.end);
      const top = ((startMin - GRID_START) / SLOT_INTERVAL) * SLOT_HEIGHT;
      const height = ((endMin - startMin) / SLOT_INTERVAL) * SLOT_HEIGHT;
      return { ...s, top, height: Math.max(height, 4) };
    });
  }, [schedule]);

  // Book handler
  async function handleBook(data: BookAppointmentRequest) {
    await bookAppointment(data);
    setShowForm(false);
    refetch();
  }

  const totalSlots = TIME_LABELS.length;
  const gridHeight = totalSlots * SLOT_HEIGHT;

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Agenda</h1>
          <p className="text-sm text-gray-500 capitalize">
            {formatDateBR(selectedDate)}
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Novo Agendamento
        </button>
      </div>

      {/* Date navigation + Provider filter */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div className="flex items-center gap-2">
          <button
            onClick={() => changeDate(-1)}
            className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Dia anterior"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />

          <button
            onClick={() => changeDate(1)}
            className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Proximo dia"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            onClick={goToToday}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors"
          >
            Hoje
          </button>
        </div>

        <select
          value={activeProvider}
          onChange={(e) => setSelectedProvider(e.target.value)}
          disabled={loadingProviders || !providers?.length}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
        >
          {!providers?.length && (
            <option value="">Carregando profissionais...</option>
          )}
          {providers?.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
              {p.specialty ? ` — ${p.specialty}` : ""}
            </option>
          ))}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
          <button onClick={refetch} className="ml-2 underline">
            Tentar novamente
          </button>
        </div>
      )}

      {/* Main content: calendar + form side by side */}
      <div className="flex gap-6">
        {/* Time grid */}
        <div className="flex-1 bg-white rounded-xl border shadow-sm overflow-hidden">
          <div className="overflow-y-auto max-h-[calc(100vh-280px)]">
            <div className="relative" style={{ height: gridHeight }}>
              {/* Time labels + grid lines */}
              {TIME_LABELS.map((label, i) => {
                const top = i * SLOT_HEIGHT;
                return (
                  <div key={label} className="absolute left-0 right-0" style={{ top }}>
                    <div className="flex items-start">
                      <span className="w-16 text-xs text-gray-400 text-right pr-3 -mt-2 select-none">
                        {label}
                      </span>
                      <div className="flex-1 border-t border-gray-100" />
                    </div>
                  </div>
                );
              })}

              {/* Available slots (lighter green) */}
              {availableSlots.map((slot, i) => (
                <div
                  key={`slot-${i}`}
                  className="absolute left-16 right-2 bg-green-50 border border-green-200 border-dashed rounded opacity-60"
                  style={{
                    top: slot.top,
                    height: slot.height,
                  }}
                />
              ))}

              {/* Appointment blocks */}
              {positionedAppointments.map((apt) => {
                const bg = STATUS_BG[apt.status] || STATUS_BG.SCHEDULED;
                return (
                  <div
                    key={apt.id}
                    className={`absolute left-16 right-2 rounded-lg border overflow-hidden ${bg}`}
                    style={{
                      top: apt.top,
                      height: apt.height,
                      zIndex: 10,
                    }}
                  >
                    <div className="p-1.5 h-full">
                      <AppointmentCard
                        appointment={apt}
                        onClick={(a) => setSelectedApt(a)}
                      />
                    </div>
                  </div>
                );
              })}

              {/* Loading overlay */}
              {loadingSchedule && (
                <div className="absolute inset-0 bg-white/60 flex items-center justify-center z-20">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <svg
                      className="animate-spin w-4 h-4 text-teal-600"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                      />
                    </svg>
                    Carregando agenda...
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Booking form (right side) */}
        {showForm && providers && (
          <div className="w-80 flex-shrink-0">
            <BookingForm
              providers={providers}
              selectedDate={selectedDate}
              selectedProvider={activeProvider}
              onSubmit={handleBook}
              onCancel={() => setShowForm(false)}
            />
          </div>
        )}
      </div>

      {/* Selected appointment detail */}
      {selectedApt && (
        <div className="bg-white rounded-xl border shadow-sm p-5">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedApt.patient_name || "Paciente"}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {new Date(selectedApt.start_at).toLocaleTimeString("pt-BR", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}{" "}
                -{" "}
                {new Date(selectedApt.end_at).toLocaleTimeString("pt-BR", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}{" "}
                ({selectedApt.duration_minutes} min)
              </p>
              <p className="text-sm text-gray-500">
                Profissional: {selectedApt.provider_name || "—"}
              </p>
              <p className="text-sm text-gray-500 capitalize">
                Tipo: {selectedApt.appointment_type}
              </p>
              {selectedApt.notes && (
                <p className="text-sm text-gray-500 mt-2">
                  Obs: {selectedApt.notes}
                </p>
              )}
            </div>
            <button
              onClick={() => setSelectedApt(null)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-gray-500">
        {LEGEND.map((item) => (
          <div key={item.status} className="flex items-center gap-1.5">
            <span className={`w-3 h-3 rounded ${item.color}`} />
            {item.label}
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-green-200 border border-green-400 border-dashed" />
          Disponivel
        </div>
      </div>
    </div>
  );
}
