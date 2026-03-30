"use client";

import { useCallback } from "react";
import { useApi } from "@/hooks/useApi";
import { fetchDashboardKPIs } from "@/lib/api/analytics";
import type { KPI } from "@/lib/types/analytics";

const KPI_CONFIG: Record<
  string,
  { bg: string; iconColor: string; path: string }
> = {
  PATIENTS_ACTIVE: {
    bg: "bg-teal-100",
    iconColor: "text-teal-600",
    path: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
  },
  APPOINTMENTS_TODAY: {
    bg: "bg-blue-100",
    iconColor: "text-blue-600",
    path: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
  },
  REVENUE_MONTH: {
    bg: "bg-green-100",
    iconColor: "text-green-600",
    path: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
  },
  ATTENDANCE_RATE: {
    bg: "bg-purple-100",
    iconColor: "text-purple-600",
    path: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  },
};

const DASHBOARD_KPIS = [
  "PATIENTS_ACTIVE",
  "APPOINTMENTS_TODAY",
  "REVENUE_MONTH",
  "ATTENDANCE_RATE",
];

export default function DashboardPage() {
  const fetcher = useCallback(() => fetchDashboardKPIs(), []);
  const { data, loading, error, refetch } = useApi(fetcher, []);

  const kpiMap = new Map<string, KPI>();
  if (data) {
    for (const kpi of data.kpis) {
      kpiMap.set(kpi.kpi_type, kpi);
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-gray-500">Visao geral da clinica</p>
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

      {/* KPI Cards */}
      {loading && !data && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border p-5">
              <div className="h-3 bg-gray-200 rounded animate-pulse w-24 mb-3" />
              <div className="h-7 bg-gray-200 rounded animate-pulse w-20" />
            </div>
          ))}
        </div>
      )}

      {data && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {DASHBOARD_KPIS.map((kpiType) => {
            const kpi = kpiMap.get(kpiType);
            const config = KPI_CONFIG[kpiType];
            return (
              <div key={kpiType} className="bg-white rounded-xl shadow-sm border p-5">
                <div className="flex items-center gap-2 mb-1">
                  <div
                    className={`w-8 h-8 ${config.bg} rounded-lg flex items-center justify-center`}
                  >
                    <svg
                      className={`w-4 h-4 ${config.iconColor}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d={config.path}
                      />
                    </svg>
                  </div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide">
                    {kpi?.label || kpiType}
                  </p>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {kpi?.formatted_value || "—"}
                </p>
              </div>
            );
          })}
        </div>
      )}

      {/* Agenda do dia */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Agenda de Hoje</h2>
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg mb-2">Nenhuma consulta agendada</p>
          <p className="text-sm">Configure seus horarios e comece a agendar pacientes</p>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Novo Paciente", href: "/pacientes/novo", color: "bg-teal-600" },
          { label: "Agendar Consulta", href: "/agenda", color: "bg-blue-600" },
          { label: "Financeiro", href: "/financeiro", color: "bg-green-600" },
          { label: "Relatorios", href: "/relatorios", color: "bg-purple-600" },
        ].map((action) => (
          <a
            key={action.label}
            href={action.href}
            className={`${action.color} text-white rounded-xl p-4 text-center font-medium hover:opacity-90 transition-opacity`}
          >
            {action.label}
          </a>
        ))}
      </div>
    </div>
  );
}
