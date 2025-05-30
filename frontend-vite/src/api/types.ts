export interface SpeciesCountData {
  species_id?: string;  // Optional to support both API formats
  species_name: string;
  count: number;
}

export interface OrthologueInfo {
  gene_id: string;
  species_id: string;
  species_name: string;
  orthogroup_id: string;
  ete_tree_data?: string;  // Optional ETE-specific tree data
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
  ete_tree?: string;  // Optional ETE-specific tree format
  message?: string;
} 