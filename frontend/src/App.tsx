import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useThemeStore } from './store/theme';
import Navbar from './components/layout/Navbar';
import Dashboard from './components/layout/Dashboard';
import Practice from './components/pages/Practice';
import Arcade from './components/pages/Arcade';

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
              <Route path="/practice" element={<Practice />} />
              <Route path="/arcade" element={<Arcade />} />
            </Routes>
          </main>
        </div>
      </Router>
    </div>
  );
}

export default App;