"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { fetchInvoices, payInstallment } from "@/lib/api/billing";
import PaymentModal from "@/components/billing/PaymentModal";
import type { Installment } from "@/lib/types/billing";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

const STATUS_OPTIONS = [
  { value: "", label: "Todos" },
  { value: "PENDING", label: "Pendente" },
  { value: "PAID", label: "Pago" },
  { value: "OVERDUE", label: "Vencido" },
  { value: "CANCELLED", label: "Cancelado" },
];

const STATUS_BADGE: Record<string, string> = {
  PENDING: "bg-yellow-100 text-yellow-800",
  PAID: "bg-green-100 text-green-800",
  PARTIAL: "bg-blue-100 text-blue-800",
  OVERDUE: "bg-red-100 text-red-800",
  CANCELLED: "bg-gray-100 text-gray-800",
};

const STATUS_LABEL: Record<string, string> = {
  PENDING: "Pendente",
  PAID: "Pago",
  PARTIAL: "Parcial",
  OVERDUE: "Vencido",
  CANCELLED: "Cancelado",
};

export default function ContasReceberPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [expandedInvoice, setExpandedInvoice] = useState<string | null>(null);
  const [payingInstallment, setPayingInstallment] = useState<{
    invoiceId: string;
    installment: Installment;
  } | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const pageSize = 15;

  const fetcher = useCallback(
    () =>
      fetchInvoices({
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

  async function handlePay(method: string) {
    if (!payingInstallment) return;
    setActionLoading(true);
    setActionError(null);
    try {
      await payInstallment(
        payingInstallment.invoiceId,
        payingInstallment.installment.number,
        method
      );
      setPayingInstallment(null);
      refetch();
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Erro ao registrar pagamento"
      );
    } finally {
      setActionLoading(false);
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-start gap-3">
          <Link
            href="/financeiro"
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 mt-0.5"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Contas a Receber</h1>
            <p className="text-sm text-gray-500">
              {data
                ? `${data.total} fatura${data.total !== 1 ? "s" : ""}`
                : "Carregando..."}
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Buscar por paciente ou descricao..."
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
      {actionError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {actionError}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600 w-8" />
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Paciente
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">
                  Descricao
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">
                  Total
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">
                  Pago
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">
                  Restante
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {loading && !data && (
                <>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-3">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-4" />
                      </td>
                      <td className="px-4 py-3">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-32" />
                      </td>
                      <td className="px-4 py-3 hidden md:table-cell">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-40" />
                      </td>
                      <td className="px-4 py-3">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-24 ml-auto" />
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-24 ml-auto" />
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <div className="h-4 bg-gray-200 rounded animate-pulse w-24 ml-auto" />
                      </td>
                      <td className="px-4 py-3">
                        <div className="h-5 bg-gray-200 rounded-full animate-pulse w-16" />
                      </td>
                    </tr>
                  ))}
                </>
              )}

              {data && data.invoices.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-12 text-center text-gray-400"
                  >
                    <p className="text-lg mb-1">Nenhuma fatura encontrada</p>
                    <p className="text-sm">
                      {query
                        ? "Tente alterar os filtros de busca"
                        : "As faturas aparecerao aqui quando criadas"}
                    </p>
                  </td>
                </tr>
              )}

              {data?.invoices.map((invoice) => (
                <InvoiceRow
                  key={invoice.id}
                  invoice={invoice}
                  expanded={expandedInvoice === invoice.id}
                  onToggle={() =>
                    setExpandedInvoice(
                      expandedInvoice === invoice.id ? null : invoice.id
                    )
                  }
                  onPayInstallment={(inst) =>
                    setPayingInstallment({
                      invoiceId: invoice.id,
                      installment: inst,
                    })
                  }
                />
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

      {/* Payment Modal */}
      {payingInstallment && (
        <PaymentModal
          installment={payingInstallment.installment}
          loading={actionLoading}
          onConfirm={handlePay}
          onClose={() => setPayingInstallment(null)}
        />
      )}
    </div>
  );
}

/* ---- Invoice Row with expandable installments ---- */

import type { Invoice } from "@/lib/types/billing";

function InvoiceRow({
  invoice,
  expanded,
  onToggle,
  onPayInstallment,
}: {
  invoice: Invoice;
  expanded: boolean;
  onToggle: () => void;
  onPayInstallment: (inst: Installment) => void;
}) {
  return (
    <>
      <tr
        className="border-b hover:bg-gray-50 transition-colors cursor-pointer"
        onClick={onToggle}
      >
        <td className="px-4 py-3">
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform ${expanded ? "rotate-90" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </td>
        <td className="px-4 py-3 font-medium text-gray-900">
          {invoice.patient_name}
        </td>
        <td className="px-4 py-3 text-gray-600 hidden md:table-cell">
          {invoice.description}
        </td>
        <td className="px-4 py-3 text-right text-gray-900 font-medium">
          {formatBRL(invoice.total_centavos)}
        </td>
        <td className="px-4 py-3 text-right text-green-700 hidden lg:table-cell">
          {formatBRL(invoice.amount_paid_centavos)}
        </td>
        <td className="px-4 py-3 text-right text-gray-600 hidden lg:table-cell">
          {formatBRL(invoice.amount_remaining_centavos)}
        </td>
        <td className="px-4 py-3">
          <span
            className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
              STATUS_BADGE[invoice.status] || "bg-gray-100 text-gray-800"
            }`}
          >
            {STATUS_LABEL[invoice.status] || invoice.status}
          </span>
        </td>
      </tr>

      {/* Installments */}
      {expanded && invoice.installments.length > 0 && (
        <tr>
          <td colSpan={7} className="px-0 py-0">
            <div className="bg-gray-50 border-b px-8 py-3">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                Parcelas
              </p>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-gray-500">
                    <th className="text-left py-1 font-medium">Parcela</th>
                    <th className="text-left py-1 font-medium">
                      Vencimento
                    </th>
                    <th className="text-right py-1 font-medium">Valor</th>
                    <th className="text-left py-1 font-medium">Metodo</th>
                    <th className="text-left py-1 font-medium">Status</th>
                    <th className="text-right py-1 font-medium">Acao</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.installments.map((inst) => (
                    <tr key={inst.id} className="border-t border-gray-200">
                      <td className="py-2 text-gray-700">
                        {inst.number}/{invoice.installments.length}
                      </td>
                      <td className="py-2 text-gray-700">
                        {new Date(inst.due_date).toLocaleDateString(
                          "pt-BR"
                        )}
                      </td>
                      <td className="py-2 text-right text-gray-700">
                        {formatBRL(inst.amount_centavos)}
                      </td>
                      <td className="py-2 text-gray-600">
                        {inst.payment_method || "—"}
                      </td>
                      <td className="py-2">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                            inst.status === "PAID"
                              ? "bg-green-100 text-green-700"
                              : inst.status === "OVERDUE"
                                ? "bg-red-100 text-red-700"
                                : "bg-yellow-100 text-yellow-700"
                          }`}
                        >
                          {inst.status === "PAID"
                            ? "Pago"
                            : inst.status === "OVERDUE"
                              ? "Vencido"
                              : "Pendente"}
                        </span>
                        {inst.paid_at && (
                          <span className="text-xs text-gray-400 ml-1">
                            {new Date(inst.paid_at).toLocaleDateString(
                              "pt-BR"
                            )}
                          </span>
                        )}
                      </td>
                      <td className="py-2 text-right">
                        {inst.status !== "PAID" &&
                          inst.status !== "CANCELLED" && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onPayInstallment(inst);
                              }}
                              className="px-3 py-1 bg-teal-600 text-white rounded-lg text-xs font-medium hover:bg-teal-700 transition-colors"
                            >
                              Registrar Pagamento
                            </button>
                          )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
