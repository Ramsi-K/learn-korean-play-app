import React, { useState, useEffect } from 'react';
import { checkHealth, HealthStatus } from '../../services/api';

const HealthIndicator: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const status = await checkHealth();
        setHealthStatus(status);
      } catch (error) {
        console.error('Failed to check health:', error);
        setHealthStatus({
          status: 'unhealthy',
          database: 'error',
          groq_api: 'error'
        });
      } finally {
        setIsLoading(false);
      }
    };

    // Check health immediately
    checkSystemHealth();

    // Check health every 30 seconds
    const interval = setInterval(checkSystemHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-3 h-3 bg-gray-400 rounded-full animate-pulse"></div>
        <span className="text-sm text-gray-500">Checking...</span>
      </div>
    );
  }

  const isHealthy = healthStatus?.status === 'healthy';
  const dotColor = isHealthy ? 'bg-green-500' : 'bg-red-500';
  const statusText = isHealthy ? 'System Healthy' : 'System Issues';

  return (
    <div 
      className="flex items-center space-x-2 cursor-pointer"
      title={`Database: ${healthStatus?.database}, Groq API: ${healthStatus?.groq_api}`}
    >
      <div className={`w-3 h-3 ${dotColor} rounded-full ${isHealthy ? 'animate-pulse' : ''}`}></div>
      <span className="text-sm text-gray-600 dark:text-gray-300">{statusText}</span>
    </div>
  );
};

export default HealthIndicator;