import { apiCall } from './apiUtils';
import type { SearchResults } from './types';

export * from './types';  // Re-export all types for backward compatibility

export const searchOrthologuesETE = async (searchType: string, query: string, maxResults?: number): Promise<SearchResults> => {
  try {
    const response = await apiCall('/orthologue/ete-search', {
      method: 'POST',
      body: JSON.stringify({ 
        search_type: searchType, 
        query: query,
        max_results: maxResults || null,
        include_tree_image: false
      }),
    });
    return response;
  } catch (error) {
    console.error('Error searching ETE orthologues:', error);
    throw error;
  }
};

export const getETETree = async (orthogroupId: string): Promise<{ success: boolean; newick: string }> => {
  try {
    const response = await apiCall(`/orthologue/tree/${orthogroupId}`, {
      method: 'GET',
    });
    return response;
  } catch (error) {
    console.error('Error fetching ETE tree:', error);
    throw error;
  }
};

export default { searchOrthologuesETE, getETETree }; 