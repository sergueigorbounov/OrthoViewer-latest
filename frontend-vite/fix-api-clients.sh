#!/bin/bash
echo "🔧 Fixing API clients..."

# Fix port numbers (8002 -> 8003) and axios imports
find src/api -name "*.ts" | while read file; do
  echo "Fixing $file"
  
  # Fix port number
  sed -i 's/localhost:8002/localhost:8003/g' "$file"
  
  # Fix any AxiosResponse imports
  sed -i 's/import.*{.*AxiosResponse.*}.*from.*axios.*/import axios from "axios";\nimport type { AxiosResponse } from "axios";/g' "$file"
done

# Update orthologueClient.ts
cat > src/api/orthologueClient.ts << 'ORTHO'
import axios from 'axios';
import type { AxiosResponse } from 'axios';

// Use environment variable or default to port 8003
const apiUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8003';

// Create API client with better error handling
const orthologueClient = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor
orthologueClient.interceptors.request.use(
  (config) => {
    console.log('🔍 Orthologue API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Orthologue API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
orthologueClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('✅ Orthologue API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ Orthologue API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Export types for orthologue data
export interface OrthoSpeciesCount {
  species_id: string;
  species_name: string;
  count: number;
}

export interface OrthologueData {
  gene_id: string;
  species_id: string;
  species_name: string;
  orthogroup_id: string;
}

export interface OrthologueSearchRequest {
  gene_id: string;
}

export interface OrthologueSearchResponse {
  success: boolean;
  gene_id: string;
  orthogroup_id?: string;
  orthologues: OrthologueData[];
  counts_by_species: OrthoSpeciesCount[];
  newick_tree?: string;
  message?: string;
}

// API functions
export const searchOrthologues = async (geneId: string): Promise<OrthologueSearchResponse> => {
  try {
    const response = await orthologueClient.post('/api/orthologue/search', {
      gene_id: geneId
    });
    return response.data;
  } catch (error) {
    console.error('Error searching orthologues:', error);
    throw error;
  }
};

export const getOrthologueTree = async (): Promise<{ success: boolean; newick: string }> => {
  try {
    const response = await orthologueClient.get('/api/orthologue/tree');
    return response.data;
  } catch (error) {
    console.error('Error fetching tree:', error);
    throw error;
  }
};

export default orthologueClient;
ORTHO

# Update phyloClient.ts
cat > src/api/phyloClient.ts << 'PHYLO'
import axios from 'axios';
import type { AxiosResponse } from 'axios';

// Use environment variable or default to port 8003
const apiUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8003';

// Create API client with better error handling
const phyloClient = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor
phyloClient.interceptors.request.use(
  (config) => {
    console.log('🧬 Phylo API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Phylo API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
phyloClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('✅ Phylo API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ Phylo API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Phylogenetic analysis types
export interface TreeAnalysisRequest {
  newick_data: string;
  species_counts?: any[];
}

export interface TreeAnalysisResponse {
  success: boolean;
  analysis: any;
  tree_newick: string;
  message?: string;
}

// API functions
export const analyzeTree = async (newickData: string, speciesCounts?: any[]): Promise<TreeAnalysisResponse> => {
  try {
    const response = await phyloClient.post('/api/phylo/analyze-tree', {
      newick_data: newickData,
      species_counts: speciesCounts
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing tree:', error);
    throw error;
  }
};

export const getEnvironmentStatus = async () => {
  try {
    const response = await phyloClient.get('/api/phylo/environment-status');
    return response.data;
  } catch (error) {
    console.error('Error getting environment status:', error);
    throw error;
  }
};

export default phyloClient;
PHYLO

echo "✅ API clients fixed!"
echo "🎯 Updated ports: 8002 -> 8003"
echo "🔧 Fixed axios imports"
