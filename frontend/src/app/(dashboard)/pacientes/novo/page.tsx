"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import PatientForm from "@/components/patient/PatientForm";
import { createPatient } from "@/lib/api/patient";

export default function NovoPacientePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(data: Record<string, unknown>) {
    setLoading(true);
    setError(null);
    try {
      const patient = await createPatient(data);
      router.push(`/pacientes/${patient.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao cadastrar paciente");
      setLoading(false);
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link
          href="/pacientes"
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Novo Paciente</h1>
          <p className="text-sm text-gray-500">Preencha os dados para cadastrar um novo paciente</p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <PatientForm onSubmit={handleSubmit} loading={loading} />
    </div>
  );
}
