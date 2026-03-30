"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  fetchPatientRecord,
  createAnamnesis,
  fetchNotes,
  createNote,
  fetchPrescriptions,
  createPrescription,
} from "@/lib/api/clinical";
import { fetchPatient } from "@/lib/api/patient";
import type { PatientRecord, ClinicalNote, Prescription } from "@/lib/types/clinical";
import type { Patient } from "@/lib/types/patient";
import ClinicalNoteForm from "@/components/clinical/ClinicalNoteForm";
import TimelineEntry from "@/components/clinical/TimelineEntry";

export default function ProntuarioPage() {
  const params = useParams();
  const patientId = params.id as string;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [record, setRecord] = useState<PatientRecord | null>(null);
  const [notes, setNotes] = useState<ClinicalNote[]>([]);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form toggles
  const [showAnamnesisForm, setShowAnamnesisForm] = useState(false);
  const [showNoteForm, setShowNoteForm] = useState(false);
  const [showPrescriptionForm, setShowPrescriptionForm] = useState(false);

  // Anamnesis form
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [medicalHistory, setMedicalHistory] = useState("");
  const [dentalHistory, setDentalHistory] = useState("");

  // Prescription form
  const [prescItems, setPrescItems] = useState([
    { medication_name: "", dosage: "", frequency: "", duration: "", instructions: "" },
  ]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [p, r, n, pr] = await Promise.all([
        fetchPatient(patientId),
        fetchPatientRecord(patientId).catch(() => null),
        fetchNotes(patientId).catch(() => []),
        fetchPrescriptions(patientId).catch(() => []),
      ]);
      setPatient(p);
      setRecord(r);
      setNotes(n);
      setPrescriptions(pr);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao carregar");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [patientId]);

  async function handleCreateAnamnesis() {
    try {
      await createAnamnesis(patientId, {
        chief_complaint: chiefComplaint,
        medical_history: { text: medicalHistory },
        dental_history: { text: dentalHistory },
      });
      setShowAnamnesisForm(false);
      load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erro");
    }
  }

  async function handleCreateNote(data: { note_type: string; content: string; tooth_references: number[] }) {
    await createNote(patientId, data);
    setShowNoteForm(false);
    load();
  }

  async function handleCreatePrescription() {
    const validItems = prescItems.filter((i) => i.medication_name.trim());
    if (validItems.length === 0) return;
    try {
      await createPrescription(patientId, { items: validItems });
      setShowPrescriptionForm(false);
      setPrescItems([{ medication_name: "", dosage: "", frequency: "", duration: "", instructions: "" }]);
      load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erro");
    }
  }

  if (loading) {
    return (
      <div className="p-6 lg:p-8 space-y-4">
        <div className="h-8 bg-gray-200 rounded w-64 animate-pulse" />
        <div className="h-48 bg-gray-200 rounded animate-pulse" />
        <div className="h-48 bg-gray-200 rounded animate-pulse" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 lg:p-8">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
          {error}
          <button onClick={load} className="ml-4 underline">Tentar novamente</button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link href={`/pacientes/${patientId}`} className="text-sm text-teal-600 hover:underline">
            ← Voltar para {patient?.full_name || "paciente"}
          </Link>
          <h1 className="text-2xl font-bold mt-1">Prontuario Clinico</h1>
        </div>
        <Link
          href={`/pacientes/${patientId}/odontograma`}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
        >
          Odontograma
        </Link>
      </div>

      {/* Anamnesis */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-5 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Anamnese</h2>
          {!record?.anamnesis && !showAnamnesisForm && (
            <button onClick={() => setShowAnamnesisForm(true)} className="text-sm text-teal-600 hover:underline">
              Criar Anamnese
            </button>
          )}
        </div>
        <div className="p-5">
          {record?.anamnesis ? (
            <div className="space-y-3">
              <div>
                <span className="text-sm font-medium text-gray-500">Queixa principal:</span>
                <p className="mt-1">{record.anamnesis.chief_complaint || "—"}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Historico medico:</span>
                <p className="mt-1 text-sm text-gray-700">
                  {typeof record.anamnesis.medical_history === "object"
                    ? JSON.stringify(record.anamnesis.medical_history)
                    : String(record.anamnesis.medical_history) || "—"}
                </p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Historico dental:</span>
                <p className="mt-1 text-sm text-gray-700">
                  {typeof record.anamnesis.dental_history === "object"
                    ? JSON.stringify(record.anamnesis.dental_history)
                    : String(record.anamnesis.dental_history) || "—"}
                </p>
              </div>
              {record.anamnesis.signed_at && (
                <p className="text-xs text-green-600">Assinado em {new Date(record.anamnesis.signed_at).toLocaleString("pt-BR")}</p>
              )}
            </div>
          ) : showAnamnesisForm ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Queixa principal</label>
                <textarea value={chiefComplaint} onChange={(e) => setChiefComplaint(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" rows={2} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Historico medico</label>
                <textarea value={medicalHistory} onChange={(e) => setMedicalHistory(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" rows={3} placeholder="Doencas, alergias, medicamentos em uso..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Historico dental</label>
                <textarea value={dentalHistory} onChange={(e) => setDentalHistory(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" rows={3} placeholder="Tratamentos anteriores, queixas recorrentes..." />
              </div>
              <div className="flex gap-2">
                <button onClick={handleCreateAnamnesis} className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700">Salvar Anamnese</button>
                <button onClick={() => setShowAnamnesisForm(false)} className="border px-4 py-2 rounded-lg text-sm">Cancelar</button>
              </div>
            </div>
          ) : (
            <p className="text-gray-400 text-sm">Nenhuma anamnese registrada</p>
          )}
        </div>
      </div>

      {/* Clinical Notes */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-5 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Notas Clinicas</h2>
          <button
            onClick={() => setShowNoteForm(!showNoteForm)}
            className="bg-teal-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-teal-700"
          >
            {showNoteForm ? "Cancelar" : "Nova Nota"}
          </button>
        </div>
        <div className="p-5 space-y-4">
          {showNoteForm && (
            <ClinicalNoteForm onSubmit={handleCreateNote} onCancel={() => setShowNoteForm(false)} loading={false} />
          )}
          {notes.length > 0 ? (
            notes.map((note) => (
              <TimelineEntry
                key={note.id}
                entry={{
                  id: note.id,
                  event_type: "note",
                  summary: note.content,
                  provider_name: null,
                  occurred_at: note.created_at,
                  metadata: {
                    note_type: note.note_type,
                    tooth_references: note.tooth_references,
                    signed: !!note.signed_at,
                  },
                }}
              />
            ))
          ) : (
            <p className="text-gray-400 text-sm text-center py-4">Nenhuma nota clinica</p>
          )}
        </div>
      </div>

      {/* Prescriptions */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-5 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Prescricoes</h2>
          <button
            onClick={() => setShowPrescriptionForm(!showPrescriptionForm)}
            className="bg-teal-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-teal-700"
          >
            {showPrescriptionForm ? "Cancelar" : "Nova Prescricao"}
          </button>
        </div>
        <div className="p-5 space-y-4">
          {showPrescriptionForm && (
            <div className="border rounded-lg p-4 space-y-3">
              {prescItems.map((item, i) => (
                <div key={i} className="grid grid-cols-5 gap-2">
                  <input placeholder="Medicamento" value={item.medication_name} onChange={(e) => { const n = [...prescItems]; n[i] = { ...n[i], medication_name: e.target.value }; setPrescItems(n); }} className="border rounded px-2 py-1.5 text-sm" />
                  <input placeholder="Dosagem" value={item.dosage} onChange={(e) => { const n = [...prescItems]; n[i] = { ...n[i], dosage: e.target.value }; setPrescItems(n); }} className="border rounded px-2 py-1.5 text-sm" />
                  <input placeholder="Frequencia" value={item.frequency} onChange={(e) => { const n = [...prescItems]; n[i] = { ...n[i], frequency: e.target.value }; setPrescItems(n); }} className="border rounded px-2 py-1.5 text-sm" />
                  <input placeholder="Duracao" value={item.duration} onChange={(e) => { const n = [...prescItems]; n[i] = { ...n[i], duration: e.target.value }; setPrescItems(n); }} className="border rounded px-2 py-1.5 text-sm" />
                  <input placeholder="Instrucoes" value={item.instructions} onChange={(e) => { const n = [...prescItems]; n[i] = { ...n[i], instructions: e.target.value }; setPrescItems(n); }} className="border rounded px-2 py-1.5 text-sm" />
                </div>
              ))}
              <div className="flex gap-2">
                <button
                  onClick={() => setPrescItems([...prescItems, { medication_name: "", dosage: "", frequency: "", duration: "", instructions: "" }])}
                  className="text-sm text-teal-600 hover:underline"
                >
                  + Adicionar item
                </button>
              </div>
              <div className="flex gap-2">
                <button onClick={handleCreatePrescription} className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-teal-700">Salvar Prescricao</button>
                <button onClick={() => setShowPrescriptionForm(false)} className="border px-4 py-2 rounded-lg text-sm">Cancelar</button>
              </div>
            </div>
          )}
          {prescriptions.length > 0 ? (
            prescriptions.map((presc) => (
              <div key={presc.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Prescricao</span>
                  <span className="text-xs text-gray-500">{new Date(presc.created_at).toLocaleString("pt-BR")}</span>
                </div>
                <div className="space-y-1">
                  {presc.items.map((item, i) => (
                    <p key={i} className="text-sm">
                      <span className="font-medium">{item.medication_name}</span> — {item.dosage}, {item.frequency}, {item.duration}
                      {item.instructions && <span className="text-gray-500"> ({item.instructions})</span>}
                    </p>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-400 text-sm text-center py-4">Nenhuma prescricao</p>
          )}
        </div>
      </div>
    </div>
  );
}
