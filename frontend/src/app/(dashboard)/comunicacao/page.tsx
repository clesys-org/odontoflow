"use client";

import { useCallback, useState } from "react";
import { useApi } from "@/hooks/useApi";
import {
  fetchMessages,
  fetchTemplates,
  fetchCampaigns,
  createTemplate,
  sendMessage,
  createCampaign,
  executeCampaign,
} from "@/lib/api/communication";

type MessageStatus = "PENDING" | "SENT" | "DELIVERED" | "FAILED";

const STATUS_STYLES: Record<MessageStatus, { bg: string; text: string; label: string }> = {
  PENDING: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Pendente" },
  SENT: { bg: "bg-blue-100", text: "text-blue-800", label: "Enviada" },
  DELIVERED: { bg: "bg-green-100", text: "text-green-800", label: "Entregue" },
  FAILED: { bg: "bg-red-100", text: "text-red-800", label: "Falhou" },
};

const CAMPAIGN_STATUS: Record<string, { bg: string; text: string; label: string }> = {
  DRAFT: { bg: "bg-gray-100", text: "text-gray-800", label: "Rascunho" },
  SCHEDULED: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Agendada" },
  RUNNING: { bg: "bg-blue-100", text: "text-blue-800", label: "Executando" },
  COMPLETED: { bg: "bg-green-100", text: "text-green-800", label: "Concluida" },
  FAILED: { bg: "bg-red-100", text: "text-red-800", label: "Falhou" },
};

type Tab = "mensagens" | "templates" | "campanhas" | "enviar-mensagem" | "novo-template" | "nova-campanha";

export default function ComunicacaoPage() {
  const [tab, setTab] = useState<Tab>("mensagens");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [channelFilter, setChannelFilter] = useState<string>("");

  // Data fetchers
  const messagesFetcher = useCallback(
    () =>
      fetchMessages({
        status: statusFilter || undefined,
        channel: channelFilter || undefined,
      }),
    [statusFilter, channelFilter]
  );
  const {
    data: messagesData,
    loading: messagesLoading,
    error: messagesError,
    refetch: messagesRefetch,
  } = useApi(messagesFetcher, [statusFilter, channelFilter]);

  const templatesFetcher = useCallback(() => fetchTemplates(), []);
  const {
    data: templatesData,
    loading: templatesLoading,
    refetch: templatesRefetch,
  } = useApi(templatesFetcher, []);

  const campaignsFetcher = useCallback(() => fetchCampaigns(), []);
  const {
    data: campaignsData,
    loading: campaignsLoading,
    refetch: campaignsRefetch,
  } = useApi(campaignsFetcher, []);

  // Send message form
  const [messageForm, setMessageForm] = useState({
    patient_id: "",
    channel: "WHATSAPP",
    template_id: "",
    content: "",
  });

  // Template form
  const [templateForm, setTemplateForm] = useState({
    name: "",
    message_type: "REMINDER",
    channel: "WHATSAPP",
    content: "",
  });

  // Campaign form
  const [campaignForm, setCampaignForm] = useState({
    name: "",
    message_type: "MARKETING",
    channel: "WHATSAPP",
    template_id: "",
    scheduled_at: "",
  });

  const [submitting, setSubmitting] = useState(false);

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await sendMessage({
        patient_id: messageForm.patient_id,
        channel: messageForm.channel,
        template_id: messageForm.template_id || undefined,
        content: messageForm.content || undefined,
      });
      setMessageForm({ patient_id: "", channel: "WHATSAPP", template_id: "", content: "" });
      setTab("mensagens");
      messagesRefetch();
    } catch {
      /* handled */
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateTemplate(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createTemplate({
        name: templateForm.name,
        message_type: templateForm.message_type,
        channel: templateForm.channel,
        content: templateForm.content,
      });
      setTemplateForm({ name: "", message_type: "REMINDER", channel: "WHATSAPP", content: "" });
      setTab("templates");
      templatesRefetch();
    } catch {
      /* handled */
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateCampaign(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createCampaign({
        name: campaignForm.name,
        message_type: campaignForm.message_type,
        channel: campaignForm.channel,
        template_id: campaignForm.template_id,
        scheduled_at: campaignForm.scheduled_at || undefined,
      });
      setCampaignForm({
        name: "",
        message_type: "MARKETING",
        channel: "WHATSAPP",
        template_id: "",
        scheduled_at: "",
      });
      setTab("campanhas");
      campaignsRefetch();
    } catch {
      /* handled */
    } finally {
      setSubmitting(false);
    }
  }

  async function handleExecuteCampaign(id: string) {
    try {
      await executeCampaign(id);
      campaignsRefetch();
    } catch {
      /* handled */
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Comunicacao</h1>
          <p className="text-sm text-gray-500">Mensagens, templates e campanhas</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setTab("enviar-mensagem")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Enviar Mensagem
          </button>
          <button
            onClick={() => setTab("novo-template")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Novo Template
          </button>
          <button
            onClick={() => setTab("nova-campanha")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Nova Campanha
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-6">
          {[
            { key: "mensagens" as Tab, label: "Mensagens" },
            { key: "templates" as Tab, label: "Templates" },
            { key: "campanhas" as Tab, label: "Campanhas" },
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
      {messagesError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {messagesError}
          <button onClick={messagesRefetch} className="ml-2 underline">
            Tentar novamente
          </button>
        </div>
      )}

      {/* Messages List */}
      {tab === "mensagens" && (
        <>
          <div className="flex gap-3 items-center flex-wrap">
            <div className="flex gap-2 items-center">
              <label className="text-sm text-gray-600">Status:</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border rounded-lg px-3 py-1.5 text-sm"
              >
                <option value="">Todos</option>
                <option value="PENDING">Pendente</option>
                <option value="SENT">Enviada</option>
                <option value="DELIVERED">Entregue</option>
                <option value="FAILED">Falhou</option>
              </select>
            </div>
            <div className="flex gap-2 items-center">
              <label className="text-sm text-gray-600">Canal:</label>
              <select
                value={channelFilter}
                onChange={(e) => setChannelFilter(e.target.value)}
                className="border rounded-lg px-3 py-1.5 text-sm"
              >
                <option value="">Todos</option>
                <option value="WHATSAPP">WhatsApp</option>
                <option value="SMS">SMS</option>
                <option value="EMAIL">E-mail</option>
              </select>
            </div>
          </div>

          {messagesLoading && !messagesData && (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border p-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-48 mb-2" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-32" />
                </div>
              ))}
            </div>
          )}

          {messagesData && (
            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left px-4 py-3 font-medium text-gray-600">Paciente</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">Canal</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Tipo</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">Conteudo</th>
                      <th className="text-center px-4 py-3 font-medium text-gray-600">Status</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Data</th>
                    </tr>
                  </thead>
                  <tbody>
                    {messagesData.messages.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                          Nenhuma mensagem encontrada
                        </td>
                      </tr>
                    )}
                    {messagesData.messages.map((msg) => {
                      const style = STATUS_STYLES[msg.status as MessageStatus] || {
                        bg: "bg-gray-100",
                        text: "text-gray-800",
                        label: msg.status,
                      };
                      return (
                        <tr key={msg.id} className="border-b hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 font-medium text-gray-900">
                            {msg.patient_name || msg.patient_id}
                          </td>
                          <td className="px-4 py-3 text-gray-600">
                            <span className="inline-flex items-center gap-1.5">
                              {msg.channel === "WHATSAPP" && (
                                <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z" />
                                </svg>
                              )}
                              {msg.channel === "SMS" && (
                                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                </svg>
                              )}
                              {msg.channel === "EMAIL" && (
                                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                </svg>
                              )}
                              {msg.channel}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-gray-500 hidden md:table-cell">
                            {msg.message_type}
                          </td>
                          <td className="px-4 py-3 text-gray-500 hidden lg:table-cell max-w-xs truncate">
                            {msg.content}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.text}`}
                            >
                              {style.label}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-gray-500 hidden md:table-cell">
                            {msg.sent_at
                              ? new Date(msg.sent_at).toLocaleDateString("pt-BR")
                              : new Date(msg.created_at).toLocaleDateString("pt-BR")}
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

      {/* Templates List */}
      {tab === "templates" && (
        <>
          {templatesLoading && !templatesData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border p-5">
                  <div className="h-5 bg-gray-200 rounded animate-pulse w-36 mb-3" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-24" />
                </div>
              ))}
            </div>
          )}

          {templatesData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templatesData.templates.length === 0 && (
                <div className="col-span-full text-center py-12 text-gray-400">
                  Nenhum template cadastrado
                </div>
              )}
              {templatesData.templates.map((tpl) => (
                <div key={tpl.id} className="bg-white rounded-xl shadow-sm border p-5">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{tpl.name}</h3>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        tpl.active
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {tpl.active ? "Ativo" : "Inativo"}
                    </span>
                  </div>
                  <div className="flex gap-2 mb-3">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
                      {tpl.message_type}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                      {tpl.channel}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 line-clamp-3">{tpl.content}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Campaigns List */}
      {tab === "campanhas" && (
        <>
          {campaignsLoading && !campaignsData && (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border p-4">
                  <div className="h-5 bg-gray-200 rounded animate-pulse w-48 mb-2" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-32" />
                </div>
              ))}
            </div>
          )}

          {campaignsData && (
            <div className="space-y-4">
              {campaignsData.campaigns.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  Nenhuma campanha encontrada
                </div>
              )}
              {campaignsData.campaigns.map((camp) => {
                const style = CAMPAIGN_STATUS[camp.status] || {
                  bg: "bg-gray-100",
                  text: "text-gray-800",
                  label: camp.status,
                };
                const progress =
                  camp.messages_total > 0
                    ? Math.round((camp.messages_sent / camp.messages_total) * 100)
                    : 0;

                return (
                  <div key={camp.id} className="bg-white rounded-xl shadow-sm border p-5">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-gray-900">{camp.name}</h3>
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.text}`}
                          >
                            {style.label}
                          </span>
                        </div>
                        <div className="flex gap-3 text-xs text-gray-500">
                          <span>{camp.message_type}</span>
                          <span>{camp.channel}</span>
                          {camp.scheduled_at && (
                            <span>
                              Agendada: {new Date(camp.scheduled_at).toLocaleString("pt-BR")}
                            </span>
                          )}
                        </div>
                      </div>
                      {(camp.status === "SCHEDULED" || camp.status === "DRAFT") && (
                        <button
                          onClick={() => handleExecuteCampaign(camp.id)}
                          className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Executar
                        </button>
                      )}
                    </div>

                    {/* Progress bar */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>
                          {camp.messages_sent} de {camp.messages_total} enviadas
                          {camp.messages_failed > 0 && (
                            <span className="text-red-500 ml-2">
                              ({camp.messages_failed} falharam)
                            </span>
                          )}
                        </span>
                        <span>{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-teal-600 h-2 rounded-full transition-all"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* Send Message Form */}
      {tab === "enviar-mensagem" && (
        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Enviar Mensagem</h2>
          <form onSubmit={handleSendMessage} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ID Paciente
                </label>
                <input
                  type="text"
                  value={messageForm.patient_id}
                  onChange={(e) => setMessageForm({ ...messageForm, patient_id: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Canal</label>
                <select
                  value={messageForm.channel}
                  onChange={(e) => setMessageForm({ ...messageForm, channel: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="WHATSAPP">WhatsApp</option>
                  <option value="SMS">SMS</option>
                  <option value="EMAIL">E-mail</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Template (opcional)
              </label>
              <select
                value={messageForm.template_id}
                onChange={(e) => setMessageForm({ ...messageForm, template_id: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                <option value="">Mensagem personalizada</option>
                {templatesData?.templates.map((tpl) => (
                  <option key={tpl.id} value={tpl.id}>
                    {tpl.name} ({tpl.channel})
                  </option>
                ))}
              </select>
            </div>
            {!messageForm.template_id && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Conteudo da Mensagem
                </label>
                <textarea
                  value={messageForm.content}
                  onChange={(e) => setMessageForm({ ...messageForm, content: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  rows={4}
                  placeholder="Digite a mensagem..."
                  required={!messageForm.template_id}
                />
              </div>
            )}
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {submitting ? "Enviando..." : "Enviar Mensagem"}
              </button>
              <button
                type="button"
                onClick={() => setTab("mensagens")}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* New Template Form */}
      {tab === "novo-template" && (
        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Novo Template</h2>
          <form onSubmit={handleCreateTemplate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input
                type="text"
                value={templateForm.name}
                onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="Ex: Lembrete de Consulta"
                required
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                <select
                  value={templateForm.message_type}
                  onChange={(e) =>
                    setTemplateForm({ ...templateForm, message_type: e.target.value })
                  }
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="REMINDER">Lembrete</option>
                  <option value="CONFIRMATION">Confirmacao</option>
                  <option value="FOLLOW_UP">Retorno</option>
                  <option value="MARKETING">Marketing</option>
                  <option value="BIRTHDAY">Aniversario</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Canal</label>
                <select
                  value={templateForm.channel}
                  onChange={(e) => setTemplateForm({ ...templateForm, channel: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="WHATSAPP">WhatsApp</option>
                  <option value="SMS">SMS</option>
                  <option value="EMAIL">E-mail</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Conteudo</label>
              <textarea
                value={templateForm.content}
                onChange={(e) => setTemplateForm({ ...templateForm, content: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                rows={6}
                placeholder={`Use variaveis: {{patient_name}}, {{date}}, {{time}}\n\nEx: Ola {{patient_name}}, sua consulta esta agendada para {{date}} as {{time}}. Confirme respondendo SIM.`}
                required
              />
              <p className="mt-1.5 text-xs text-gray-400">
                Variaveis disponiveis: {"{{patient_name}}"}, {"{{date}}"}, {"{{time}}"}, {"{{clinic_name}}"}, {"{{doctor_name}}"}
              </p>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {submitting ? "Salvando..." : "Criar Template"}
              </button>
              <button
                type="button"
                onClick={() => setTab("templates")}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* New Campaign Form */}
      {tab === "nova-campanha" && (
        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Nova Campanha</h2>
          <form onSubmit={handleCreateCampaign} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome da Campanha
              </label>
              <input
                type="text"
                value={campaignForm.name}
                onChange={(e) => setCampaignForm({ ...campaignForm, name: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="Ex: Campanha Clareamento Junho"
                required
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                <select
                  value={campaignForm.message_type}
                  onChange={(e) =>
                    setCampaignForm({ ...campaignForm, message_type: e.target.value })
                  }
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="MARKETING">Marketing</option>
                  <option value="REMINDER">Lembrete</option>
                  <option value="FOLLOW_UP">Retorno</option>
                  <option value="BIRTHDAY">Aniversario</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Canal</label>
                <select
                  value={campaignForm.channel}
                  onChange={(e) => setCampaignForm({ ...campaignForm, channel: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="WHATSAPP">WhatsApp</option>
                  <option value="SMS">SMS</option>
                  <option value="EMAIL">E-mail</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Template</label>
              <select
                value={campaignForm.template_id}
                onChange={(e) =>
                  setCampaignForm({ ...campaignForm, template_id: e.target.value })
                }
                className="w-full border rounded-lg px-3 py-2 text-sm"
                required
              >
                <option value="">Selecione um template...</option>
                {templatesData?.templates.map((tpl) => (
                  <option key={tpl.id} value={tpl.id}>
                    {tpl.name} ({tpl.channel})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Agendar para (opcional)
              </label>
              <input
                type="datetime-local"
                value={campaignForm.scheduled_at}
                onChange={(e) =>
                  setCampaignForm({ ...campaignForm, scheduled_at: e.target.value })
                }
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {submitting ? "Criando..." : "Criar Campanha"}
              </button>
              <button
                type="button"
                onClick={() => setTab("campanhas")}
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
