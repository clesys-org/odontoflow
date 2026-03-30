"use client";

import { useState } from "react";

const NOTE_TYPES = [
  { value: "EVOLUTION", label: "Evolucao" },
  { value: "PROCEDURE", label: "Procedimento" },
  { value: "OBSERVATION", label: "Observacao" },
];

interface ClinicalNoteFormProps {
  onSubmit: (data: {
    note_type: string;
    content: string;
    tooth_references: number[];
  }) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
}

export default function ClinicalNoteForm({
  onSubmit,
  onCancel,
  loading,
}: ClinicalNoteFormProps) {
  const [noteType, setNoteType] = useState("EVOLUTION");
  const [content, setContent] = useState("");
  const [toothRefsInput, setToothRefsInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!content.trim()) {
      setError("O conteudo da nota e obrigatorio.");
      return;
    }

    const toothRefs = toothRefsInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .map(Number)
      .filter((n) => !isNaN(n) && n > 0);

    try {
      await onSubmit({
        note_type: noteType,
        content: content.trim(),
        tooth_references: toothRefs,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar nota.");
    }
  }

  const inputClass =
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border p-5 space-y-4">
      <h3 className="text-base font-semibold">Nova Nota Clinica</h3>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Tipo da nota</label>
          <select value={noteType} onChange={(e) => setNoteType(e.target.value)} className={inputClass}>
            {NOTE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className={labelClass}>Dentes referenciados</label>
          <input
            type="text"
            value={toothRefsInput}
            onChange={(e) => setToothRefsInput(e.target.value)}
            className={inputClass}
            placeholder="Ex: 11, 21, 36 (separar por virgula)"
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>
          Conteudo <span className="text-red-500">*</span>
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className={`${inputClass} resize-none`}
          rows={5}
          placeholder="Descreva a evolucao, procedimento ou observacao..."
        />
      </div>

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
          {loading ? "Salvando..." : "Salvar Nota"}
        </button>
      </div>
    </form>
  );
}
