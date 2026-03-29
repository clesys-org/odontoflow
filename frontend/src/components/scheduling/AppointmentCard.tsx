"use client";

import type { AppointmentResponse } from "@/lib/types/scheduling";

const STATUS_COLORS: Record<string, string> = {
  SCHEDULED: "bg-blue-100 text-blue-800 border-blue-200",
  CONFIRMED: "bg-green-100 text-green-800 border-green-200",
  IN_PROGRESS: "bg-yellow-100 text-yellow-800 border-yellow-200",
  COMPLETED: "bg-gray-100 text-gray-600 border-gray-200",
  CANCELLED: "bg-red-100 text-red-700 border-red-200",
  NO_SHOW: "bg-orange-100 text-orange-800 border-orange-200",
  WAITING: "bg-purple-100 text-purple-800 border-purple-200",
};

const STATUS_LABEL: Record<string, string> = {
  SCHEDULED: "Agendado",
  CONFIRMED: "Confirmado",
  IN_PROGRESS: "Em Atendimento",
  COMPLETED: "Concluido",
  CANCELLED: "Cancelado",
  NO_SHOW: "Faltou",
  WAITING: "Aguardando",
};

function formatTime(isoString: string): string {
  const d = new Date(isoString);
  return d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

interface AppointmentCardProps {
  appointment: AppointmentResponse;
  onClick?: (appointment: AppointmentResponse) => void;
}

export default function AppointmentCard({
  appointment,
  onClick,
}: AppointmentCardProps) {
  const statusClass =
    STATUS_COLORS[appointment.status] || STATUS_COLORS.SCHEDULED;
  const statusLabel =
    STATUS_LABEL[appointment.status] || appointment.status;

  return (
    <button
      type="button"
      onClick={() => onClick?.(appointment)}
      className="w-full text-left rounded-lg border p-2 shadow-sm hover:shadow-md transition-shadow"
      style={{
        borderLeftWidth: "4px",
        borderLeftColor: appointment.type_color || "#3b82f6",
      }}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-gray-900 truncate">
            {appointment.patient_name || "Paciente"}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            {formatTime(appointment.start_at)} - {formatTime(appointment.end_at)}
          </p>
          <p className="text-xs text-gray-400 mt-0.5 capitalize">
            {appointment.appointment_type}
          </p>
        </div>
        <span
          className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-medium whitespace-nowrap border ${statusClass}`}
        >
          {statusLabel}
        </span>
      </div>
    </button>
  );
}
