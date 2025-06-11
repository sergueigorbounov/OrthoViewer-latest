const apiUrl = import.meta.env.VITE_BACKEND_URL || '';

export async function apiCall(endpoint: string, options: RequestInit = {}): Promise<any> {
  // Ensure endpoint starts with /api if not already present
  const normalizedEndpoint = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
  const url = `${apiUrl}${normalizedEndpoint}`;
  
  console.log('🔍 API Request:', options.method || 'GET', url);
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  // Create an AbortController to handle timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000); // 120 second timeout

  const MAX_RETRIES = 2;
  let retries = 0;
  let lastError: any = null;

  while (retries < MAX_RETRIES) {
    try {
      const response = await fetch(url, {
        ...defaultOptions,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId); // Clear the timeout if request completes

      console.log('✅ API Response:', response.status, url);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`);
      }
      
      return await response.json();
    } catch (error: any) {
      lastError = error;

      // Don't retry on abort (timeout)
      if (error.name === 'AbortError') {
        clearTimeout(timeoutId);
        console.error('❌ API Timeout: Request took too long to complete');
        throw new Error('Request timeout: The operation is taking too long to complete. Please try again.');
      }

      // Don't retry on 404 or other client errors
      if (error.message && error.message.includes('status: 4')) {
        clearTimeout(timeoutId);
        throw error;
      }

      // Log retry attempt
      retries++;
      console.log(`Retry attempt ${retries}/${MAX_RETRIES} for ${url}`);

      // Wait before retrying (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, 1000 * retries));
    }
  }

  clearTimeout(timeoutId);
  console.error('❌ API Error after retries:', lastError);
  throw lastError || new Error('Failed to fetch after retries');
} 