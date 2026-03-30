import Link from "next/link";

const FEATURES = [
  {
    title: "Agenda Inteligente",
    desc: "Agendamento com deteccao de conflitos, slots disponiveis e lembretes automaticos por WhatsApp.",
    icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
  },
  {
    title: "Prontuario Digital",
    desc: "Anamnese, notas clinicas, prescricoes e odontograma interativo. Compliance CFO e LGPD.",
    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  },
  {
    title: "Odontograma SVG",
    desc: "32 dentes interativos com 5 faces por dente. Clique, edite condicoes e salve em tempo real.",
    icon: "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
  },
  {
    title: "Financeiro Completo",
    desc: "Planos de tratamento, faturamento, parcelas, Pix e dashboard de receita em tempo real.",
    icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  {
    title: "Convenios TISS",
    desc: "Guias GTO, autorizacao, faturamento em lote e gestao de glosas. Padrao ANS.",
    icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
  },
  {
    title: "Comunicacao",
    desc: "WhatsApp, SMS e email automaticos. Templates personalizaveis e campanhas em massa.",
    icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
  },
];

const STATS = [
  { value: "12", label: "Modulos integrados" },
  { value: "81", label: "Endpoints API" },
  { value: "294", label: "Testes automatizados" },
  { value: "100%", label: "LGPD Compliance" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-dental-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">OdontoFlow</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900 font-medium">
              Entrar
            </Link>
            <Link
              href="/register"
              className="bg-dental-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-dental-700 transition-colors"
            >
              Criar Conta Gratis
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-dental-50 text-dental-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            <span className="w-2 h-2 bg-dental-500 rounded-full animate-pulse" />
            Sistema completo para clinicas odontologicas
          </div>
          <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
            Gestao odontologica{" "}
            <span className="text-dental-600">integrada</span> e{" "}
            <span className="text-dental-600">inteligente</span>
          </h1>
          <p className="text-lg lg:text-xl text-gray-500 mt-6 max-w-2xl mx-auto">
            Do agendamento ao financeiro, do prontuario ao convenio. Tudo em um unico sistema
            com odontograma interativo, TISS integrado e comunicacao automatizada.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mt-10">
            <Link
              href="/register"
              className="bg-dental-600 text-white px-8 py-3.5 rounded-xl text-lg font-semibold hover:bg-dental-700 transition-colors shadow-lg shadow-dental-600/25"
            >
              Comecar Gratis
            </Link>
            <Link
              href="#features"
              className="border-2 border-gray-200 text-gray-700 px-8 py-3.5 rounded-xl text-lg font-semibold hover:border-dental-300 hover:text-dental-700 transition-colors"
            >
              Conhecer Recursos
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-dental-600 py-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {STATS.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-3xl lg:text-4xl font-bold text-white">{stat.value}</p>
                <p className="text-dental-200 text-sm mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900">
            Tudo que sua clinica precisa
          </h2>
          <p className="text-gray-500 mt-4 max-w-xl mx-auto">
            12 modulos integrados cobrindo todas as areas da gestao odontologica
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {FEATURES.map((feat) => (
            <div
              key={feat.title}
              className="border rounded-2xl p-6 hover:shadow-lg hover:border-dental-200 transition-all group"
            >
              <div className="w-12 h-12 bg-dental-50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-dental-100 transition-colors">
                <svg className="w-6 h-6 text-dental-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={feat.icon} />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{feat.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{feat.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            Pronto para modernizar sua clinica?
          </h2>
          <p className="text-gray-500 mt-4">
            Crie sua conta em 30 segundos. Sem cartao de credito. Sem compromisso.
          </p>
          <Link
            href="/register"
            className="inline-block bg-dental-600 text-white px-10 py-4 rounded-xl text-lg font-semibold hover:bg-dental-700 transition-colors shadow-lg shadow-dental-600/25 mt-8"
          >
            Criar Conta Gratis
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-dental-600 rounded flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-gray-700">OdontoFlow</span>
          </div>
          <p className="text-xs text-gray-400">
            Sistema integrado de gestao odontologica. LGPD compliant. CFO 91/2009.
          </p>
        </div>
      </footer>
    </div>
  );
}
