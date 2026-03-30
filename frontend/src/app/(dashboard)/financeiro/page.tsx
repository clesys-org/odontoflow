"use client";

import { useCallback } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { fetchFinanceDashboard } from "@/lib/api/billing";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

export default function FinanceiroPage() {
  const fetcher = useCallback(() => fetchFinanceDashboard(), []);
  const { data, loading, error, refetch } = useApi(fetcher, []);

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Financeiro</h1>
          <p className="text-sm text-gray-500">
            Visao geral das financas da clinica
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            href="/financeiro/receber"
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            Contas a Receber
          </Link>
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

      {/* KPI Cards */}
      {loading && !data && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-xl shadow-sm border p-5"
            >
              <div className="h-3 bg-gray-200 rounded animate-pulse w-24 mb-3" />
              <div className="h-7 bg-gray-200 rounded animate-pulse w-32" />
            </div>
          ))}
        </div>
      )}

      {data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl shadow-sm border p-5">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                    />
                  </svg>
                </div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  Receita Total
                </p>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {formatBRL(data.total_revenue_centavos)}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {data.paid_count} fatura{data.paid_count !== 1 ? "s" : ""}{" "}
                paga{data.paid_count !== 1 ? "s" : ""}
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-5">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                </div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  Contas a Receber
                </p>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {formatBRL(data.total_receivable_centavos)}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {data.pending_count} pendente{data.pending_count !== 1 ? "s" : ""}
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-5">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                    />
                  </svg>
                </div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  Vencidas
                </p>
              </div>
              <p className="text-2xl font-bold text-red-600">
                {formatBRL(data.total_overdue_centavos)}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {data.overdue_count} fatura{data.overdue_count !== 1 ? "s" : ""}
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-5">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-8 h-8 bg-teal-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-teal-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  Total Faturas
                </p>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {data.invoices_count}
              </p>
            </div>
          </div>

          {/* Recent Payments */}
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="px-4 py-3 border-b bg-gray-50 flex items-center justify-between">
              <h2 className="text-base font-semibold">
                Pagamentos Recentes
              </h2>
              <Link
                href="/financeiro/receber"
                className="text-teal-600 hover:text-teal-800 text-sm font-medium"
              >
                Ver todos
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left px-4 py-3 font-medium text-gray-600">
                      Paciente
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">
                      Valor
                    </th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">
                      Metodo
                    </th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">
                      Data
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_payments.length === 0 && (
                    <tr>
                      <td
                        colSpan={4}
                        className="px-4 py-8 text-center text-gray-400"
                      >
                        Nenhum pagamento registrado
                      </td>
                    </tr>
                  )}
                  {data.recent_payments.map((payment, idx) => (
                    <tr
                      key={idx}
                      className="border-b hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-4 py-3 font-medium text-gray-900">
                        {payment.patient_name}
                      </td>
                      <td className="px-4 py-3 text-right text-green-700 font-medium">
                        {formatBRL(payment.amount_centavos)}
                      </td>
                      <td className="px-4 py-3 text-gray-600 hidden md:table-cell">
                        {payment.method}
                      </td>
                      <td className="px-4 py-3 text-gray-600 hidden md:table-cell">
                        {new Date(payment.paid_at).toLocaleDateString(
                          "pt-BR"
                        )}
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
  );
}
