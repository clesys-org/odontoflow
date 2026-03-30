"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchOdontogram, updateTooth } from "@/lib/api/clinical";
import { fetchPatient } from "@/lib/api/patient";
import type { Tooth } from "@/lib/types/clinical";
import type { Patient } from "@/lib/types/patient";
import OdontogramSVG from "@/components/clinical/OdontogramSVG";
import ToothDetailPanel from "@/components/clinical/ToothDetailPanel";

const CONDITION_COLORS: Record<string, { color: string; label: string }> = {
  HEALTHY: { color: "#22c55e", label: "Saudavel" },
  CARIES: { color: "#ef4444", label: "Carie" },
  RESTORATION: { color: "#3b82f6", label: "Restauracao" },
  FRACTURE: { color: "#f59e0b", label: "Fratura" },
  SEALANT: { color: "#8b5cf6", label: "Selante" },
  CROWN: { color: "#6b7280", label: "Coroa" },
  VENEER: { color: "#06b6d4", label: "Faceta" },
};

const STATUS_COLORS: Record<string, { style: string; label: string }> = {
  PRESENT: { style: "border-gray-300", label: "Presente" },
  ABSENT: { style: "border-dashed border-gray-400 bg-gray-100", label: "Ausente" },
  IMPLANT: { style: "border-blue-400 bg-blue-50", label: "Implante" },
  DECIDUOUS: { style: "border-purple-300", label: "Deciduo" },
  ROOT_REMNANT: { style: "border-amber-500", label: "Raiz residual" },
};

export default function OdontogramaPage() {
  const params = useParams();
  const patientId = params.id as string;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [teeth, setTeeth] = useState<Tooth[]>([]);
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [p, data] = await Promise.all([
        fetchPatient(patientId),
        fetchOdontogram(patientId),
      ]);
      setPatient(p);
      setTeeth(data.teeth || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao carregar odontograma");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [patientId]);

  const selectedToothData = teeth.find((t) => t.tooth_number === selectedTooth) || null;

  async function handleSaveTooth(data: {
    status: string;
    surfaces: { position: string; condition: string }[];
    notes: string | null;
  }) {
    if (!selectedTooth) return;
    setSaving(true);
    try {
      await updateTooth(patientId, selectedTooth, data);
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erro ao salvar");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="p-6 lg:p-8 space-y-4">
        <div className="h-8 bg-gray-200 rounded w-64 animate-pulse" />
        <div className="h-80 bg-gray-200 rounded animate-pulse" />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div>
        <Link href={`/pacientes/${patientId}/prontuario`} className="text-sm text-teal-600 hover:underline">
          ← Voltar para prontuario
        </Link>
        <h1 className="text-2xl font-bold mt-1">
          Odontograma — {patient?.full_name || "Paciente"}
        </h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          {error}
          <button onClick={load} className="ml-4 underline">Tentar novamente</button>
        </div>
      )}

      {/* Main content */}
      <div className="flex gap-6">
        {/* Odontogram SVG */}
        <div className="flex-1 bg-white rounded-xl shadow-sm border p-6">
          <div className="flex justify-center overflow-x-auto">
            <OdontogramSVG
              teeth={teeth}
              onToothClick={(num) => setSelectedTooth(num === selectedTooth ? null : num)}
              selectedTooth={selectedTooth}
            />
          </div>

          {/* Legend - Conditions */}
          <div className="mt-6 border-t pt-4">
            <p className="text-xs font-medium text-gray-500 mb-2">Condicoes das faces</p>
            <div className="flex flex-wrap gap-3">
              {Object.entries(CONDITION_COLORS).map(([key, { color, label }]) => (
                <div key={key} className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
                  <span className="text-xs text-gray-600">{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Legend - Tooth Status */}
          <div className="mt-3">
            <p className="text-xs font-medium text-gray-500 mb-2">Status do dente</p>
            <div className="flex flex-wrap gap-3">
              {Object.entries(STATUS_COLORS).map(([key, { label }]) => (
                <div key={key} className="flex items-center gap-1.5">
                  <div className={`w-3 h-3 border-2 rounded-sm ${STATUS_COLORS[key].style}`} />
                  <span className="text-xs text-gray-600">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Tooth Detail Panel */}
        {selectedTooth && (
          <div className="w-80 shrink-0">
            <ToothDetailPanel
              tooth={selectedToothData || undefined}
              toothNumber={selectedTooth}
              onSave={handleSaveTooth}
              onClose={() => setSelectedTooth(null)}
              saving={saving}
            />
          </div>
        )}
      </div>
    </div>
  );
}
