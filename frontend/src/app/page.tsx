import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center">
      <div className="text-center space-y-6">
        <h1 className="text-5xl font-bold text-dental-700">OdontoFlow</h1>
        <p className="text-xl text-gray-500">
          Sistema integrado de gestao odontologica
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="bg-dental-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-dental-700 transition-colors"
          >
            Entrar
          </Link>
          <Link
            href="/register"
            className="border-2 border-dental-600 text-dental-600 px-8 py-3 rounded-lg text-lg font-medium hover:bg-dental-50 transition-colors"
          >
            Criar Conta
          </Link>
        </div>
      </div>
    </main>
  );
}
