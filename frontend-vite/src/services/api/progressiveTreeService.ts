// Progressive Tree Loading Service
export interface TreePreview {
  success: boolean;
  orthogroup_id: string;
  preview: {
    total_species: number;
    total_genes: number;
    estimated_load_time: string;
    has_tree_data: boolean;
  };
  instant_tree?: {
    newick: string;
    species_list: string[];
    is_simplified: boolean;
  };
  loading: boolean;
  stream_url: string;
  response_time_ms: number;
}

export interface TreeChunkMessage {
  type: 'metadata' | 'species_chunk' | 'tree_complete' | 'error';
  orthogroup_id?: string;
  chunk_number?: number;
  species?: Array<{
    species_name: string;
    species_id: string;
    count: number;
  }>;
  progress?: number;
  newick?: string;
  total_species?: number;
  message?: string;
  timestamp?: number;
}

export class ProgressiveTreeService {
  private baseUrl: string;

  constructor(baseUrl: string = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8003/api') {
    this.baseUrl = `${baseUrl}/orthologue`;
  }

  /**
   * Get instant tree preview (< 50ms response)
   */
  async getTreePreview(orthogroupId: string): Promise<TreePreview> {
    const url = `${this.baseUrl}/tree/progressive/${orthogroupId}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Stream complete tree data in chunks
   */
  async *streamTreeData(orthogroupId: string): AsyncGenerator<TreeChunkMessage> {
    const url = `${this.baseUrl}/tree/stream/${orthogroupId}`;
    
    const response = await fetch(url, {
      headers: {
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep last line in buffer (might be incomplete)
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data as TreeChunkMessage;
            } catch (e) {
              console.warn('Failed to parse SSE tree data:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

export const progressiveTreeService = new ProgressiveTreeService(); 