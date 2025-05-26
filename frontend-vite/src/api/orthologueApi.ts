const apiUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8003';

export interface SpeciesCountData {
  species_id: string;
  species_name: string;
  count: number;
}

export interface OrthologueInfo {
  gene_id: string;
  species_id: string;
  species_name: string;
  orthogroup_id: string;
}

export interface SearchRequest {
  gene_id: string;
}

export interface SearchResults {
  success: boolean;
  gene_id: string;
  orthogroup_id?: string;
  orthologues: OrthologueInfo[];
  counts_by_species: SpeciesCountData[];
  newick_tree?: string;
  message?: string;
}

// Helper function for API calls
async function apiCall(endpoint: string, options: RequestInit = {}): Promise<any> {
  const url = `${apiUrl}${endpoint}`;
  
  console.log('🔍 Orthologue API Request:', options.method || 'GET', url);
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  // Create an AbortController to handle timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000); // 120 second timeout (increased from 60s)

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

      console.log('✅ Orthologue API Response:', response.status, url);
      
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
        console.error('❌ Orthologue API Timeout: Request took too long to complete');
        throw new Error('Request timeout: The search is taking too long to complete. Please try again or use a different gene ID.');
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
  console.error('❌ Orthologue API Error after retries:', lastError);
  throw lastError || new Error('Failed to fetch after retries');
}

export const searchOrthologues = async (geneId: string): Promise<SearchResults> => {
  try {
    const response = await apiCall('/api/orthologue/search', {
      method: 'POST',
      body: JSON.stringify({ gene_id: geneId }),
    });
    return response;
  } catch (error) {
    console.error('Error searching orthologues:', error);
    throw error;
  }
};

export const getOrthologueTree = async (): Promise<{ success: boolean; newick: string }> => {
  try {
    const response = await apiCall('/api/orthologue/tree');
    return response;
  } catch (error) {
    console.error('Error fetching tree:', error);
    throw error;
  }
};

export default { searchOrthologues, getOrthologueTree };