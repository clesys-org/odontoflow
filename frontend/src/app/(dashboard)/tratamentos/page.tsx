"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { fetchPlans } from "@/lib/api/treatment";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

const STATUS_OPTIONS = [
  { value: "", label: "Todos" },
  { value: "DRAFT", label: "Rascunho" },
  { value: "PROPOSED", label: "Proposto" },
  { value: "APPROVED", label: "Aprovado" },
  { value: "IN_PROGRESS", label: "Em andamento" },
  { value: "COMPLETED", label: "Concluido" },
  { value: "CANCELLED", label: "Cancelado" },
];

const STATUS_BADGE: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-800",
  PROPOSED: "bg-blue-100 text-blue-800",
  APPROVED: "bg-green-100 text-green-800",
  IN_PROGRESS: "bg-yellow-100 text-yellow-800",
  COMPLETED: "bg-teal-100 text-teal-800",
  CANCELLED: "bg-red-100 text-red-800",
};

const STATUS_LABEL: Record<string, string> = {
  DRAFT: "Rascunho",
  PROPOSED: "Proposto",
  APPROVED: "Aprovado",
  IN_PROGRESS: "Em andamento",
  COMPLETED: "Concluido",
  CANCELLED: "Cancelado",
};

export default function TratamentosPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 15;

  const fetcher = useCallback(
    () =>
      fetchPlans({
        q: query || undefined,
        status: status || undefined,
        page,
        page_size: pageSize,
      }),
    [query, status, page]
  );

  const { data, loading, error, refetch } = useApi(fetcher, [
    query,
    status,
    page,
  ]);

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Tratamentos</h1>
          <p className="text-sm text-gray-500">
            {data
              ? `${data.total} plano${data.total !== 1 ? "s" : ""} encontrado${data.total !== 1 ? "s" : ""}`
              : "Carregando..."}
          </p>
        </div>
        <Link
          href="/tratamentos/novo"
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
          Novo Plano
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Buscar por paciente ou titulo..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(1);
            }}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
        </div>
        <select
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
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

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Paciente
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Titulo
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">
                  Status
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">
                  Total
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">
                  Data
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">
                  Acoes
                </th>
              </tr>
            </thead>
            <tbody>
              {loading && !data && (
                <>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-3">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-32" />
                      </td>
                      <td className="px-4 py-3">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-40" />
                      </td>
                      <td className="px-4 py-3 hidden md:table-cell">
                        <div className="h-5 bg-gray-200 rounded-full animate-pulse w-20" />
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-24 ml-auto" />
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-20" />
                      </td>
                      <td className="px-4 py-3">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-12 ml-auto" />
                      </td>
                    </tr>
                  ))}
                </>
              )}

              {data && data.plans.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-12 text-center text-gray-400"
                  >
                    <p className="text-lg mb-1">
                      Nenhum plano de tratamento encontrado
                    </p>
                    <p className="text-sm">
                      {query
                        ? "Tente alterar os filtros de busca"
                        : "Crie o primeiro plano de tratamento"}
                    </p>
                  </td>
                </tr>
              )}

              {data?.plans.map((plan) => (
                <tr
                  key={plan.id}
                  className="border-b hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3">
                    <span className="font-medium text-gray-900">
                      {plan.patient_name}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/tratamentos/${plan.id}`}
                      className="text-gray-700 hover:text-teal-700"
                    >
                      {plan.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        STATUS_BADGE[plan.status] || "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {STATUS_LABEL[plan.status] || plan.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600 hidden lg:table-cell">
                    {formatBRL(plan.total_value_centavos)}
                  </td>
                  <td className="px-4 py-3 text-gray-600 hidden lg:table-cell">
                    {new Date(plan.created_at).toLocaleDateString("pt-BR")}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/tratamentos/${plan.id}`}
                      className="text-teal-600 hover:text-teal-800 text-sm font-medium"
                    >
                      Ver
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
            <p className="text-sm text-gray-600">
              Pagina {data.page} de {data.total_pages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm disabled:opacity-40 hover:bg-white transition-colors"
              >
                Anterior
              </button>
              <button
                onClick={() =>
                  setPage((p) => Math.min(data.total_pages, p + 1))
                }
                disabled={page >= data.total_pages}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm disabled:opacity-40 hover:bg-white transition-colors"
              >
                Proxima
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
