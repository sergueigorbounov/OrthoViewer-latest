// Chunked Search API Service
export interface ChunkMetadata {
  type: 'metadata';
  query: string;
  chunk_size: number;
  max_total: number;
  timestamp: number;
}

export interface ChunkData {
  type: 'chunk';
  chunk_number: number;
  results: Array<{
    gene_id: string;
    orthogroup_id: string;
  }>;
  count: number;
  offset: number;
  total_sent: number;
}

export interface ChunkComplete {
  type: 'complete';
  total_sent: number;
  chunks_sent: number;
  query: string;
}

export type ChunkMessage = ChunkMetadata | ChunkData | ChunkComplete;

export interface ChunkedSearchResponse {
  query: string;
  chunk_number: number;
  chunk_size: number;
  results: Array<{
    gene_id: string;
    orthogroup_id: string;
  }>;
  count: number;
  offset: number;
  has_more: boolean;
  total_estimate?: number;
  estimated_chunks?: number;
  next_chunk?: number;
}

export class ChunkedSearchService {
  private baseUrl: string;

  constructor(baseUrl: string = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8003/api') {
    this.baseUrl = `${baseUrl}/orthologue`;
  }

  /**
   * Stream search results using Server-Sent Events
   */
  async *streamSearch(
    query: string,
    chunkSize: number = 50
  ): AsyncGenerator<ChunkMessage> {
    const url = `${this.baseUrl}/search/genes/stream?query=${encodeURIComponent(query)}&chunk_size=${chunkSize}`;
    
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
              yield data as ChunkMessage;
            } catch (e) {
              console.warn('Failed to parse SSE data:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Get a specific chunk of search results
   */
  async getChunk(
    query: string,
    chunkNumber: number = 1,
    chunkSize: number = 50,
    includeEstimate: boolean = true
  ): Promise<ChunkedSearchResponse> {
    const url = `${this.baseUrl}/search/genes/chunked?query=${encodeURIComponent(query)}&chunk_number=${chunkNumber}&chunk_size=${chunkSize}&total_estimate=${includeEstimate}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Get all chunks progressively (non-streaming)
   */
  async *getAllChunks(
    query: string,
    chunkSize: number = 50,
    maxChunks: number = 20
  ): AsyncGenerator<ChunkedSearchResponse> {
    let chunkNumber = 1;
    let hasMore = true;

    while (hasMore && chunkNumber <= maxChunks) {
      const chunk = await this.getChunk(query, chunkNumber, chunkSize, chunkNumber === 1);
      yield chunk;
      
      hasMore = chunk.has_more;
      chunkNumber++;
    }
  }
}

export const chunkedSearchService = new ChunkedSearchService(); 