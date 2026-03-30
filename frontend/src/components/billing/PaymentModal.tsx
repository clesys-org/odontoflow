"use client";

import { useState } from "react";
import type { Installment } from "@/lib/types/billing";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

const PAYMENT_METHODS = [
  { value: "PIX", label: "PIX" },
  { value: "CARTAO_CREDITO", label: "Cartao Credito" },
  { value: "CARTAO_DEBITO", label: "Cartao Debito" },
  { value: "DINHEIRO", label: "Dinheiro" },
  { value: "BOLETO", label: "Boleto" },
];

interface PaymentModalProps {
  installment: Installment;
  loading: boolean;
  onConfirm: (method: string) => void;
  onClose: () => void;
}

export default function PaymentModal({
  installment,
  loading,
  onConfirm,
  onClose,
}: PaymentModalProps) {
  const [method, setMethod] = useState("PIX");

  const inputClass =
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-xl border p-6 w-full max-w-md mx-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold">
            Registrar Pagamento
          </h3>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Info */}
        <div className="bg-gray-50 rounded-lg p-3 space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Parcela</span>
            <span className="font-medium">{installment.number}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Valor</span>
            <span className="font-bold text-teal-700">
              {formatBRL(installment.amount_centavos)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Vencimento</span>
            <span className="font-medium">
              {new Date(installment.due_date).toLocaleDateString("pt-BR")}
            </span>
          </div>
        </div>

        {/* Method Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Forma de pagamento
          </label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className={inputClass}
          >
            {PAYMENT_METHODS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => onConfirm(method)}
            disabled={loading}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Processando..." : "Confirmar Pagamento"}
          </button>
        </div>
      </div>
    </div>
  );
}
