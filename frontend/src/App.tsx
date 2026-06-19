import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { DashboardView } from './views/DashboardView';
import { QuizView } from './views/QuizView';
import { QuizResultView } from './views/QuizResultView';
import { checkQuizCompleted } from './lib/session';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RootRedirect />} />
        <Route path="/quiz" element={<QuizView />} />
        <Route path="/quiz/result" element={<QuizResultView />} />
        <Route path="/chat" element={<DashboardView />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

/**
 * Componente de redirección en la raíz.
 * Si el usuario ya completó el quiz → /chat
 * Si no → /quiz
 */
function RootRedirect() {
  const [target, setTarget] = useState<string | null>(null);

  useEffect(() => {
    checkQuizCompleted().then((result) => {
      setTarget(result ? '/chat' : '/quiz');
    });
  }, []);

  if (!target) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    );
  }

  return <Navigate to={target} replace />;
}

export default App
