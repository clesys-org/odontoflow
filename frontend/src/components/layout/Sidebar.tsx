"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const NAV = [
  { href: "/", label: "Dashboard", icon: "H" },
  { href: "/agenda", label: "Agenda", icon: "A" },
  { href: "/pacientes", label: "Pacientes", icon: "P" },
  { href: "/tratamentos", label: "Tratamentos", icon: "T" },
  { href: "/financeiro", label: "Financeiro", icon: "F" },
  { href: "/convenios", label: "Convenios", icon: "C" },
  { href: "/estoque", label: "Estoque", icon: "E" },
  { href: "/equipe", label: "Equipe", icon: "Q" },
  { href: "/comunicacao", label: "Comunicacao", icon: "M" },
  { href: "/relatorios", label: "Relatorios", icon: "R" },
  { href: "/configuracoes", label: "Config", icon: "G" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const navContent = (
    <>
      <div className="p-4 border-b border-teal-800">
        <h1 className="text-lg font-bold text-white">OdontoFlow</h1>
        <p className="text-xs text-teal-300 mt-0.5">Gestao Odontologica</p>
      </div>
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {NAV.map((item) => {
          const active = item.href === "/"
            ? pathname === "/"
            : pathname.startsWith(item.href);
          return (
            <Link
              key={item.label}
              href={item.href}
              onClick={() => setOpen(false)}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                active
                  ? "bg-teal-800 text-white font-medium"
                  : "text-teal-200 hover:bg-teal-800 hover:text-white"
              }`}
            >
              <span className="w-6 h-6 rounded bg-teal-800/50 flex items-center justify-center text-xs font-bold">
                {item.icon}
              </span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-teal-800 text-xs text-teal-400">
        v0.1.0
      </div>
    </>
  );

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setOpen(true)}
        className="md:hidden fixed top-3 left-3 z-50 bg-teal-700 text-white p-2 rounded-lg shadow-lg"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <rect y="3" width="20" height="2" rx="1" />
          <rect y="9" width="20" height="2" rx="1" />
          <rect y="15" width="20" height="2" rx="1" />
        </svg>
      </button>

      {/* Mobile drawer */}
      {open && (
        <div className="md:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <aside className="relative w-60 h-full bg-teal-900 text-teal-100 flex flex-col">
            {navContent}
          </aside>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-56 bg-teal-900 text-teal-100 flex-col min-h-screen shrink-0">
        {navContent}
      </aside>
    </>
  );
}
