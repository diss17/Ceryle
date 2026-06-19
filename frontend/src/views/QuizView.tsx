import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSessionId } from '../lib/session';

interface QuizQuestion {
  id: string;
  text: string;
  options: string[];
}

export function QuizView() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch questions on mount
  useEffect(() => {
    fetch('/api/quiz/questions')
      .then((res) => res.json())
      .then(setQuestions)
      .catch(() => setError('Failed to load questions. Is the backend running?'));
  }, []);

  const current = questions[currentIndex];
  const progress = questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0;
  const isLastQuestion = currentIndex === questions.length - 1;
  const hasAnswered = current ? answers[current.id] !== undefined : false;

  function handleSelect(optionIndex: number) {
    if (!current) return;
    setAnswers((prev) => ({ ...prev, [current.id]: optionIndex }));
  }

  function handleNext() {
    if (isLastQuestion) {
      handleSubmit();
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  }

  function handleBack() {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  }

  async function handleSubmit() {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: getSessionId(),
          answers,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Submit failed');
      }

      const result = await response.json();
      navigate('/quiz/result', { state: result });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setIsSubmitting(false);
    }
  }

  if (error && questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading quiz...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <h1 className="text-lg font-bold bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text text-transparent">
            Ceryle
          </h1>
          <span className="text-xs text-gray-500">
            {currentIndex + 1} / {questions.length}
          </span>
        </div>
      </header>

      {/* Progress bar */}
      <div className="w-full bg-gray-800 h-1">
        <div
          className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Question */}
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-2xl">
          <h2 className="text-xl font-medium text-white mb-8 leading-relaxed">
            {current.text}
          </h2>

          <div className="space-y-3">
            {current.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleSelect(index)}
                className={`w-full text-left px-5 py-4 rounded-xl border transition-all duration-200 ${
                  answers[current.id] === index
                    ? 'border-purple-500 bg-purple-500/10 text-white'
                    : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-500 hover:bg-gray-800'
                }`}
              >
                <span className="text-sm">{option}</span>
              </button>
            ))}
          </div>

          {error && (
            <p className="mt-4 text-sm text-red-400">{error}</p>
          )}
        </div>
      </main>

      {/* Navigation */}
      <footer className="border-t border-gray-800 px-6 py-4">
        <div className="max-w-2xl mx-auto flex justify-between">
          <button
            onClick={handleBack}
            disabled={currentIndex === 0}
            className="px-5 py-2.5 text-sm text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            ← Back
          </button>
          <button
            onClick={handleNext}
            disabled={!hasAnswered || isSubmitting}
            className="px-6 py-2.5 text-sm font-medium bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg disabled:opacity-40 disabled:cursor-not-allowed hover:from-purple-500 hover:to-indigo-500 transition-all"
          >
            {isSubmitting ? 'Submitting...' : isLastQuestion ? 'See Results' : 'Next →'}
          </button>
        </div>
      </footer>
    </div>
  );
}
