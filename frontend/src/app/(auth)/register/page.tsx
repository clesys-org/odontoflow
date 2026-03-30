"use client";

import { useState } from "react";
import Link from "next/link";

export default function RegisterPage() {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    clinic_name: "",
    clinic_slug: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (field === "clinic_name" && !form.clinic_slug) {
      const slug = value.toLowerCase().replace(/[^a-z0-9]/g, "-").replace(/-+/g, "-").slice(0, 30);
      setForm((prev) => ({ ...prev, clinic_slug: slug }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.detail || "Erro ao criar conta");
      }

      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      window.location.href = "/pacientes";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao registrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-dental-700">OdontoFlow</h1>
          <p className="text-gray-500 mt-1">Crie sua conta e cadastre sua clinica</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-8 space-y-5">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Seu nome completo</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => updateField("full_name", e.target.value)}
              className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-dental-500"
              placeholder="Dr. Joao Silva"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
              className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-dental-500"
              placeholder="seu@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => updateField("password", e.target.value)}
              className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-dental-500"
              placeholder="Minimo 8 caracteres"
              minLength={8}
              required
            />
          </div>

          <hr className="border-gray-200" />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome da clinica</label>
            <input
              type="text"
              value={form.clinic_name}
              onChange={(e) => updateField("clinic_name", e.target.value)}
              className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-dental-500"
              placeholder="Clinica Sorriso"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Identificador (slug)
            </label>
            <div className="flex items-center">
              <span className="text-sm text-gray-400 mr-1">odontoflow.com.br/</span>
              <input
                type="text"
                value={form.clinic_slug}
                onChange={(e) => updateField("clinic_slug", e.target.value)}
                className="flex-1 border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-dental-500"
                placeholder="clinica-sorriso"
                pattern="[a-z0-9-]+"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-dental-600 text-white py-2.5 rounded-lg font-medium hover:bg-dental-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Criando conta..." : "Criar Conta Gratis"}
          </button>

          <p className="text-center text-sm text-gray-500">
            Ja tem conta?{" "}
            <Link href="/login" className="text-dental-600 hover:underline">
              Fazer login
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
