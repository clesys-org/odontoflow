"use client";

import { useCallback, useState } from "react";
import { useApi } from "@/hooks/useApi";
import { fetchDashboardKPIs, fetchPeriodReport } from "@/lib/api/analytics";
import type { KPI, ClinicReport } from "@/lib/types/analytics";

const KPI_ICONS: Record<string, { bg: string; icon: string }> = {
  PATIENTS_ACTIVE: { bg: "bg-teal-100", icon: "text-teal-600" },
  APPOINTMENTS_TODAY: { bg: "bg-blue-100", icon: "text-blue-600" },
  REVENUE_MONTH: { bg: "bg-green-100", icon: "text-green-600" },
  ATTENDANCE_RATE: { bg: "bg-purple-100", icon: "text-purple-600" },
  TREATMENT_ACCEPTANCE: { bg: "bg-indigo-100", icon: "text-indigo-600" },
  AVG_TICKET: { bg: "bg-yellow-100", icon: "text-yellow-600" },
  NEW_PATIENTS_MONTH: { bg: "bg-pink-100", icon: "text-pink-600" },
  CANCELLATION_RATE: { bg: "bg-red-100", icon: "text-red-600" },
};

function TrendBadge({ trend }: { trend: string | null }) {
  if (!trend) return null;
  const styles = {
    up: "text-green-600 bg-green-50",
    down: "text-red-600 bg-red-50",
    stable: "text-gray-600 bg-gray-50",
  };
  const arrows = { up: "^", down: "v", stable: "~" };
  const s = styles[trend as keyof typeof styles] || styles.stable;
  const a = arrows[trend as keyof typeof arrows] || "~";
  return (
    <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${s}`}>{a}</span>
  );
}

type PeriodType = "month" | "quarter" | "year";

function getPeriodDates(period: PeriodType): { start: string; end: string } {
  const now = new Date();
  const end = now.toISOString().split("T")[0];
  let start: string;

  if (period === "month") {
    const d = new Date(now.getFullYear(), now.getMonth(), 1);
    start = d.toISOString().split("T")[0];
  } else if (period === "quarter") {
    const d = new Date(now.getFullYear(), now.getMonth() - 2, 1);
    start = d.toISOString().split("T")[0];
  } else {
    const d = new Date(now.getFullYear(), 0, 1);
    start = d.toISOString().split("T")[0];
  }

  return { start, end };
}

export default function RelatoriosPage() {
  const [period, setPeriod] = useState<PeriodType>("month");

  // Dashboard KPIs
  const kpiFetcher = useCallback(() => fetchDashboardKPIs(), []);
  const { data: kpiData, loading: kpiLoading, error: kpiError, refetch: kpiRefetch } =
    useApi(kpiFetcher, []);

  // Period report
  const [report, setReport] = useState<ClinicReport | null>(null);
  const [reportLoading, setReportLoading] = useState(false);

  async function loadReport(p: PeriodType) {
    setPeriod(p);
    setReportLoading(true);
    try {
      const { start, end } = getPeriodDates(p);
      const r = await fetchPeriodReport(start, end);
      setReport(r);
    } catch {
      setReport(null);
    } finally {
      setReportLoading(false);
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Relatorios</h1>
          <p className="text-sm text-gray-500">KPIs e indicadores da clinica</p>
        </div>
        <div className="flex gap-2">
          {(["month", "quarter", "year"] as PeriodType[]).map((p) => (
            <button
              key={p}
              onClick={() => loadReport(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                period === p
                  ? "bg-teal-600 text-white"
                  : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
              }`}
            >
              {p === "month" ? "Mes" : p === "quarter" ? "Trimestre" : "Ano"}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {kpiError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {kpiError}
          <button onClick={kpiRefetch} className="ml-2 underline">
            Tentar novamente
          </button>
        </div>
      )}

      {/* KPI Cards */}
      {kpiLoading && !kpiData && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border p-5">
              <div className="h-3 bg-gray-200 rounded animate-pulse w-24 mb-3" />
              <div className="h-7 bg-gray-200 rounded animate-pulse w-20" />
            </div>
          ))}
        </div>
      )}

      {kpiData && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiData.kpis.map((kpi: KPI) => {
            const style = KPI_ICONS[kpi.kpi_type] || {
              bg: "bg-gray-100",
              icon: "text-gray-600",
            };
            return (
              <div key={kpi.kpi_type} className="bg-white rounded-xl shadow-sm border p-5">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-8 h-8 ${style.bg} rounded-lg flex items-center justify-center`}
                    >
                      <svg
                        className={`w-4 h-4 ${style.icon}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                      </svg>
                    </div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">{kpi.label}</p>
                  </div>
                  <TrendBadge trend={kpi.trend} />
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">{kpi.formatted_value}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Period Report Section */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">
          Relatorio do Periodo
          {report && (
            <span className="text-sm font-normal text-gray-500 ml-2">
              {new Date(report.period_start).toLocaleDateString("pt-BR")} —{" "}
              {new Date(report.period_end).toLocaleDateString("pt-BR")}
            </span>
          )}
        </h2>

        {reportLoading && (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded animate-pulse w-64" />
            ))}
          </div>
        )}

        {!reportLoading && !report && (
          <div className="text-center py-8 text-gray-400">
            <p>Selecione um periodo acima para gerar o relatorio</p>
          </div>
        )}

        {!reportLoading && report && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {report.kpis.map((kpi) => (
              <div key={kpi.kpi_type} className="border rounded-lg p-3">
                <p className="text-xs text-gray-500">{kpi.label}</p>
                <p className="text-lg font-semibold text-gray-900 mt-1">
                  {kpi.formatted_value}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Charts Placeholder */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Graficos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center text-gray-400">
            <svg
              className="w-10 h-10 mx-auto mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <p className="font-medium">Faturamento Mensal</p>
            <p className="text-sm mt-1">Grafico disponivel na proxima fase</p>
          </div>
          <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center text-gray-400">
            <svg
              className="w-10 h-10 mx-auto mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"
              />
            </svg>
            <p className="font-medium">Distribuicao por Procedimento</p>
            <p className="text-sm mt-1">Grafico disponivel na proxima fase</p>
          </div>
        </div>
      </div>
    </div>
  );
}
