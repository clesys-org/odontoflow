"use client";

import { useCallback, useState } from "react";
import { useApi } from "@/hooks/useApi";
import {
  fetchMaterials,
  fetchSuppliers,
  createMaterial,
  createSupplier,
  recordStockMovement,
} from "@/lib/api/inventory";
import type { MovementType } from "@/lib/types/inventory";

function formatBRL(centavos: number): string {
  return (centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

type Tab = "materiais" | "fornecedores" | "novo-material" | "novo-fornecedor";

export default function EstoquePage() {
  const [tab, setTab] = useState<Tab>("materiais");
  const [lowStockOnly, setLowStockOnly] = useState(false);

  const materialsFetcher = useCallback(
    () => fetchMaterials({ low_stock_only: lowStockOnly }),
    [lowStockOnly]
  );
  const {
    data: materialsData,
    loading: materialsLoading,
    error: materialsError,
    refetch: materialsRefetch,
  } = useApi(materialsFetcher, [lowStockOnly]);

  const suppliersFetcher = useCallback(() => fetchSuppliers(), []);
  const {
    data: suppliersData,
    loading: suppliersLoading,
    refetch: suppliersRefetch,
  } = useApi(suppliersFetcher, []);

  // Material form
  const [materialForm, setMaterialForm] = useState({
    name: "",
    description: "",
    category: "",
    unit: "un",
    current_stock: "",
    min_stock: "",
    cost_centavos: "",
    supplier_id: "",
  });

  // Supplier form
  const [supplierForm, setSupplierForm] = useState({
    name: "",
    cnpj: "",
    phone: "",
    email: "",
  });

  // Movement modal
  const [movementModal, setMovementModal] = useState<{
    materialId: string;
    materialName: string;
  } | null>(null);
  const [movementForm, setMovementForm] = useState({
    movement_type: "ENTRADA" as MovementType,
    quantity: "",
    reason: "",
  });

  const [submitting, setSubmitting] = useState(false);

  async function handleCreateMaterial(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createMaterial({
        name: materialForm.name,
        description: materialForm.description || undefined,
        category: materialForm.category || undefined,
        unit: materialForm.unit,
        current_stock: Number(materialForm.current_stock),
        min_stock: Number(materialForm.min_stock),
        cost_centavos: Number(materialForm.cost_centavos),
        supplier_id: materialForm.supplier_id || undefined,
      });
      setMaterialForm({
        name: "",
        description: "",
        category: "",
        unit: "un",
        current_stock: "",
        min_stock: "",
        cost_centavos: "",
        supplier_id: "",
      });
      setTab("materiais");
      materialsRefetch();
    } catch {
      /* handled */
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateSupplier(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createSupplier({
        name: supplierForm.name,
        cnpj: supplierForm.cnpj || undefined,
        phone: supplierForm.phone || undefined,
        email: supplierForm.email || undefined,
      });
      setSupplierForm({ name: "", cnpj: "", phone: "", email: "" });
      setTab("fornecedores");
      suppliersRefetch();
    } catch {
      /* handled */
    } finally {
      setSubmitting(false);
    }
  }

  async function handleMovement(e: React.FormEvent) {
    e.preventDefault();
    if (!movementModal) return;
    setSubmitting(true);
    try {
      await recordStockMovement(movementModal.materialId, {
        movement_type: movementForm.movement_type,
        quantity: Number(movementForm.quantity),
        reason: movementForm.reason || undefined,
      });
      setMovementModal(null);
      setMovementForm({ movement_type: "ENTRADA", quantity: "", reason: "" });
      materialsRefetch();
    } catch {
      /* handled */
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Estoque</h1>
          <p className="text-sm text-gray-500">Controle de materiais e fornecedores</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setTab("novo-material")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Novo Material
          </button>
          <button
            onClick={() => setTab("novo-fornecedor")}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Novo Fornecedor
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-6">
          {[
            { key: "materiais" as Tab, label: "Materiais" },
            { key: "fornecedores" as Tab, label: "Fornecedores" },
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
      {materialsError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {materialsError}
          <button onClick={materialsRefetch} className="ml-2 underline">
            Tentar novamente
          </button>
        </div>
      )}

      {/* Materials List */}
      {tab === "materiais" && (
        <>
          <div className="flex gap-3 items-center">
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={lowStockOnly}
                onChange={(e) => setLowStockOnly(e.target.checked)}
                className="rounded border-gray-300 text-teal-600"
              />
              Apenas estoque baixo
            </label>
          </div>

          {materialsLoading && !materialsData && (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border p-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-40 mb-2" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-24" />
                </div>
              ))}
            </div>
          )}

          {materialsData && (
            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left px-4 py-3 font-medium text-gray-600">Material</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Categoria</th>
                      <th className="text-center px-4 py-3 font-medium text-gray-600">Estoque</th>
                      <th className="text-center px-4 py-3 font-medium text-gray-600">Min.</th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Custo Unit.</th>
                      <th className="text-center px-4 py-3 font-medium text-gray-600">Acoes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {materialsData.materials.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                          Nenhum material cadastrado
                        </td>
                      </tr>
                    )}
                    {materialsData.materials.map((mat) => (
                      <tr key={mat.id} className="border-b hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-medium text-gray-900">{mat.name}</div>
                          {mat.description && (
                            <div className="text-xs text-gray-500">{mat.description}</div>
                          )}
                        </td>
                        <td className="px-4 py-3 text-gray-600 hidden md:table-cell">
                          {mat.category || "—"}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span
                            className={`font-semibold ${
                              mat.is_low_stock ? "text-red-600" : "text-gray-900"
                            }`}
                          >
                            {mat.current_stock}
                          </span>
                          <span className="text-gray-400 text-xs ml-1">{mat.unit}</span>
                        </td>
                        <td className="px-4 py-3 text-center text-gray-500">{mat.min_stock}</td>
                        <td className="px-4 py-3 text-right text-gray-600 hidden md:table-cell">
                          {formatBRL(mat.cost_centavos)}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="flex gap-1 justify-center">
                            {(["ENTRADA", "SAIDA", "AJUSTE"] as MovementType[]).map((type) => (
                              <button
                                key={type}
                                onClick={() =>
                                  setMovementModal({
                                    materialId: mat.id,
                                    materialName: mat.name,
                                  })
                                }
                                className={`px-2 py-1 text-xs rounded font-medium transition-colors ${
                                  type === "ENTRADA"
                                    ? "bg-green-100 text-green-700 hover:bg-green-200"
                                    : type === "SAIDA"
                                    ? "bg-red-100 text-red-700 hover:bg-red-200"
                                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                                }`}
                              >
                                {type === "ENTRADA"
                                  ? "Entrada"
                                  : type === "SAIDA"
                                  ? "Saida"
                                  : "Ajuste"}
                              </button>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Suppliers List */}
      {tab === "fornecedores" && (
        <>
          {suppliersLoading && !suppliersData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border p-5">
                  <div className="h-5 bg-gray-200 rounded animate-pulse w-36 mb-3" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-24" />
                </div>
              ))}
            </div>
          )}

          {suppliersData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {suppliersData.suppliers.length === 0 && (
                <div className="col-span-full text-center py-12 text-gray-400">
                  Nenhum fornecedor cadastrado
                </div>
              )}
              {suppliersData.suppliers.map((sup) => (
                <div key={sup.id} className="bg-white rounded-xl shadow-sm border p-5">
                  <h3 className="font-semibold text-gray-900 mb-2">{sup.name}</h3>
                  {sup.cnpj && <p className="text-sm text-gray-500">CNPJ: {sup.cnpj}</p>}
                  {sup.phone && <p className="text-sm text-gray-500">Tel: {sup.phone}</p>}
                  {sup.email && <p className="text-sm text-gray-500">{sup.email}</p>}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* New Material Form */}
      {tab === "novo-material" && (
        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Novo Material</h2>
          <form onSubmit={handleCreateMaterial} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                <input
                  type="text"
                  value={materialForm.name}
                  onChange={(e) => setMaterialForm({ ...materialForm, name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                <input
                  type="text"
                  value={materialForm.category}
                  onChange={(e) => setMaterialForm({ ...materialForm, category: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descricao</label>
              <input
                type="text"
                value={materialForm.description}
                onChange={(e) => setMaterialForm({ ...materialForm, description: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Unidade</label>
                <select
                  value={materialForm.unit}
                  onChange={(e) => setMaterialForm({ ...materialForm, unit: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="un">Unidade</option>
                  <option value="cx">Caixa</option>
                  <option value="pct">Pacote</option>
                  <option value="ml">mL</option>
                  <option value="g">g</option>
                  <option value="par">Par</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Estoque Atual</label>
                <input
                  type="number"
                  value={materialForm.current_stock}
                  onChange={(e) => setMaterialForm({ ...materialForm, current_stock: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  min={0}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Estoque Min.</label>
                <input
                  type="number"
                  value={materialForm.min_stock}
                  onChange={(e) => setMaterialForm({ ...materialForm, min_stock: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  min={0}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Custo (centavos)</label>
                <input
                  type="number"
                  value={materialForm.cost_centavos}
                  onChange={(e) => setMaterialForm({ ...materialForm, cost_centavos: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  min={0}
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fornecedor</label>
              <select
                value={materialForm.supplier_id}
                onChange={(e) => setMaterialForm({ ...materialForm, supplier_id: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                <option value="">Nenhum</option>
                {suppliersData?.suppliers.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {submitting ? "Salvando..." : "Cadastrar Material"}
              </button>
              <button
                type="button"
                onClick={() => setTab("materiais")}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* New Supplier Form */}
      {tab === "novo-fornecedor" && (
        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Novo Fornecedor</h2>
          <form onSubmit={handleCreateSupplier} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                <input
                  type="text"
                  value={supplierForm.name}
                  onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">CNPJ</label>
                <input
                  type="text"
                  value={supplierForm.cnpj}
                  onChange={(e) => setSupplierForm({ ...supplierForm, cnpj: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
                <input
                  type="text"
                  value={supplierForm.phone}
                  onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
                <input
                  type="email"
                  value={supplierForm.email}
                  onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })}
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
                {submitting ? "Salvando..." : "Cadastrar Fornecedor"}
              </button>
              <button
                type="button"
                onClick={() => setTab("fornecedores")}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Stock Movement Modal */}
      {movementModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-semibold mb-1">Movimentacao de Estoque</h2>
            <p className="text-sm text-gray-500 mb-4">{movementModal.materialName}</p>
            <form onSubmit={handleMovement} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                <select
                  value={movementForm.movement_type}
                  onChange={(e) =>
                    setMovementForm({
                      ...movementForm,
                      movement_type: e.target.value as MovementType,
                    })
                  }
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="ENTRADA">Entrada</option>
                  <option value="SAIDA">Saida</option>
                  <option value="AJUSTE">Ajuste</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantidade</label>
                <input
                  type="number"
                  value={movementForm.quantity}
                  onChange={(e) => setMovementForm({ ...movementForm, quantity: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  min={1}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
                <input
                  type="text"
                  value={movementForm.reason}
                  onChange={(e) => setMovementForm({ ...movementForm, reason: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
                >
                  {submitting ? "Registrando..." : "Registrar"}
                </button>
                <button
                  type="button"
                  onClick={() => setMovementModal(null)}
                  className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
