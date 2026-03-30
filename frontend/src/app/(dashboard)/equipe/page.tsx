"use client";

import { useCallback, useState } from "react";
import { useApi } from "@/hooks/useApi";
import { fetchStaff, fetchProductionReport } from "@/lib/api/staff";
import type { StaffMember, ProductionReport } from "@/lib/types/staff";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

export default function EquipePage() {
  const staffFetcher = useCallback(() => fetchStaff(), []);
  const { data: staffData, loading, error, refetch } = useApi(staffFetcher, []);

  // Production report state
  const [selectedMember, setSelectedMember] = useState<StaffMember | null>(null);
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(1);
    return d.toISOString().split("T")[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [productionReport, setProductionReport] = useState<ProductionReport | null>(null);
  const [reportLoading, setReportLoading] = useState(false);

  async function loadReport(member: StaffMember) {
    setSelectedMember(member);
    setReportLoading(true);
    try {
      const report = await fetchProductionReport(member.id, {
        start_date: startDate,
        end_date: endDate,
      });
      setProductionReport(report);
    } catch {
      setProductionReport(null);
    } finally {
      setReportLoading(false);
    }
  }

  async function refreshReport() {
    if (selectedMember) {
      await loadReport(selectedMember);
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Equipe</h1>
          <p className="text-sm text-gray-500">Profissionais, comissoes e producao</p>
        </div>
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

      {/* Loading */}
      {loading && !staffData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border p-5">
              <div className="h-5 bg-gray-200 rounded animate-pulse w-36 mb-3" />
              <div className="h-3 bg-gray-200 rounded animate-pulse w-24 mb-2" />
              <div className="h-3 bg-gray-200 rounded animate-pulse w-20" />
            </div>
          ))}
        </div>
      )}

      {staffData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Staff List */}
          <div className="lg:col-span-1 space-y-3">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
              Profissionais ({staffData.total})
            </h2>
            {staffData.staff.length === 0 && (
              <div className="text-center py-8 text-gray-400 bg-white rounded-xl shadow-sm border">
                Nenhum profissional cadastrado
              </div>
            )}
            {staffData.staff.map((member) => (
              <button
                key={member.id}
                onClick={() => loadReport(member)}
                className={`w-full text-left bg-white rounded-xl shadow-sm border p-4 hover:border-teal-300 transition-colors ${
                  selectedMember?.id === member.id ? "border-teal-500 ring-1 ring-teal-500" : ""
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-semibold text-gray-900">{member.full_name}</h3>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      member.active
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {member.active ? "Ativo" : "Inativo"}
                  </span>
                </div>
                {member.cro_number && (
                  <p className="text-sm text-gray-500">CRO: {member.cro_number}</p>
                )}
                {member.specialty && (
                  <p className="text-sm text-gray-500">{member.specialty}</p>
                )}
                {member.commission_rules.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {member.commission_rules.map((rule, i) => (
                      <span
                        key={i}
                        className="text-xs bg-teal-50 text-teal-700 px-2 py-0.5 rounded"
                      >
                        {rule.procedure_category || "Geral"}:{" "}
                        {rule.commission_type === "PERCENTAGE"
                          ? `${rule.value}%`
                          : formatBRL(rule.value)}
                      </span>
                    ))}
                  </div>
                )}
              </button>
            ))}
          </div>

          {/* Production Report */}
          <div className="lg:col-span-2">
            {!selectedMember && (
              <div className="bg-white rounded-xl shadow-sm border p-12 text-center text-gray-400">
                <svg
                  className="w-12 h-12 mx-auto mb-3 text-gray-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p>Selecione um profissional para ver o relatorio de producao</p>
              </div>
            )}

            {selectedMember && (
              <div className="space-y-4">
                <div className="bg-white rounded-xl shadow-sm border p-4">
                  <h2 className="font-semibold text-gray-900 mb-3">
                    Producao — {selectedMember.full_name}
                  </h2>
                  <div className="flex flex-wrap gap-3 items-end">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Inicio</label>
                      <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="border rounded-lg px-3 py-1.5 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Fim</label>
                      <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="border rounded-lg px-3 py-1.5 text-sm"
                      />
                    </div>
                    <button
                      onClick={refreshReport}
                      className="px-4 py-1.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
                    >
                      Filtrar
                    </button>
                  </div>
                </div>

                {reportLoading && (
                  <div className="bg-white rounded-xl shadow-sm border p-8 text-center">
                    <div className="h-5 bg-gray-200 rounded animate-pulse w-48 mx-auto mb-3" />
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-32 mx-auto" />
                  </div>
                )}

                {!reportLoading && productionReport && (
                  <>
                    {/* Summary Cards */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-white rounded-xl shadow-sm border p-4">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Receita</p>
                        <p className="text-xl font-bold text-gray-900 mt-1">
                          {formatBRL(productionReport.total_revenue_centavos)}
                        </p>
                      </div>
                      <div className="bg-white rounded-xl shadow-sm border p-4">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Comissao</p>
                        <p className="text-xl font-bold text-teal-600 mt-1">
                          {formatBRL(productionReport.total_commission_centavos)}
                        </p>
                      </div>
                      <div className="bg-white rounded-xl shadow-sm border p-4">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">
                          Procedimentos
                        </p>
                        <p className="text-xl font-bold text-gray-900 mt-1">
                          {productionReport.entries_count}
                        </p>
                      </div>
                    </div>

                    {/* Entries table */}
                    <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b bg-gray-50">
                              <th className="text-left px-4 py-3 font-medium text-gray-600">
                                Data
                              </th>
                              <th className="text-left px-4 py-3 font-medium text-gray-600">
                                Paciente
                              </th>
                              <th className="text-left px-4 py-3 font-medium text-gray-600">
                                Procedimento
                              </th>
                              <th className="text-right px-4 py-3 font-medium text-gray-600">
                                Receita
                              </th>
                              <th className="text-right px-4 py-3 font-medium text-gray-600">
                                Comissao
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {productionReport.entries.length === 0 && (
                              <tr>
                                <td
                                  colSpan={5}
                                  className="px-4 py-8 text-center text-gray-400"
                                >
                                  Nenhum registro de producao no periodo
                                </td>
                              </tr>
                            )}
                            {productionReport.entries.map((entry) => (
                              <tr
                                key={entry.id}
                                className="border-b hover:bg-gray-50 transition-colors"
                              >
                                <td className="px-4 py-3 text-gray-600">
                                  {new Date(entry.date).toLocaleDateString("pt-BR")}
                                </td>
                                <td className="px-4 py-3 font-medium text-gray-900">
                                  {entry.patient_name}
                                </td>
                                <td className="px-4 py-3 text-gray-600">
                                  {entry.procedure_description}
                                </td>
                                <td className="px-4 py-3 text-right text-gray-900">
                                  {formatBRL(entry.revenue_centavos)}
                                </td>
                                <td className="px-4 py-3 text-right text-teal-600 font-medium">
                                  {formatBRL(entry.commission_centavos)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
