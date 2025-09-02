import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { checkHealth } from '../../services/api';

interface QuickStats {
  total_words: number;
  total_sessions: number;
  total_mistakes: number;
}

interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  database: 'ok' | 'error';
  groq_api: 'ok' | 'error';
}

const Dashboard = () => {
  const [stats, setStats] = useState<QuickStats | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get health status
        const healthData = await checkHealth();
        setHealth(healthData);

        // Get quick stats from the API
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
        const response = await fetch(`${API_URL}/dashboard/quick-stats`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch stats: ${response.status}`);
        }
        
        const statsData = await response.json();
        setStats(statsData);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        setError(error instanceof Error ? error.message : 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="space-y-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
          <span className="ml-2">Loading dashboard...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      {error && (
        <div className="bg-red-500/20 border border-red-500/50 p-4 rounded-lg">
          <p className="text-red-200">Error: {error}</p>
        </div>
      )}

      {/* Quick Stats */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-blue-500/20 border border-blue-500/50 p-6 rounded-lg">
          <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
          {stats ? (
            <div className="space-y-2">
              <p>Total Words: <span className="font-bold text-blue-300">{stats.total_words}</span></p>
              <p>Study Sessions: <span className="font-bold text-blue-300">{stats.total_sessions}</span></p>
              <p>Total Mistakes: <span className="font-bold text-blue-300">{stats.total_mistakes}</span></p>
            </div>
          ) : (
            <p className="text-gray-400">Stats unavailable</p>
          )}
        </div>

        {/* Health Status */}
        <div className="bg-green-500/20 border border-green-500/50 p-6 rounded-lg">
          <h2 className="text-xl font-bold mb-4">System Health</h2>
          {health ? (
            <div className="space-y-2">
              <p>Status: <span className={`font-bold ${health.status === 'healthy' ? 'text-green-300' : 'text-red-300'}`}>
                {health.status}
              </span></p>
              <p>Database: <span className={`font-bold ${health.database === 'ok' ? 'text-green-300' : 'text-red-300'}`}>
                {health.database}
              </span></p>
              <p>AI Service: <span className={`font-bold ${health.groq_api === 'ok' ? 'text-green-300' : 'text-red-300'}`}>
                {health.groq_api}
              </span></p>
            </div>
          ) : (
            <p className="text-gray-400">Health check unavailable</p>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-purple-500/20 border border-purple-500/50 p-6 rounded-lg">
          <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
          <div className="flex flex-col space-y-3">
            <Link 
              to="/practice" 
              className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-center transition-colors"
            >
              Start Practice
            </Link>
            <Link 
              to="/arcade" 
              className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-center transition-colors"
            >
              Play Arcade
            </Link>
          </div>
        </div>
      </section>

      {/* Navigation Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link to="/practice" className="group">
          <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/50 p-8 rounded-lg hover:border-blue-400 transition-colors">
            <h3 className="text-2xl font-bold mb-2 group-hover:text-blue-300">Word Practice</h3>
            <p className="text-gray-300">Practice Korean vocabulary with AI-powered exercises and personalized learning.</p>
          </div>
        </Link>

        <Link to="/arcade" className="group">
          <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 border border-green-500/50 p-8 rounded-lg hover:border-green-400 transition-colors">
            <h3 className="text-2xl font-bold mb-2 group-hover:text-green-300">Arcade Games</h3>
            <p className="text-gray-300">Learn through fun and interactive games designed to improve your Korean skills.</p>
          </div>
        </Link>
      </section>
    </div>
  );
};

export default Dashboard;
