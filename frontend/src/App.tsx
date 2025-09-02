import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useThemeStore } from './store/theme';
import Navbar from './components/layout/Navbar';
import Dashboard from './components/layout/Dashboard';

// Simple minimal components for V1
const PracticePage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold">Word Practice</h1>
    <p className="text-lg opacity-80">Practice Korean words with AI-powered exercises.</p>
    <div className="bg-blue-500/20 border border-blue-500/50 p-4 rounded-lg">
      <p>Practice features coming soon! This will include AI-generated exercises for Korean vocabulary.</p>
    </div>
  </div>
);

const ArcadePage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold">Arcade</h1>
    <p className="text-lg opacity-80">Play games to learn Korean in a fun way.</p>
    <div className="bg-green-500/20 border border-green-500/50 p-4 rounded-lg">
      <p>Arcade games coming soon! This will include flashcard games and other interactive learning activities.</p>
    </div>
  </div>
);

function App() {
  const theme = useThemeStore((state) => state.theme);

  return (
    <div className={theme}>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/practice" element={<PracticePage />} />
              <Route path="/arcade" element={<ArcadePage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </div>
  );
}

export default App;