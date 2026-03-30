"use client";

import { useCallback, useState } from "react";
import { useApi } from "@/hooks/useApi";
import {
  fetchTISSRequests,
  fetchInsuranceProviders,
  createTISSRequest,
  createInsuranceProvider,
} from "@/lib/api/insurance";
import type { TISSStatus } from "@/lib/types/insurance";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

const STATUS_STYLES: Record<TISSStatus, { bg: string; text: string; label: string }> = {
  PENDING: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Pendente" },
  AUTHORIZED: { bg: "bg-green-100", text: "text-green-800", label: "Autorizada" },
  DENIED: { bg: "bg-red-100", text: "text-red-800", label: "Negada" },
  BILLED: { bg: "bg-blue-100", text: "text-blue-800", label: "Faturada" },
  PAID: { bg: "bg-teal-100", text: "text-teal-800", label: "Paga" },
  GLOSA: { bg: "bg-orange-100", text: "text-orange-800", label: "Glosa" },
};

type Tab = "guias" | "convenios" | "nova-guia" | "novo-convenio";

export default function ConveniosPage() {
  const [tab, setTab] = useState<Tab>("guias");
  const [statusFilter, setStatusFilter] = useState<TISSStatus | "">("");

  const tissFetcher = useCallback(
    () => fetchTISSRequests(statusFilter ? { status: statusFilter as TISSStatus } : undefined),
    [statusFilter]
  );
  const { data: tissData, loading: tissLoading, error: tissError, refetch: tissRefetch } =
    useApi(tissFetcher, [statusFilter]);

  const providersFetcher = useCallback(() => fetchInsuranceProviders(), []);
  const {
    data: providersData,
    loading: providersLoading,
    refetch: providersRefetch,
  } = useApi(providersFetcher, []);

  // Form states
  const [guiaForm, setGuiaForm] = useState({
    patient_id: "",
    insurance_provider_id: "",
    tuss_code: "",
    procedure_description: "",
    tooth_number: "",
    requested_amount_centavos: "",
  });
  const [convenioForm, setConvenioForm] = useState({
    name: "",
    ans_code: "",
    contact_phone: "",
    contact_email: "",
  });
  const [submitting, setSubmitting] = useState(false);

  async function handleCreateGuia(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createTISSRequest({
        patient_id: guiaForm.patient_id,
        insurance_provider_id: guiaForm.insurance_provider_id,
        tuss_code: guiaForm.tuss_code,
        procedure_description: guiaForm.procedure_description,
        tooth_number: guiaForm.tooth_number ? Number(guiaForm.tooth_number) : undefined,
        requested_amount_centavos: Number(guiaForm.requested_amount_centavos),
      });
      setGuiaForm({
        patient_id: "",
        insurance_provider_id: "",
        tuss_code: "",
        procedure_description: "",
        tooth_number: "",
        requested_amount_centavos: "",
      });
      setTab("guias");
      tissRefetch();
    } catch {
      /* error handled by UI */
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateConvenio(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createInsuranceProvider({
        name: convenioForm.name,
        ans_code: convenioForm.ans_code,
        contact_phone: convenioForm.contact_phone || undefined,
        contact_email: convenioForm.contact_email || undefined,
      });
      setConvenioForm({ name: "", ans_code: "", contact_phone: "", contact_email: "" });
      setTab("convenios");
      providersRefetch();
    } catch {
      /* error handled by UI */
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Convenios & TISS</h1>
          <p className="text-sm text-gray-500">Gerenciamento de guias e convenios</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setTab("nova-guia")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nova Guia TISS
          </button>
          <button
            onClick={() => setTab("novo-convenio")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Novo Convenio
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-6">
          {[
            { key: "guias" as Tab, label: "Guias TISS" },
            { key: "convenios" as Tab, label: "Convenios" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key
                  ? "border-teal-600 text-teal-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Error */}
      {tissError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {tissError}
          <button onClick={tissRefetch} className="ml-2 underline">
            Tentar novamente
          </button>
        </div>
      )}

      {/* TISS Requests List */}
      {tab === "guias" && (
        <>
          {/* Filter */}
          <div className="flex gap-3 items-center">
            <label className="text-sm text-gray-600">Status:</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as TISSStatus | "")}
              className="border rounded-lg px-3 py-1.5 text-sm"
            >
              <option value="">Todos</option>
              <option value="PENDING">Pendente</option>
              <option value="AUTHORIZED">Autorizada</option>
              <option value="DENIED">Negada</option>
              <option value="BILLED">Faturada</option>
              <option value="PAID">Paga</option>
              <option value="GLOSA">Glosa</option>
            </select>
          </div>

          {tissLoading && !tissData && (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border p-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-48 mb-2" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-32" />
                </div>
              ))}
            </div>
          )}

          {tissData && (
            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left px-4 py-3 font-medium text-gray-600">Paciente</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">Procedimento</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">Convenio</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">TUSS</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">Valor</th>
                      <th className="text-center px-4 py-3 font-medium text-gray-600">Status</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Data</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tissData.requests.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                          Nenhuma guia TISS encontrada
                        </td>
                      </tr>
                    )}
                    {tissData.requests.map((req) => {
                      const style = STATUS_STYLES[req.status];
                      return (
                        <tr key={req.id} className="border-b hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 font-medium text-gray-900">{req.patient_name}</td>
                          <td className="px-4 py-3 text-gray-600">{req.procedure_description}</td>
                          <td className="px-4 py-3 text-gray-600">{req.insurance_provider_name}</td>
                          <td className="px-4 py-3 text-gray-500 font-mono text-xs">{req.tuss_code}</td>
                          <td className="px-4 py-3 text-right font-medium">
                            {formatBRL(req.requested_amount_centavos)}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.text}`}
                            >
                              {style.label}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-gray-500 hidden md:table-cell">
                            {new Date(req.created_at).toLocaleDateString("pt-BR")}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Insurance Providers List */}
      {tab === "convenios" && (
        <>
          {providersLoading && !providersData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border p-5">
                  <div className="h-5 bg-gray-200 rounded animate-pulse w-36 mb-3" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-24" />
                </div>
              ))}
            </div>
          )}

          {providersData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {providersData.providers.length === 0 && (
                <div className="col-span-full text-center py-12 text-gray-400">
                  Nenhum convenio cadastrado
                </div>
              )}
              {providersData.providers.map((prov) => (
                <div key={prov.id} className="bg-white rounded-xl shadow-sm border p-5">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{prov.name}</h3>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        prov.active
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {prov.active ? "Ativo" : "Inativo"}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">ANS: {prov.ans_code}</p>
                  {prov.contact_phone && (
                    <p className="text-sm text-gray-500 mt-1">Tel: {prov.contact_phone}</p>
                  )}
                  {prov.contact_email && (
                    <p className="text-sm text-gray-500 mt-1">{prov.contact_email}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* New TISS Request Form */}
      {tab === "nova-guia" && (
        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Nova Guia TISS</h2>
          <form onSubmit={handleCreateGuia} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ID Paciente
                </label>
                <input
                  type="text"
                  value={guiaForm.patient_id}
                  onChange={(e) => setGuiaForm({ ...guiaForm, patient_id: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Convenio
                </label>
                <select
                  value={guiaForm.insurance_provider_id}
                  onChange={(e) =>
                    setGuiaForm({ ...guiaForm, insurance_provider_id: e.target.value })
                  }
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                >
                  <option value="">Selecione...</option>
                  {providersData?.providers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Codigo TUSS
                </label>
                <input
                  type="text"
                  value={guiaForm.tuss_code}
                  onChange={(e) => setGuiaForm({ ...guiaForm, tuss_code: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dente (opcional)
                </label>
                <input
                  type="number"
                  value={guiaForm.tooth_number}
                  onChange={(e) => setGuiaForm({ ...guiaForm, tooth_number: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  min={11}
                  max={48}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descricao do Procedimento
              </label>
              <input
                type="text"
                value={guiaForm.procedure_description}
                onChange={(e) =>
                  setGuiaForm({ ...guiaForm, procedure_description: e.target.value })
                }
                className="w-full border rounded-lg px-3 py-2 text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Valor Solicitado (centavos)
              </label>
              <input
                type="number"
                value={guiaForm.requested_amount_centavos}
                onChange={(e) =>
                  setGuiaForm({ ...guiaForm, requested_amount_centavos: e.target.value })
                }
                className="w-full border rounded-lg px-3 py-2 text-sm"
                min={1}
                required
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {submitting ? "Enviando..." : "Criar Guia"}
              </button>
              <button
                type="button"
                onClick={() => setTab("guias")}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* New Insurance Provider Form */}
      {tab === "novo-convenio" && (
        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Novo Convenio</h2>
          <form onSubmit={handleCreateConvenio} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                <input
                  type="text"
                  value={convenioForm.name}
                  onChange={(e) => setConvenioForm({ ...convenioForm, name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Codigo ANS
                </label>
                <input
                  type="text"
                  value={convenioForm.ans_code}
                  onChange={(e) =>
                    setConvenioForm({ ...convenioForm, ans_code: e.target.value })
                  }
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefone
                </label>
                <input
                  type="text"
                  value={convenioForm.contact_phone}
                  onChange={(e) =>
                    setConvenioForm({ ...convenioForm, contact_phone: e.target.value })
                  }
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
                <input
                  type="email"
                  value={convenioForm.contact_email}
                  onChange={(e) =>
                    setConvenioForm({ ...convenioForm, contact_email: e.target.value })
                  }
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {submitting ? "Salvando..." : "Cadastrar Convenio"}
              </button>
              <button
                type="button"
                onClick={() => setTab("convenios")}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
