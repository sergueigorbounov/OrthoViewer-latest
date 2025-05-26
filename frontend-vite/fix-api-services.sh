#!/bin/bash
echo "🔧 Fixing missing API service functions..."

# Check what functions are being imported
echo "Functions being imported from services/api:"
grep -r "from.*services/api" src/ | grep -o "{[^}]*}" | sort | uniq

# Add commonly used API utility functions
cat >> src/services/api.ts << 'FUNCTIONS'

// Error handling utilities
export const handleApiError = (error: any): string => {
  console.error('API Error:', error);
  
  if (error.response) {
    const status = error.response.status;
    const message = error.response.data?.message || error.response.data?.detail || 'Unknown error';
    
    switch (status) {
      case 400:
        return `Bad Request: ${message}`;
      case 401:
        return 'Unauthorized: Please check your credentials';
      case 403:
        return 'Forbidden: Access denied';
      case 404:
        return 'Not Found: Resource not found';
      case 422:
        return `Validation Error: ${message}`;
      case 500:
        return 'Server Error: Internal server error';
      case 503:
        return 'Service Unavailable: Server temporarily unavailable';
      default:
        return `Error ${status}: ${message}`;
    }
  } else if (error.request) {
    return 'Network Error: Unable to connect to server';
  } else {
    return `Request Error: ${error.message || 'Unexpected error'}`;
  }
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

export interface ApiState<T = any> {
  isLoading: boolean;
  error: string | null;
  data: T | null;
}

FUNCTIONS

echo "✅ Added missing API utility functions!"
