"use client";

import { useState, useCallback } from "react";
import { useApi } from "@/hooks/useApi";
import { fetchProcedures } from "@/lib/api/treatment";
import type { Procedure } from "@/lib/types/treatment";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

interface PlanItemInput {
  key: string;
  tuss_code: string;
  description: string;
  tooth_number: string;
  surface: string;
  quantity: number;
  unit_price_centavos: number;
  phase_number: number;
  phase_name: string;
}

function createEmptyItem(): PlanItemInput {
  return {
    key: crypto.randomUUID(),
    tuss_code: "",
    description: "",
    tooth_number: "",
    surface: "",
    quantity: 1,
    unit_price_centavos: 0,
    phase_number: 1,
    phase_name: "",
  };
}

interface TreatmentPlanBuilderProps {
  onSubmit: (data: {
    title: string;
    items: {
      tuss_code: string;
      description: string;
      tooth_number?: number | null;
      surface?: string | null;
      quantity: number;
      unit_price_centavos: number;
      phase_number?: number;
      phase_name?: string | null;
    }[];
    discount_centavos?: number;
  }) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
}

export default function TreatmentPlanBuilder({
  onSubmit,
  onCancel,
  loading,
}: TreatmentPlanBuilderProps) {
  const [title, setTitle] = useState("");
  const [items, setItems] = useState<PlanItemInput[]>([createEmptyItem()]);
  const [discountReais, setDiscountReais] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [procedureSearch, setProcedureSearch] = useState<{
    key: string;
    query: string;
  } | null>(null);

  const proceduresFetcher = useCallback(() => fetchProcedures(), []);
  const { data: procedures } = useApi(proceduresFetcher, []);

  function updateItem(key: string, field: string, value: string | number) {
    setItems((prev) =>
      prev.map((item) =>
        item.key === key ? { ...item, [field]: value } : item
      )
    );
  }

  function removeItem(key: string) {
    setItems((prev) => {
      if (prev.length <= 1) return prev;
      return prev.filter((item) => item.key !== key);
    });
  }

  function addItem() {
    setItems((prev) => [...prev, createEmptyItem()]);
  }

  function selectProcedure(key: string, proc: Procedure) {
    setItems((prev) =>
      prev.map((item) =>
        item.key === key
          ? {
              ...item,
              tuss_code: proc.tuss_code,
              description: proc.description,
              unit_price_centavos: proc.default_price_centavos,
            }
          : item
      )
    );
    setProcedureSearch(null);
  }

  const totalCentavos = items.reduce(
    (sum, item) => sum + item.quantity * item.unit_price_centavos,
    0
  );
  const discountCentavos = Math.round(
    (parseFloat(discountReais.replace(",", ".")) || 0) * 100
  );
  const finalCentavos = Math.max(0, totalCentavos - discountCentavos);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError("O titulo do plano e obrigatorio.");
      return;
    }

    const validItems = items.filter(
      (i) => i.tuss_code && i.description
    );
    if (validItems.length === 0) {
      setError("Adicione pelo menos um procedimento.");
      return;
    }

    try {
      await onSubmit({
        title: title.trim(),
        items: validItems.map((i) => ({
          tuss_code: i.tuss_code,
          description: i.description,
          tooth_number: i.tooth_number ? Number(i.tooth_number) : null,
          surface: i.surface || null,
          quantity: i.quantity,
          unit_price_centavos: i.unit_price_centavos,
          phase_number: i.phase_number,
          phase_name: i.phase_name || null,
        })),
        discount_centavos: discountCentavos > 0 ? discountCentavos : undefined,
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao salvar plano."
      );
    }
  }

  const inputClass =
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  const filteredProcedures =
    procedureSearch && procedures
      ? procedures.filter(
          (p) =>
            p.description
              .toLowerCase()
              .includes(procedureSearch.query.toLowerCase()) ||
            p.tuss_code.includes(procedureSearch.query)
        )
      : [];

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-xl shadow-sm border p-5 space-y-5"
    >
      <h3 className="text-base font-semibold">Novo Plano de Tratamento</h3>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Title */}
      <div>
        <label className={labelClass}>
          Titulo do Plano <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={inputClass}
          placeholder="Ex: Tratamento ortodontico completo"
        />
      </div>

      {/* Items */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className={labelClass}>Procedimentos</label>
          <button
            type="button"
            onClick={addItem}
            className="text-teal-600 hover:text-teal-800 text-sm font-medium"
          >
            + Adicionar item
          </button>
        </div>

        {items.map((item, idx) => (
          <div
            key={item.key}
            className="border border-gray-200 rounded-lg p-4 space-y-3 relative"
          >
            {items.length > 1 && (
              <button
                type="button"
                onClick={() => removeItem(item.key)}
                className="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 transition-colors"
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
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}

            <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
              {/* Procedure Search */}
              <div className="md:col-span-5 relative">
                <label className="text-xs text-gray-500">Procedimento</label>
                <input
                  type="text"
                  value={item.description}
                  onChange={(e) => {
                    updateItem(item.key, "description", e.target.value);
                    setProcedureSearch({
                      key: item.key,
                      query: e.target.value,
                    });
                  }}
                  onFocus={() =>
                    setProcedureSearch({
                      key: item.key,
                      query: item.description,
                    })
                  }
                  className={inputClass}
                  placeholder="Buscar procedimento..."
                />
                {/* Dropdown */}
                {procedureSearch?.key === item.key &&
                  filteredProcedures.length > 0 && (
                    <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                      {filteredProcedures.slice(0, 10).map((proc) => (
                        <button
                          key={proc.id}
                          type="button"
                          onClick={() =>
                            selectProcedure(item.key, proc)
                          }
                          className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm border-b last:border-b-0"
                        >
                          <span className="font-medium">
                            {proc.tuss_code}
                          </span>{" "}
                          — {proc.description}
                          <span className="text-gray-400 ml-1">
                            ({formatBRL(proc.default_price_centavos)})
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
              </div>

              {/* TUSS Code */}
              <div className="md:col-span-2">
                <label className="text-xs text-gray-500">TUSS</label>
                <input
                  type="text"
                  value={item.tuss_code}
                  onChange={(e) =>
                    updateItem(item.key, "tuss_code", e.target.value)
                  }
                  className={inputClass}
                  placeholder="Codigo"
                />
              </div>

              {/* Tooth */}
              <div className="md:col-span-1">
                <label className="text-xs text-gray-500">Dente</label>
                <input
                  type="text"
                  value={item.tooth_number}
                  onChange={(e) =>
                    updateItem(item.key, "tooth_number", e.target.value)
                  }
                  className={inputClass}
                  placeholder="11"
                />
              </div>

              {/* Surface */}
              <div className="md:col-span-1">
                <label className="text-xs text-gray-500">Face</label>
                <input
                  type="text"
                  value={item.surface}
                  onChange={(e) =>
                    updateItem(item.key, "surface", e.target.value)
                  }
                  className={inputClass}
                  placeholder="MO"
                />
              </div>

              {/* Quantity */}
              <div className="md:col-span-1">
                <label className="text-xs text-gray-500">Qtd</label>
                <input
                  type="number"
                  min={1}
                  value={item.quantity}
                  onChange={(e) =>
                    updateItem(
                      item.key,
                      "quantity",
                      parseInt(e.target.value) || 1
                    )
                  }
                  className={inputClass}
                />
              </div>

              {/* Price */}
              <div className="md:col-span-2">
                <label className="text-xs text-gray-500">
                  Preco (R$)
                </label>
                <input
                  type="text"
                  value={
                    item.unit_price_centavos > 0
                      ? (item.unit_price_centavos / 100)
                          .toFixed(2)
                          .replace(".", ",")
                      : ""
                  }
                  onChange={(e) => {
                    const val = parseFloat(
                      e.target.value.replace(",", ".")
                    );
                    updateItem(
                      item.key,
                      "unit_price_centavos",
                      isNaN(val) ? 0 : Math.round(val * 100)
                    );
                  }}
                  className={inputClass}
                  placeholder="0,00"
                />
              </div>
            </div>

            {/* Subtotal */}
            <div className="text-right text-sm text-gray-500">
              Subtotal:{" "}
              <span className="font-medium text-gray-700">
                {formatBRL(item.quantity * item.unit_price_centavos)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Discount + Total */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 pt-2 border-t">
        <div className="sm:w-48">
          <label className={labelClass}>Desconto (R$)</label>
          <input
            type="text"
            value={discountReais}
            onChange={(e) => setDiscountReais(e.target.value)}
            className={inputClass}
            placeholder="0,00"
          />
        </div>
        <div className="text-right space-y-1">
          <p className="text-sm text-gray-500">
            Subtotal: {formatBRL(totalCentavos)}
          </p>
          {discountCentavos > 0 && (
            <p className="text-sm text-red-500">
              Desconto: -{formatBRL(discountCentavos)}
            </p>
          )}
          <p className="text-lg font-bold text-teal-700">
            Total: {formatBRL(finalCentavos)}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Salvando..." : "Criar Plano"}
        </button>
      </div>
    </form>
  );
}
