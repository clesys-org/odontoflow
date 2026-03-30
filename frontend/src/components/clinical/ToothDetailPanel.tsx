"use client";

import { useState, useEffect } from "react";
import type { Tooth, ToothSurface } from "@/lib/types/clinical";

const STATUS_OPTIONS = [
  { value: "PRESENT", label: "Presente" },
  { value: "ABSENT", label: "Ausente" },
  { value: "IMPLANT", label: "Implante" },
  { value: "DECIDUOUS", label: "Deciduo" },
  { value: "ROOT_REMNANT", label: "Resto radicular" },
];

const CONDITION_OPTIONS = [
  { value: "HEALTHY", label: "Saudavel", color: "#22c55e" },
  { value: "CARIES", label: "Carie", color: "#ef4444" },
  { value: "RESTORATION", label: "Restauracao", color: "#3b82f6" },
  { value: "FRACTURE", label: "Fratura", color: "#f59e0b" },
  { value: "SEALANT", label: "Selante", color: "#8b5cf6" },
  { value: "CROWN", label: "Coroa", color: "#6b7280" },
  { value: "VENEER", label: "Faceta", color: "#06b6d4" },
];

const SURFACES = [
  { position: "VESTIBULAR", label: "Vestibular" },
  { position: "LINGUAL", label: "Lingual" },
  { position: "MESIAL", label: "Mesial" },
  { position: "DISTAL", label: "Distal" },
  { position: "OCLUSAL", label: "Oclusal" },
];

interface ToothDetailPanelProps {
  tooth: Tooth | undefined;
  toothNumber: number;
  onSave: (data: {
    status: string;
    surfaces: { position: string; condition: string }[];
    notes: string | null;
  }) => Promise<void>;
  onClose: () => void;
  saving: boolean;
}

export default function ToothDetailPanel({
  tooth,
  toothNumber,
  onSave,
  onClose,
  saving,
}: ToothDetailPanelProps) {
  const [status, setStatus] = useState(tooth?.status || "PRESENT");
  const [surfaces, setSurfaces] = useState<Record<string, string>>(() => {
    const map: Record<string, string> = {};
    SURFACES.forEach((s) => {
      const existing = tooth?.surfaces.find((ts) => ts.position === s.position);
      map[s.position] = existing?.condition || "HEALTHY";
    });
    return map;
  });
  const [notes, setNotes] = useState(tooth?.notes || "");

  // Reset form when tooth changes
  useEffect(() => {
    setStatus(tooth?.status || "PRESENT");
    const map: Record<string, string> = {};
    SURFACES.forEach((s) => {
      const existing = tooth?.surfaces.find((ts) => ts.position === s.position);
      map[s.position] = existing?.condition || "HEALTHY";
    });
    setSurfaces(map);
    setNotes(tooth?.notes || "");
  }, [tooth, toothNumber]);

  function handleSurfaceChange(position: string, condition: string) {
    setSurfaces((prev) => ({ ...prev, [position]: condition }));
  }

  async function handleSubmit() {
    await onSave({
      status,
      surfaces: Object.entries(surfaces).map(([position, condition]) => ({
        position,
        condition,
      })),
      notes: notes.trim() || null,
    });
  }

  const inputClass =
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500";
  const labelClass = "block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1";

  return (
    <div className="bg-white rounded-xl shadow-sm border p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Dente {toothNumber}</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {tooth ? `Atualizado em ${new Date(tooth.updated_at).toLocaleDateString("pt-BR")}` : "Sem registro"}
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Status */}
      <div>
        <label className={labelClass}>Status do dente</label>
        <select value={status} onChange={(e) => setStatus(e.target.value)} className={inputClass}>
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      {/* Surfaces - only show if tooth is present-like */}
      {status !== "ABSENT" && (
        <div className="space-y-3">
          <p className={labelClass}>Faces dentarias</p>
          {SURFACES.map((s) => {
            const currentCondition = surfaces[s.position];
            const condOption = CONDITION_OPTIONS.find((c) => c.value === currentCondition);
            return (
              <div key={s.position} className="flex items-center gap-3">
                <span
                  className="w-3 h-3 rounded-full shrink-0 border border-gray-200"
                  style={{ backgroundColor: condOption?.color || "#22c55e" }}
                />
                <span className="text-sm text-gray-700 w-24 shrink-0">{s.label}</span>
                <select
                  value={currentCondition}
                  onChange={(e) => handleSurfaceChange(s.position, e.target.value)}
                  className="flex-1 px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  {CONDITION_OPTIONS.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>
            );
          })}
        </div>
      )}

      {/* Notes */}
      <div>
        <label className={labelClass}>Observacoes</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className={`${inputClass} resize-none`}
          rows={3}
          placeholder="Observacoes sobre este dente..."
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={onClose}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </button>
        <button
          onClick={handleSubmit}
          disabled={saving}
          className="flex-1 px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? "Salvando..." : "Salvar"}
        </button>
      </div>
    </div>
  );
}
