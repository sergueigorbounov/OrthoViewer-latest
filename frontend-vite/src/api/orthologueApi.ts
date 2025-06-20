import { apiCall } from './apiUtils';
import type { SearchResults } from './types';

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

export const searchOrthologues = async (geneId: string): Promise<SearchResults> => {
  try {
    const response = await apiCall('/orthologue/search', {
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
    const response = await apiCall('/orthologue/tree');
    return response;
  } catch (error) {
    console.error('Error fetching tree:', error);
    throw error;
  }
};

export const getOrthologueTreeByOrthogroup = async (orthogroupId: string): Promise<any> => {
  try {
    const response = await apiCall(`/orthologue/ete/tree/${orthogroupId}`);
    return response;
  } catch (error) {
    console.error('Error fetching tree by orthogroup:', error);
    throw error;
  }
};

export default { searchOrthologues, getOrthologueTree, getOrthologueTreeByOrthogroup };