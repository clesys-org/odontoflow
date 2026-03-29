"use client";

import { useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { fetchPatient, updatePatient, deletePatient } from "@/lib/api/patient";
import PatientForm from "@/components/patient/PatientForm";
import { formatCPF, formatPhone } from "@/lib/utils/format";

const STATUS_BADGE: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  inactive: "bg-gray-100 text-gray-800",
  archived: "bg-red-100 text-red-800",
};

const STATUS_LABEL: Record<string, string> = {
  active: "Ativo",
  inactive: "Inativo",
  archived: "Arquivado",
};

type Tab = "dados" | "historico" | "financeiro";

export default function PacienteDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [activeTab, setActiveTab] = useState<Tab>("dados");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetcher = useCallback(() => fetchPatient(id), [id]);
  const { data: patient, loading, error: fetchError, refetch } = useApi(fetcher, [id]);

  async function handleUpdate(data: Record<string, unknown>) {
    setSaving(true);
    setError(null);
    try {
      await updatePatient(id, data);
      setEditing(false);
      refetch();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao atualizar paciente");
    } finally {
      setSaving(false);
    }
  }

  async function handleArchive() {
    if (!confirm("Tem certeza que deseja arquivar este paciente?")) return;
    try {
      await deletePatient(id);
      router.push("/pacientes");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao arquivar paciente");
    }
  }

  // Loading state
  if (loading && !patient) {
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
        <Link href="/pacientes" className="text-teal-600 hover:text-teal-800 text-sm font-medium">
          ← Voltar para pacientes
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

  if (!patient) return null;

  const tabs: { key: Tab; label: string }[] = [
    { key: "dados", label: "Dados" },
    { key: "historico", label: "Historico" },
    { key: "financeiro", label: "Financeiro" },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex items-start gap-3">
          <Link
            href="/pacientes"
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 mt-0.5"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{patient.full_name}</h1>
              <span
                className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  STATUS_BADGE[patient.status] || "bg-gray-100 text-gray-800"
                }`}
              >
                {STATUS_LABEL[patient.status] || patient.status}
              </span>
              {patient.is_minor && (
                <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-medium">
                  Menor de idade
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-sm text-gray-500">
              {patient.cpf_formatted && <span>CPF: {patient.cpf_formatted}</span>}
              {patient.age !== null && <span>{patient.age} anos</span>}
              {patient.phone_formatted && <span>Tel: {patient.phone_formatted}</span>}
            </div>
          </div>
        </div>

        <div className="flex gap-2 sm:shrink-0">
          {activeTab === "dados" && !editing && (
            <button
              onClick={() => setEditing(true)}
              className="px-4 py-2 border border-teal-600 text-teal-600 rounded-lg text-sm font-medium hover:bg-teal-50 transition-colors"
            >
              Editar
            </button>
          )}
          {patient.status !== "archived" && (
            <button
              onClick={handleArchive}
              className="px-4 py-2 border border-red-300 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors"
            >
              Arquivar
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

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key);
                if (tab.key !== "dados") setEditing(false);
              }}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? "border-teal-600 text-teal-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === "dados" && (
        <>
          {editing ? (
            <div>
              <PatientForm
                initialData={patient}
                onSubmit={handleUpdate}
                loading={saving}
              />
            </div>
          ) : (
            <PatientReadView patient={patient} />
          )}
        </>
      )}

      {activeTab === "historico" && (
        <div className="bg-white rounded-xl shadow-sm border p-8 text-center">
          <div className="text-gray-400">
            <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-lg font-medium mb-1">Prontuario clinico</p>
            <p className="text-sm">Sera implementado na Fase 1C</p>
          </div>
        </div>
      )}

      {activeTab === "financeiro" && (
        <div className="bg-white rounded-xl shadow-sm border p-8 text-center">
          <div className="text-gray-400">
            <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
              />
            </svg>
            <p className="text-lg font-medium mb-1">Financeiro do paciente</p>
            <p className="text-sm">Sera implementado na Fase 2</p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---- Read-only view component ---- */

import type { Patient } from "@/lib/types/patient";

function InfoRow({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <dt className="text-xs text-gray-500 uppercase tracking-wide">{label}</dt>
      <dd className="mt-0.5 text-sm text-gray-900">{value || "—"}</dd>
    </div>
  );
}

function PatientReadView({ patient }: { patient: Patient }) {
  return (
    <div className="space-y-6">
      {/* Dados Pessoais */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-base font-semibold mb-4">Dados Pessoais</h3>
        <dl className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <InfoRow label="Nome completo" value={patient.full_name} />
          <InfoRow label="CPF" value={patient.cpf_formatted || (patient.cpf ? formatCPF(patient.cpf) : null)} />
          <InfoRow label="Data de nascimento" value={patient.birth_date ? new Date(patient.birth_date + "T00:00:00").toLocaleDateString("pt-BR") : null} />
          <InfoRow label="Idade" value={patient.age !== null ? `${patient.age} anos` : null} />
          <InfoRow label="Genero" value={patient.gender} />
          <InfoRow label="Estado civil" value={patient.marital_status} />
          <InfoRow label="Profissao" value={patient.profession} />
        </dl>
      </section>

      {/* Contato */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-base font-semibold mb-4">Contato</h3>
        <dl className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <InfoRow label="Telefone" value={patient.phone_formatted || (patient.phone ? formatPhone(patient.phone) : null)} />
          <InfoRow label="WhatsApp" value={patient.whatsapp ? formatPhone(patient.whatsapp) : null} />
          <InfoRow label="Email" value={patient.email} />
          <InfoRow label="Canal preferido" value={patient.preferred_channel} />
        </dl>
      </section>

      {/* Endereco */}
      {patient.address && (
        <section className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-base font-semibold mb-4">Endereco</h3>
          <dl className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <InfoRow label="CEP" value={patient.address.zip_code} />
            <InfoRow label="Rua" value={patient.address.street} />
            <InfoRow label="Numero" value={patient.address.number} />
            <InfoRow label="Complemento" value={patient.address.complement} />
            <InfoRow label="Bairro" value={patient.address.neighborhood} />
            <InfoRow label="Cidade" value={patient.address.city} />
            <InfoRow label="Estado" value={patient.address.state} />
          </dl>
        </section>
      )}

      {/* Responsavel */}
      {patient.responsible && (
        <section className="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-amber-500">
          <h3 className="text-base font-semibold mb-4">Responsavel Legal</h3>
          <dl className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <InfoRow label="Nome" value={patient.responsible.name} />
            <InfoRow label="CPF" value={patient.responsible.cpf ? formatCPF(patient.responsible.cpf) : null} />
            <InfoRow label="Parentesco" value={patient.responsible.relationship} />
            <InfoRow label="Telefone" value={patient.responsible.phone ? formatPhone(patient.responsible.phone) : null} />
          </dl>
        </section>
      )}

      {/* Convenio */}
      {patient.insurance_info && (
        <section className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-base font-semibold mb-4">Convenio</h3>
          <dl className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <InfoRow label="Operadora" value={patient.insurance_info.provider_name} />
            <InfoRow label="Plano" value={patient.insurance_info.plan_name} />
            <InfoRow label="Carteirinha" value={patient.insurance_info.card_number} />
            <InfoRow label="Validade" value={patient.insurance_info.valid_until ? new Date(patient.insurance_info.valid_until + "T00:00:00").toLocaleDateString("pt-BR") : null} />
          </dl>
        </section>
      )}

      {/* Observacoes */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-base font-semibold mb-4">Observacoes</h3>
        <dl className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <InfoRow label="Como conheceu" value={patient.referral_source} />
          <InfoRow label="Tags" value={patient.tags.length > 0 ? patient.tags.join(", ") : null} />
          <div className="col-span-2 md:col-span-3">
            <InfoRow label="Observacoes" value={patient.notes} />
          </div>
        </dl>
      </section>

      {/* Meta */}
      <div className="text-xs text-gray-400 flex gap-4">
        <span>Cadastrado em: {new Date(patient.created_at).toLocaleDateString("pt-BR")}</span>
        <span>Atualizado em: {new Date(patient.updated_at).toLocaleDateString("pt-BR")}</span>
      </div>
    </div>
  );
}
