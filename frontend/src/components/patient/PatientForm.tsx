"use client";

import { useState, useEffect, useCallback } from "react";
import type { Patient } from "@/lib/types/patient";
import { fetchAddressFromCEP } from "@/lib/api/patient";
import { formatCPF, formatPhone, formatCEP } from "@/lib/utils/format";
import { isValidCPF, isValidEmail, isValidPhone } from "@/lib/utils/validators";

interface PatientFormProps {
  initialData?: Partial<Patient>;
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  loading: boolean;
}

const GENDER_OPTIONS = [
  { value: "", label: "Selecione" },
  { value: "M", label: "Masculino" },
  { value: "F", label: "Feminino" },
  { value: "O", label: "Outro" },
  { value: "N", label: "Prefiro nao informar" },
];

const MARITAL_OPTIONS = [
  { value: "", label: "Selecione" },
  { value: "solteiro", label: "Solteiro(a)" },
  { value: "casado", label: "Casado(a)" },
  { value: "divorciado", label: "Divorciado(a)" },
  { value: "viuvo", label: "Viuvo(a)" },
  { value: "uniao_estavel", label: "Uniao estavel" },
];

const CHANNEL_OPTIONS = [
  { value: "whatsapp", label: "WhatsApp" },
  { value: "phone", label: "Telefone" },
  { value: "email", label: "Email" },
  { value: "sms", label: "SMS" },
];

const REFERRAL_OPTIONS = [
  { value: "", label: "Selecione" },
  { value: "indicacao", label: "Indicacao de paciente" },
  { value: "google", label: "Google" },
  { value: "instagram", label: "Instagram" },
  { value: "facebook", label: "Facebook" },
  { value: "convenio", label: "Convenio" },
  { value: "outro", label: "Outro" },
];

const STATES = [
  "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
  "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO",
];

function isMinor(birthDate: string): boolean {
  if (!birthDate) return false;
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age < 18;
}

function maskCPF(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

function maskPhone(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 2) return digits;
  if (digits.length <= 7) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
}

function maskCEP(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 5) return digits;
  return `${digits.slice(0, 5)}-${digits.slice(5)}`;
}

export default function PatientForm({ initialData, onSubmit, loading }: PatientFormProps) {
  // Personal data
  const [fullName, setFullName] = useState(initialData?.full_name || "");
  const [cpf, setCpf] = useState(initialData?.cpf_formatted || initialData?.cpf || "");
  const [birthDate, setBirthDate] = useState(initialData?.birth_date || "");
  const [gender, setGender] = useState(initialData?.gender || "");
  const [maritalStatus, setMaritalStatus] = useState(initialData?.marital_status || "");
  const [profession, setProfession] = useState(initialData?.profession || "");

  // Contact
  const [phone, setPhone] = useState(initialData?.phone_formatted || initialData?.phone || "");
  const [whatsapp, setWhatsapp] = useState(initialData?.whatsapp || "");
  const [email, setEmail] = useState(initialData?.email || "");
  const [preferredChannel, setPreferredChannel] = useState(initialData?.preferred_channel || "whatsapp");

  // Address
  const [zipCode, setZipCode] = useState(initialData?.address?.zip_code || "");
  const [street, setStreet] = useState(initialData?.address?.street || "");
  const [number, setNumber] = useState(initialData?.address?.number || "");
  const [complement, setComplement] = useState(initialData?.address?.complement || "");
  const [neighborhood, setNeighborhood] = useState(initialData?.address?.neighborhood || "");
  const [city, setCity] = useState(initialData?.address?.city || "");
  const [state, setState] = useState(initialData?.address?.state || "");
  const [cepLoading, setCepLoading] = useState(false);

  // Responsible (minor)
  const [respName, setRespName] = useState(initialData?.responsible?.name || "");
  const [respCpf, setRespCpf] = useState(initialData?.responsible?.cpf || "");
  const [respRelationship, setRespRelationship] = useState(initialData?.responsible?.relationship || "");
  const [respPhone, setRespPhone] = useState(initialData?.responsible?.phone || "");

  // Insurance
  const [hasInsurance, setHasInsurance] = useState(!!initialData?.insurance_info);
  const [insProvider, setInsProvider] = useState(initialData?.insurance_info?.provider_name || "");
  const [insPlan, setInsPlan] = useState(initialData?.insurance_info?.plan_name || "");
  const [insCard, setInsCard] = useState(initialData?.insurance_info?.card_number || "");
  const [insValidUntil, setInsValidUntil] = useState(initialData?.insurance_info?.valid_until || "");

  // Notes
  const [referralSource, setReferralSource] = useState(initialData?.referral_source || "");
  const [tagsInput, setTagsInput] = useState((initialData?.tags || []).join(", "));
  const [notes, setNotes] = useState(initialData?.notes || "");

  // LGPD
  const [lgpdConsent, setLgpdConsent] = useState(!!initialData?.id);

  // Validation
  const [errors, setErrors] = useState<Record<string, string>>({});

  const showMinor = isMinor(birthDate);

  // CEP auto-fill
  const handleCepChange = useCallback(async (value: string) => {
    const masked = maskCEP(value);
    setZipCode(masked);
    const digits = value.replace(/\D/g, "");
    if (digits.length === 8) {
      setCepLoading(true);
      const addr = await fetchAddressFromCEP(digits);
      setCepLoading(false);
      if (addr) {
        setStreet(addr.street);
        setNeighborhood(addr.neighborhood);
        setCity(addr.city);
        setState(addr.state);
      }
    }
  }, []);

  function validate(): boolean {
    const errs: Record<string, string> = {};
    if (!fullName.trim()) errs.fullName = "Nome e obrigatorio";
    if (cpf && !isValidCPF(cpf)) errs.cpf = "CPF invalido";
    if (email && !isValidEmail(email)) errs.email = "Email invalido";
    if (phone && !isValidPhone(phone)) errs.phone = "Telefone invalido";
    if (!lgpdConsent) errs.lgpd = "Consentimento LGPD e obrigatorio";
    if (showMinor && !respName.trim()) errs.respName = "Nome do responsavel e obrigatorio";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;

    const data: Record<string, unknown> = {
      full_name: fullName.trim(),
      cpf: cpf.replace(/\D/g, "") || null,
      birth_date: birthDate || null,
      gender: gender || null,
      marital_status: maritalStatus || null,
      profession: profession.trim() || null,
      phone: phone.replace(/\D/g, "") || null,
      whatsapp: whatsapp.replace(/\D/g, "") || null,
      email: email.trim() || null,
      preferred_channel: preferredChannel,
      referral_source: referralSource || null,
      tags: tagsInput.split(",").map((t) => t.trim()).filter(Boolean),
      notes: notes.trim() || null,
    };

    // Address
    if (street || number || city) {
      data.address = {
        street: street.trim(),
        number: number.trim(),
        complement: complement.trim(),
        neighborhood: neighborhood.trim(),
        city: city.trim(),
        state: state.trim(),
        zip_code: zipCode.replace(/\D/g, ""),
      };
    }

    // Responsible
    if (showMinor && respName) {
      data.responsible = {
        name: respName.trim(),
        cpf: respCpf.replace(/\D/g, ""),
        relationship: respRelationship.trim(),
        phone: respPhone.replace(/\D/g, ""),
      };
    }

    // Insurance
    if (hasInsurance && insProvider) {
      data.insurance_info = {
        provider_name: insProvider.trim(),
        plan_name: insPlan.trim(),
        card_number: insCard.trim(),
        valid_until: insValidUntil || null,
      };
    }

    await onSubmit(data);
  }

  const inputClass =
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";
  const errorClass = "text-xs text-red-600 mt-1";

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Dados Pessoais */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Dados Pessoais</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="md:col-span-2 lg:col-span-3">
            <label className={labelClass}>
              Nome completo <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className={inputClass}
              placeholder="Nome completo do paciente"
            />
            {errors.fullName && <p className={errorClass}>{errors.fullName}</p>}
          </div>

          <div>
            <label className={labelClass}>CPF</label>
            <input
              type="text"
              value={cpf}
              onChange={(e) => setCpf(maskCPF(e.target.value))}
              className={inputClass}
              placeholder="000.000.000-00"
              maxLength={14}
            />
            {errors.cpf && <p className={errorClass}>{errors.cpf}</p>}
          </div>

          <div>
            <label className={labelClass}>Data de nascimento</label>
            <input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              className={inputClass}
            />
          </div>

          <div>
            <label className={labelClass}>Genero</label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className={inputClass}
            >
              {GENDER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className={labelClass}>Estado civil</label>
            <select
              value={maritalStatus}
              onChange={(e) => setMaritalStatus(e.target.value)}
              className={inputClass}
            >
              {MARITAL_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className={labelClass}>Profissao</label>
            <input
              type="text"
              value={profession}
              onChange={(e) => setProfession(e.target.value)}
              className={inputClass}
              placeholder="Ex: Engenheiro"
            />
          </div>
        </div>
      </section>

      {/* Contato */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Contato</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Telefone</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(maskPhone(e.target.value))}
              className={inputClass}
              placeholder="(11) 99999-9999"
              maxLength={15}
            />
            {errors.phone && <p className={errorClass}>{errors.phone}</p>}
          </div>

          <div>
            <label className={labelClass}>WhatsApp</label>
            <input
              type="text"
              value={whatsapp}
              onChange={(e) => setWhatsapp(maskPhone(e.target.value))}
              className={inputClass}
              placeholder="(11) 99999-9999"
              maxLength={15}
            />
          </div>

          <div>
            <label className={labelClass}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputClass}
              placeholder="paciente@email.com"
            />
            {errors.email && <p className={errorClass}>{errors.email}</p>}
          </div>

          <div>
            <label className={labelClass}>Canal preferido</label>
            <select
              value={preferredChannel}
              onChange={(e) => setPreferredChannel(e.target.value)}
              className={inputClass}
            >
              {CHANNEL_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {/* Endereco */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Endereco</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className={labelClass}>CEP</label>
            <div className="relative">
              <input
                type="text"
                value={zipCode}
                onChange={(e) => handleCepChange(e.target.value)}
                className={inputClass}
                placeholder="00000-000"
                maxLength={9}
              />
              {cepLoading && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <div className="w-4 h-4 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-2">
            <label className={labelClass}>Rua</label>
            <input
              type="text"
              value={street}
              onChange={(e) => setStreet(e.target.value)}
              className={inputClass}
              placeholder="Rua, Avenida..."
            />
          </div>

          <div>
            <label className={labelClass}>Numero</label>
            <input
              type="text"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              className={inputClass}
              placeholder="123"
            />
          </div>

          <div>
            <label className={labelClass}>Complemento</label>
            <input
              type="text"
              value={complement}
              onChange={(e) => setComplement(e.target.value)}
              className={inputClass}
              placeholder="Apto, Sala..."
            />
          </div>

          <div>
            <label className={labelClass}>Bairro</label>
            <input
              type="text"
              value={neighborhood}
              onChange={(e) => setNeighborhood(e.target.value)}
              className={inputClass}
            />
          </div>

          <div>
            <label className={labelClass}>Cidade</label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className={inputClass}
            />
          </div>

          <div>
            <label className={labelClass}>Estado</label>
            <select
              value={state}
              onChange={(e) => setState(e.target.value)}
              className={inputClass}
            >
              <option value="">UF</option>
              {STATES.map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {/* Responsavel (menor de idade) */}
      {showMinor && (
        <section className="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-amber-500">
          <h2 className="text-lg font-semibold mb-1">Responsavel Legal</h2>
          <p className="text-sm text-amber-600 mb-4">
            Paciente menor de 18 anos — responsavel obrigatorio
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>
                Nome do responsavel <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={respName}
                onChange={(e) => setRespName(e.target.value)}
                className={inputClass}
              />
              {errors.respName && <p className={errorClass}>{errors.respName}</p>}
            </div>

            <div>
              <label className={labelClass}>CPF do responsavel</label>
              <input
                type="text"
                value={respCpf}
                onChange={(e) => setRespCpf(maskCPF(e.target.value))}
                className={inputClass}
                placeholder="000.000.000-00"
                maxLength={14}
              />
            </div>

            <div>
              <label className={labelClass}>Parentesco</label>
              <input
                type="text"
                value={respRelationship}
                onChange={(e) => setRespRelationship(e.target.value)}
                className={inputClass}
                placeholder="Mae, Pai, Tutor..."
              />
            </div>

            <div>
              <label className={labelClass}>Telefone do responsavel</label>
              <input
                type="text"
                value={respPhone}
                onChange={(e) => setRespPhone(maskPhone(e.target.value))}
                className={inputClass}
                placeholder="(11) 99999-9999"
                maxLength={15}
              />
            </div>
          </div>
        </section>
      )}

      {/* Convenio */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Convenio</h2>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={hasInsurance}
              onChange={(e) => setHasInsurance(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500"
            />
            Possui convenio
          </label>
        </div>
        {hasInsurance && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Operadora</label>
              <input
                type="text"
                value={insProvider}
                onChange={(e) => setInsProvider(e.target.value)}
                className={inputClass}
                placeholder="Ex: Amil, Bradesco Dental"
              />
            </div>

            <div>
              <label className={labelClass}>Plano</label>
              <input
                type="text"
                value={insPlan}
                onChange={(e) => setInsPlan(e.target.value)}
                className={inputClass}
                placeholder="Nome do plano"
              />
            </div>

            <div>
              <label className={labelClass}>Carteirinha</label>
              <input
                type="text"
                value={insCard}
                onChange={(e) => setInsCard(e.target.value)}
                className={inputClass}
                placeholder="Numero da carteirinha"
              />
            </div>

            <div>
              <label className={labelClass}>Validade</label>
              <input
                type="date"
                value={insValidUntil}
                onChange={(e) => setInsValidUntil(e.target.value)}
                className={inputClass}
              />
            </div>
          </div>
        )}
      </section>

      {/* Observacoes */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Observacoes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Como conheceu a clinica</label>
            <select
              value={referralSource}
              onChange={(e) => setReferralSource(e.target.value)}
              className={inputClass}
            >
              {REFERRAL_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className={labelClass}>Tags</label>
            <input
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              className={inputClass}
              placeholder="ortodontia, implante (separar por virgula)"
            />
          </div>

          <div className="md:col-span-2">
            <label className={labelClass}>Observacoes gerais</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className={`${inputClass} resize-none`}
              rows={3}
              placeholder="Alergias, condicoes especiais, preferencias..."
            />
          </div>
        </div>
      </section>

      {/* LGPD */}
      <section className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Consentimento LGPD</h2>
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={lgpdConsent}
            onChange={(e) => setLgpdConsent(e.target.checked)}
            className="w-4 h-4 mt-0.5 rounded border-gray-300 text-teal-600 focus:ring-teal-500"
          />
          <span className="text-sm text-gray-600">
            O paciente autoriza a coleta e o tratamento de seus dados pessoais e
            de saude conforme a Lei Geral de Protecao de Dados (LGPD), para fins
            de atendimento odontologico, prontuario clinico e comunicacao sobre
            tratamentos. <span className="text-red-500">*</span>
          </span>
        </label>
        {errors.lgpd && <p className={`${errorClass} ml-7`}>{errors.lgpd}</p>}
      </section>

      {/* Submit */}
      <div className="flex justify-end gap-3">
        <a
          href="/pacientes"
          className="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </a>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Salvando..." : initialData?.id ? "Atualizar" : "Cadastrar paciente"}
        </button>
      </div>
    </form>
  );
}
