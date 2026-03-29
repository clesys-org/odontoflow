"use client";

function MetricCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color || "text-gray-900"}`}>{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="p-6 lg:p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-gray-500">Visao geral da clinica</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Pacientes ativos" value="—" />
        <MetricCard label="Consultas hoje" value="—" />
        <MetricCard label="Faturamento mensal" value="—" />
        <MetricCard label="Taxa de comparecimento" value="—" />
      </div>

      {/* Agenda do dia */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Agenda de Hoje</h2>
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg mb-2">Nenhuma consulta agendada</p>
          <p className="text-sm">Configure seus horarios e comece a agendar pacientes</p>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Novo Paciente", href: "/pacientes/novo", color: "bg-teal-600" },
          { label: "Agendar Consulta", href: "/agenda", color: "bg-blue-600" },
          { label: "Financeiro", href: "/financeiro", color: "bg-green-600" },
          { label: "Relatorios", href: "/relatorios", color: "bg-purple-600" },
        ].map((action) => (
          <a
            key={action.label}
            href={action.href}
            className={`${action.color} text-white rounded-xl p-4 text-center font-medium hover:opacity-90 transition-opacity`}
          >
            {action.label}
          </a>
        ))}
      </div>
    </div>
  );
}
