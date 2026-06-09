function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-8">
      <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
        Ceryle
      </h1>
      <p className="text-gray-400 text-lg mb-8 text-center max-w-md">
        Plataforma de adopcion de IA Generativa con Memoria de Largo Plazo
      </p>
      <div className="flex gap-4">
        <button className="px-6 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg font-medium transition-colors">
          Modo Aula
        </button>
        <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors">
          Modo Co-creador
        </button>
      </div>
      <p className="mt-12 text-gray-600 text-sm">
        Backend: FastAPI + LangChain | Frontend: React + Tailwind
      </p>
    </div>
  )
}

export default App
