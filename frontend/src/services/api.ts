// src/services/api.ts
// Base API configuration

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

interface RequestOptions {
  method?: RequestMethod;
  headers?: HeadersInit;
  body?: any;
}

/**
 * Base API request function
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', headers = {}, body } = options;
  
  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  };
  
  const config: RequestInit = {
    method,
    headers: requestHeaders,
    body: body ? JSON.stringify(body) : undefined,
  };
  
  try {
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, config);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    return data as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Health check types
 */
export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  database: 'ok' | 'error';
  groq_api: 'ok' | 'error';
}

/**
 * Check system health
 */
export async function checkHealth(): Promise<HealthStatus> {
  try {
    // Health endpoint is not under /api prefix
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    // Return unhealthy status if health check fails
    return {
      status: 'unhealthy',
      database: 'error',
      groq_api: 'error'
    };
  }
}