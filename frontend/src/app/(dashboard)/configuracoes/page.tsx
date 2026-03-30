"use client";

import { useCallback, useState, useEffect } from "react";
import { useApi } from "@/hooks/useApi";
import { fetchWebsite, updateWebsite, togglePublish } from "@/lib/api/website";
import type { ServiceItem } from "@/lib/types/website";

const DEFAULT_COLORS = [
  "#0d9488", "#0891b2", "#2563eb", "#7c3aed", "#db2777", "#dc2626",
  "#ea580c", "#16a34a", "#ca8a04", "#475569",
];

const APPOINTMENT_TYPES = [
  "Consulta Avaliacao",
  "Limpeza",
  "Clareamento",
  "Ortodontia",
  "Implante",
  "Restauracao",
  "Extracao",
  "Canal",
];

export default function ConfiguracoesPage() {
  const websiteFetcher = useCallback(() => fetchWebsite(), []);
  const {
    data: websiteData,
    loading: websiteLoading,
    error: websiteError,
    refetch: websiteRefetch,
  } = useApi(websiteFetcher, []);

  // Website form
  const [form, setForm] = useState({
    clinic_name: "",
    tagline: "",
    description: "",
    phone: "",
    whatsapp: "",
    email: "",
    address: "",
    primary_color: "#0d9488",
    working_hours_text: "",
    seo_title: "",
    seo_description: "",
    google_maps_url: "",
    instagram: "",
    facebook: "",
    booking_enabled: false,
    published: false,
  });

  const [services, setServices] = useState<ServiceItem[]>([]);
  const [newService, setNewService] = useState<ServiceItem>({
    name: "",
    description: "",
    icon: "tooth",
  });

  // Widget settings
  const [widgetActive, setWidgetActive] = useState(false);
  const [widgetTypes, setWidgetTypes] = useState<string[]>(["Consulta Avaliacao", "Limpeza"]);
  const [widgetMaxDays, setWidgetMaxDays] = useState(30);

  const [submitting, setSubmitting] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Populate form when data loads
  useEffect(() => {
    if (websiteData) {
      setForm({
        clinic_name: websiteData.clinic_name || "",
        tagline: websiteData.tagline || "",
        description: websiteData.description || "",
        phone: websiteData.phone || "",
        whatsapp: websiteData.whatsapp || "",
        email: websiteData.email || "",
        address: websiteData.address || "",
        primary_color: websiteData.primary_color || "#0d9488",
        working_hours_text: websiteData.working_hours_text || "",
        seo_title: websiteData.seo_title || "",
        seo_description: websiteData.seo_description || "",
        google_maps_url: "",
        instagram: websiteData.social_links?.instagram || "",
        facebook: websiteData.social_links?.facebook || "",
        booking_enabled: websiteData.booking_enabled,
        published: websiteData.published,
      });
      setServices(websiteData.services || []);
    }
  }, [websiteData]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setSaveSuccess(false);
    try {
      await updateWebsite({
        clinic_name: form.clinic_name,
        tagline: form.tagline || null,
        description: form.description || null,
        phone: form.phone || null,
        whatsapp: form.whatsapp || null,
        email: form.email || null,
        address: form.address || null,
        primary_color: form.primary_color,
        services,
        working_hours_text: form.working_hours_text || null,
        social_links: {
          ...(form.instagram ? { instagram: form.instagram } : {}),
          ...(form.facebook ? { facebook: form.facebook } : {}),
        },
        seo_title: form.seo_title || null,
        seo_description: form.seo_description || null,
        booking_enabled: form.booking_enabled,
      });
      setSaveSuccess(true);
      websiteRefetch();
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch {
      /* handled */
    } finally {
      setSubmitting(false);
    }
  }

  async function handleTogglePublish() {
    try {
      await togglePublish();
      websiteRefetch();
    } catch {
      /* handled */
    }
  }

  function addService() {
    if (!newService.name) return;
    setServices([...services, { ...newService }]);
    setNewService({ name: "", description: "", icon: "tooth" });
  }

  function removeService(index: number) {
    setServices(services.filter((_, i) => i !== index));
  }

  function toggleWidgetType(type: string) {
    setWidgetTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  }

  const embedCode = `<!-- OdontoFlow Agendamento Widget -->
<iframe
  src="${typeof window !== "undefined" ? window.location.origin : ""}/widget/booking/${websiteData?.slug || "sua-clinica"}"
  width="100%"
  height="600"
  frameborder="0"
  style="border: none; border-radius: 12px;"
></iframe>`;

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Configuracoes</h1>
        <p className="text-sm text-gray-500">Site da clinica e configuracoes do sistema</p>
      </div>

      {/* Error */}
      {websiteError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {websiteError}
          <button onClick={websiteRefetch} className="ml-2 underline">
            Tentar novamente
          </button>
        </div>
      )}

      {/* Save success */}
      {saveSuccess && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
          Configuracoes salvas com sucesso!
        </div>
      )}

      {/* Loading skeleton */}
      {websiteLoading && !websiteData && (
        <div className="space-y-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border p-6">
              <div className="h-6 bg-gray-200 rounded animate-pulse w-48 mb-4" />
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded animate-pulse w-full" />
                <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
              </div>
            </div>
          ))}
        </div>
      )}

      {websiteData && (
        <form onSubmit={handleSave} className="space-y-8">
          {/* ===== SECTION 1: Site da Clinica ===== */}
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900">Site da Clinica</h2>
              <p className="text-sm text-gray-500">Informacoes exibidas no site publico</p>
            </div>

            {/* Preview Card */}
            <div className="px-6 pt-6">
              <div
                className="rounded-xl border-2 overflow-hidden"
                style={{ borderColor: form.primary_color }}
              >
                <div
                  className="px-6 py-8 text-white"
                  style={{ backgroundColor: form.primary_color }}
                >
                  <h3 className="text-xl font-bold">{form.clinic_name || "Nome da Clinica"}</h3>
                  <p className="text-white/80 mt-1">{form.tagline || "Seu sorriso, nossa prioridade"}</p>
                </div>
                <div className="px-6 py-4 bg-white">
                  <p className="text-sm text-gray-600">
                    {form.description || "Descricao da clinica aparecera aqui..."}
                  </p>
                  <div className="flex gap-4 mt-3 text-xs text-gray-500">
                    {form.phone && <span>Tel: {form.phone}</span>}
                    {form.email && <span>{form.email}</span>}
                  </div>
                  {services.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {services.map((svc, i) => (
                        <span
                          key={i}
                          className="text-xs px-2 py-1 rounded-full"
                          style={{
                            backgroundColor: `${form.primary_color}20`,
                            color: form.primary_color,
                          }}
                        >
                          {svc.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="px-6 py-3 bg-gray-50 border-t flex items-center justify-between">
                  <span className="text-xs text-gray-400">
                    {websiteData.slug}.odontoflow.com.br
                  </span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      form.published
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {form.published ? "Publicado" : "Rascunho"}
                  </span>
                </div>
              </div>
            </div>

            <div className="px-6 py-6 space-y-6">
              {/* Basic info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nome da Clinica
                  </label>
                  <input
                    type="text"
                    value={form.clinic_name}
                    onChange={(e) => setForm({ ...form, clinic_name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tagline</label>
                  <input
                    type="text"
                    value={form.tagline}
                    onChange={(e) => setForm({ ...form, tagline: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="Frase curta sobre a clinica"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descricao</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  rows={3}
                  placeholder="Sobre a clinica..."
                />
              </div>

              {/* Contact info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
                  <input
                    type="text"
                    value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="(11) 3000-0000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">WhatsApp</label>
                  <input
                    type="text"
                    value={form.whatsapp}
                    onChange={(e) => setForm({ ...form, whatsapp: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="(11) 99000-0000"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="contato@clinica.com.br"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Endereco</label>
                  <input
                    type="text"
                    value={form.address}
                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="Rua, numero - Bairro, Cidade - UF"
                  />
                </div>
              </div>

              {/* Color picker */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cor Principal
                </label>
                <div className="flex gap-3 items-center flex-wrap">
                  {DEFAULT_COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setForm({ ...form, primary_color: color })}
                      className={`w-8 h-8 rounded-full border-2 transition-transform ${
                        form.primary_color === color
                          ? "border-gray-900 scale-110"
                          : "border-transparent hover:scale-105"
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                  <input
                    type="color"
                    value={form.primary_color}
                    onChange={(e) => setForm({ ...form, primary_color: e.target.value })}
                    className="w-8 h-8 rounded cursor-pointer border-0"
                    title="Cor personalizada"
                  />
                </div>
              </div>

              {/* Services */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Servicos</label>
                {services.length > 0 && (
                  <div className="space-y-2 mb-3">
                    {services.map((svc, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2"
                      >
                        <div>
                          <span className="text-sm font-medium text-gray-900">{svc.name}</span>
                          {svc.description && (
                            <span className="text-xs text-gray-500 ml-2">{svc.description}</span>
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={() => removeService(i)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          Remover
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newService.name}
                    onChange={(e) => setNewService({ ...newService, name: e.target.value })}
                    className="flex-1 border rounded-lg px-3 py-2 text-sm"
                    placeholder="Nome do servico"
                  />
                  <input
                    type="text"
                    value={newService.description}
                    onChange={(e) =>
                      setNewService({ ...newService, description: e.target.value })
                    }
                    className="flex-1 border rounded-lg px-3 py-2 text-sm"
                    placeholder="Descricao curta"
                  />
                  <select
                    value={newService.icon}
                    onChange={(e) => setNewService({ ...newService, icon: e.target.value })}
                    className="border rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="tooth">Dente</option>
                    <option value="smile">Sorriso</option>
                    <option value="xray">Raio-X</option>
                    <option value="braces">Aparelho</option>
                    <option value="implant">Implante</option>
                    <option value="whitening">Clareamento</option>
                    <option value="surgery">Cirurgia</option>
                    <option value="pediatric">Pediatrico</option>
                  </select>
                  <button
                    type="button"
                    onClick={addService}
                    className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
                  >
                    Adicionar
                  </button>
                </div>
              </div>

              {/* Working hours */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Horario de Funcionamento
                </label>
                <textarea
                  value={form.working_hours_text}
                  onChange={(e) => setForm({ ...form, working_hours_text: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  rows={3}
                  placeholder={"Seg-Sex: 08:00 - 18:00\nSab: 08:00 - 12:00\nDom: Fechado"}
                />
              </div>

              {/* Social links */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Instagram
                  </label>
                  <input
                    type="text"
                    value={form.instagram}
                    onChange={(e) => setForm({ ...form, instagram: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="https://instagram.com/suaclinica"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Facebook</label>
                  <input
                    type="text"
                    value={form.facebook}
                    onChange={(e) => setForm({ ...form, facebook: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    placeholder="https://facebook.com/suaclinica"
                  />
                </div>
              </div>

              {/* SEO */}
              <div className="border-t pt-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">SEO</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Titulo SEO
                    </label>
                    <input
                      type="text"
                      value={form.seo_title}
                      onChange={(e) => setForm({ ...form, seo_title: e.target.value })}
                      className="w-full border rounded-lg px-3 py-2 text-sm"
                      placeholder="Clinica Odontologica | Seu Nome | Cidade"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Descricao SEO
                    </label>
                    <textarea
                      value={form.seo_description}
                      onChange={(e) => setForm({ ...form, seo_description: e.target.value })}
                      className="w-full border rounded-lg px-3 py-2 text-sm"
                      rows={2}
                      placeholder="Clinica odontologica especializada em..."
                    />
                  </div>
                </div>
              </div>

              {/* Google Maps */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL Google Maps (embed)
                </label>
                <input
                  type="text"
                  value={form.google_maps_url}
                  onChange={(e) => setForm({ ...form, google_maps_url: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  placeholder="https://www.google.com/maps/embed?pb=..."
                />
              </div>

              {/* Toggles */}
              <div className="flex flex-col gap-3 border-t pt-6">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.booking_enabled}
                    onChange={(e) => setForm({ ...form, booking_enabled: e.target.checked })}
                    className="rounded border-gray-300 text-teal-600 w-5 h-5"
                  />
                  <div>
                    <span className="text-sm font-medium text-gray-900">
                      Agendamento Online
                    </span>
                    <p className="text-xs text-gray-500">
                      Permitir que pacientes agendem pelo site
                    </p>
                  </div>
                </label>
              </div>

              {/* Action buttons */}
              <div className="flex gap-3 pt-4 border-t">
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
                >
                  {submitting ? "Salvando..." : "Salvar Configuracoes"}
                </button>
                <button
                  type="button"
                  onClick={handleTogglePublish}
                  className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    websiteData.published
                      ? "bg-orange-100 text-orange-700 hover:bg-orange-200"
                      : "bg-green-100 text-green-700 hover:bg-green-200"
                  }`}
                >
                  {websiteData.published ? "Despublicar Site" : "Publicar Site"}
                </button>
              </div>
            </div>
          </div>

          {/* ===== SECTION 2: Widget de Agendamento ===== */}
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900">Widget de Agendamento</h2>
              <p className="text-sm text-gray-500">
                Incorpore o agendamento em qualquer site externo
              </p>
            </div>

            <div className="px-6 py-6 space-y-6">
              {/* Toggle active */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={widgetActive}
                  onChange={(e) => setWidgetActive(e.target.checked)}
                  className="rounded border-gray-300 text-teal-600 w-5 h-5"
                />
                <div>
                  <span className="text-sm font-medium text-gray-900">Widget Ativo</span>
                  <p className="text-xs text-gray-500">
                    Habilitar widget de agendamento para embed externo
                  </p>
                </div>
              </label>

              {widgetActive && (
                <>
                  {/* Appointment types */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tipos de Consulta Disponiveis
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {APPOINTMENT_TYPES.map((type) => (
                        <label
                          key={type}
                          className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer transition-colors text-sm ${
                            widgetTypes.includes(type)
                              ? "border-teal-600 bg-teal-50 text-teal-800"
                              : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={widgetTypes.includes(type)}
                            onChange={() => toggleWidgetType(type)}
                            className="rounded border-gray-300 text-teal-600"
                          />
                          {type}
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Max days ahead */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Maximo de dias para agendamento: <span className="text-teal-600 font-semibold">{widgetMaxDays} dias</span>
                    </label>
                    <input
                      type="range"
                      min={7}
                      max={90}
                      step={1}
                      value={widgetMaxDays}
                      onChange={(e) => setWidgetMaxDays(Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>7 dias</span>
                      <span>30 dias</span>
                      <span>60 dias</span>
                      <span>90 dias</span>
                    </div>
                  </div>

                  {/* Embed code preview */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Codigo de Incorporacao
                    </label>
                    <div className="relative">
                      <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 text-xs overflow-x-auto">
                        <code>{embedCode}</code>
                      </pre>
                      <button
                        type="button"
                        onClick={() => {
                          navigator.clipboard.writeText(embedCode);
                        }}
                        className="absolute top-2 right-2 px-3 py-1.5 bg-gray-700 text-gray-200 rounded text-xs font-medium hover:bg-gray-600 transition-colors"
                      >
                        Copiar
                      </button>
                    </div>
                    <p className="mt-2 text-xs text-gray-400">
                      Cole este codigo no HTML do site onde deseja exibir o widget de agendamento.
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
