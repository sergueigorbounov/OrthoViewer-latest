import { apiCall } from './apiUtils';
import type { SearchResults } from './types';

export * from './types';  // Re-export all types for backward compatibility

export const searchOrthologuesETE = async (geneId: string): Promise<SearchResults> => {
  try {
    const response = await apiCall('/api/orthologue/ete-search', {
      method: 'POST',
      body: JSON.stringify({
        search_type: 'gene',
        query: geneId,
        max_results: 50,
        include_tree_image: true
      }),
    });
    return response;
  } catch (error) {
    console.error('Error searching orthologues with ETE:', error);
    throw error;
  }
};

export const getOrthologueETETree = async (orthogroupId: string): Promise<string> => {
  try {
    const response = await apiCall(`/api/orthologue/ete/tree/${orthogroupId}`, {
      method: 'GET',
    });
    return response.tree;
  } catch (error) {
    console.error('Error fetching ETE tree:', error);
    throw error;
  }
};

export default { searchOrthologuesETE, getOrthologueETETree }; 