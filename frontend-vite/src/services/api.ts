import axios from 'axios';
import type { AxiosResponse } from 'axios';

// Use relative path for production, environment variable for development
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 second timeout
});

// Add request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('🔄 Services API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Services API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('✅ Services API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ Services API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Type definitions
export interface ProcessedData {
  id: string;
  filename: string;
  size: number;
  type: string;
  processed_at: string;
  data: any;
}

export interface AnalysisResult {
  id: string;
  type: string;
  results: any;
  metadata: {
    processing_time: number;
    parameters: any;
  };
}

export interface VisualizationResult {
  id: string;
  type: string;
  data: any;
  config: any;
}

export interface ApiState<T = any> {
  isLoading: boolean;
  error: string | null;
  data: T | null;
}

// API functions
export const uploadFile = async (file: File): Promise<ProcessedData> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response: AxiosResponse<ProcessedData> = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

export const analyzeData = async (dataId: string, analysisType: string, parameters?: any): Promise<AnalysisResult> => {
  try {
    const response: AxiosResponse<AnalysisResult> = await apiClient.post('/analyze', {
      data_id: dataId,
      analysis_type: analysisType,
      parameters: parameters || {}
    });
    
    return response.data;
  } catch (error) {
    console.error('Error analyzing data:', error);
    throw error;
  }
};

export const generateVisualization = async (dataId: string, vizType: string, config?: any): Promise<VisualizationResult> => {
  try {
    const response: AxiosResponse<VisualizationResult> = await apiClient.post('/visualize', {
      data_id: dataId,
      visualization_type: vizType,
      config: config || {}
    });
    
    return response.data;
  } catch (error) {
    console.error('Error generating visualization:', error);
    throw error;
  }
};

export const getExamples = async (): Promise<string[]> => {
  try {
    const response: AxiosResponse<string[]> = await apiClient.get('/examples');
    return response.data;
  } catch (error) {
    console.error('Error fetching examples:', error);
    throw error;
  }
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// Error handling utility function
export const handleApiError = (error: any): string => {
  console.error('API Error:', error);
  
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const message = error.response.data?.message || error.response.data?.detail || 'Unknown error';
    
    switch (status) {
      case 400:
        return `Bad Request: ${message}`;
      case 401:
        return 'Unauthorized: Please check your credentials';
      case 403:
        return 'Forbidden: You do not have permission to access this resource';
      case 404:
        return 'Not Found: The requested resource was not found';
      case 422:
        return `Validation Error: ${message}`;
      case 500:
        return 'Server Error: Internal server error occurred';
      case 503:
        return 'Service Unavailable: The server is temporarily unavailable';
      default:
        return `Error ${status}: ${message}`;
    }
  } else if (error.request) {
    // Request was made but no response received
    return 'Network Error: Unable to connect to the server. Please check your connection.';
  } else {
    // Something happened in setting up the request
    return `Request Error: ${error.message || 'An unexpected error occurred'}`;
  }
};

// Additional utility for displaying user-friendly error messages
export const getErrorMessage = (error: any): string => {
  return handleApiError(error);
};

// Format file size utility
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Validate file type utility
export const validateFileType = (file: File, allowedTypes: string[]): boolean => {
  return allowedTypes.some(type => file.type.includes(type) || file.name.toLowerCase().endsWith(type));
};

// Loading state utilities
export const createLoadingState = () => ({
  isLoading: false,
  error: null as string | null,
  data: null as any
});

export default apiClient;