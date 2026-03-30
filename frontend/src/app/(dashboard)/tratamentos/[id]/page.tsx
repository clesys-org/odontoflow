"use client";

import { useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import {
  fetchPlan,
  approvePlan,
  executeItem,
  cancelPlan,
} from "@/lib/api/treatment";
import { createInvoice } from "@/lib/api/billing";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

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

const ITEM_STATUS_BADGE: Record<string, string> = {
  PENDING: "bg-gray-100 text-gray-700",
  EXECUTED: "bg-green-100 text-green-700",
  CANCELLED: "bg-red-100 text-red-700",
};

const ITEM_STATUS_LABEL: Record<string, string> = {
  PENDING: "Pendente",
  EXECUTED: "Executado",
  CANCELLED: "Cancelado",
};

export default function TratamentoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetcher = useCallback(() => fetchPlan(id), [id]);
  const {
    data: plan,
    loading,
    error: fetchError,
    refetch,
  } = useApi(fetcher, [id]);

  async function handleApprove() {
    if (!plan) return;
    setActionLoading(true);
    setError(null);
    try {
      await approvePlan(plan.id, plan.provider_id);
      refetch();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao aprovar plano"
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function handleExecuteItem(itemId: string) {
    if (!plan) return;
    setActionLoading(true);
    setError(null);
    try {
      await executeItem(plan.id, itemId);
      refetch();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao executar item"
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function handleCancel() {
    if (!plan || !confirm("Tem certeza que deseja cancelar este plano?"))
      return;
    setActionLoading(true);
    setError(null);
    try {
      await cancelPlan(plan.id);
      refetch();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao cancelar plano"
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function handleGenerateInvoice() {
    if (!plan) return;
    setActionLoading(true);
    setError(null);
    try {
      const invoice = await createInvoice({
        patient_id: plan.patient_id,
        treatment_plan_id: plan.id,
        description: plan.title,
        total_centavos:
          plan.total_value_centavos - plan.discount_centavos,
      });
      router.push(`/financeiro/receber?invoice=${invoice.id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao gerar fatura"
      );
    } finally {
      setActionLoading(false);
    }
  }

  // Loading state
  if (loading && !plan) {
    return (
      <div className="p-6 lg:p-8 space-y-6">
        <div className="h-8 bg-gray-200 rounded animate-pulse w-48" />
        <div className="bg-white rounded-xl shadow-sm border p-6 space-y-4">
          <div className="h-6 bg-gray-200 rounded animate-pulse w-64" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-40" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-52" />
        </div>
      </div>
    );
  }

  // Error state
  if (fetchError) {
    return (
      <div className="p-6 lg:p-8 space-y-6">
        <Link
          href="/tratamentos"
          className="text-teal-600 hover:text-teal-800 text-sm font-medium"
        >
          ← Voltar para tratamentos
        </Link>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {fetchError}
          <button onClick={refetch} className="ml-2 underline">
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  if (!plan) return null;

  const completedItems = plan.items.filter(
    (i) => i.status === "EXECUTED"
  ).length;
  const totalItems = plan.items.length;
  const progressPercent =
    totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;

  const canApprove =
    plan.status === "DRAFT" || plan.status === "PROPOSED";
  const canExecuteItems =
    plan.status === "APPROVED" || plan.status === "IN_PROGRESS";
  const canGenerateInvoice =
    plan.status === "APPROVED" ||
    plan.status === "IN_PROGRESS" ||
    plan.status === "COMPLETED";
  const canCancel = plan.status !== "CANCELLED" && plan.status !== "COMPLETED";

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex items-start gap-3">
          <Link
            href="/tratamentos"
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
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{plan.title}</h1>
              <span
                className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  STATUS_BADGE[plan.status] || "bg-gray-100 text-gray-800"
                }`}
              >
                {STATUS_LABEL[plan.status] || plan.status}
              </span>
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-sm text-gray-500">
              <span>Paciente: {plan.patient_name}</span>
              <span>Dentista: {plan.provider_name}</span>
              <span>
                Criado em:{" "}
                {new Date(plan.created_at).toLocaleDateString("pt-BR")}
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 sm:shrink-0">
          {canApprove && (
            <button
              onClick={handleApprove}
              disabled={actionLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              Aprovar Plano
            </button>
          )}
          {canGenerateInvoice && (
            <button
              onClick={handleGenerateInvoice}
              disabled={actionLoading}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
            >
              Gerar Fatura
            </button>
          )}
          {canCancel && (
            <button
              onClick={handleCancel}
              disabled={actionLoading}
              className="px-4 py-2 border border-red-300 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">
            Total
          </p>
          <p className="text-xl font-bold text-gray-900 mt-1">
            {formatBRL(plan.total_value_centavos)}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">
            Desconto
          </p>
          <p className="text-xl font-bold text-gray-900 mt-1">
            {formatBRL(plan.discount_centavos)}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">
            Valor Final
          </p>
          <p className="text-xl font-bold text-teal-700 mt-1">
            {formatBRL(
              plan.total_value_centavos - plan.discount_centavos
            )}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">
            Progresso
          </p>
          <p className="text-xl font-bold text-gray-900 mt-1">
            {completedItems}/{totalItems}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      {totalItems > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Progresso do tratamento
            </span>
            <span className="text-sm text-gray-500">{progressPercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-teal-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Items Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-4 py-3 border-b bg-gray-50">
          <h2 className="text-base font-semibold">
            Itens do Plano ({plan.items.length})
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Procedimento
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">
                  Dente
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">
                  Face
                </th>
                <th className="text-center px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">
                  Qtd
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">
                  Preco Unit.
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Status
                </th>
                {canExecuteItems && (
                  <th className="text-right px-4 py-3 font-medium text-gray-600">
                    Acao
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {plan.items.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-8 text-center text-gray-400"
                  >
                    Nenhum item neste plano
                  </td>
                </tr>
              )}
              {plan.items.map((item) => (
                <tr
                  key={item.id}
                  className="border-b hover:bg-gray-50 transition-colors"
                >
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-gray-900">
                        {item.description}
                      </p>
                      <p className="text-xs text-gray-500">
                        TUSS: {item.tuss_code}
                        {item.phase_name &&
                          ` | Fase ${item.phase_number}: ${item.phase_name}`}
                      </p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 hidden md:table-cell">
                    {item.tooth_number || "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-600 hidden md:table-cell">
                    {item.surface || "—"}
                  </td>
                  <td className="px-4 py-3 text-center text-gray-600 hidden lg:table-cell">
                    {item.quantity}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600 hidden lg:table-cell">
                    {formatBRL(item.unit_price_centavos)}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        ITEM_STATUS_BADGE[item.status] ||
                        "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {ITEM_STATUS_LABEL[item.status] || item.status}
                    </span>
                    {item.executed_at && (
                      <p className="text-xs text-gray-400 mt-0.5">
                        {new Date(item.executed_at).toLocaleDateString(
                          "pt-BR"
                        )}
                      </p>
                    )}
                  </td>
                  {canExecuteItems && (
                    <td className="px-4 py-3 text-right">
                      {item.status === "PENDING" && (
                        <button
                          onClick={() => handleExecuteItem(item.id)}
                          disabled={actionLoading}
                          className="px-3 py-1 bg-teal-600 text-white rounded-lg text-xs font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
                        >
                          Executar
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Approval Info */}
      {plan.approved_at && (
        <div className="text-xs text-gray-400 flex gap-4">
          <span>
            Aprovado em:{" "}
            {new Date(plan.approved_at).toLocaleDateString("pt-BR")}
          </span>
          {plan.approved_by && (
            <span>Aprovado por: {plan.approved_by}</span>
          )}
        </div>
      )}
    </div>
  );
}
