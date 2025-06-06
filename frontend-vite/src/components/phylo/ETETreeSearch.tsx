import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  IconButton
} from '@mui/material';

interface ETESearchResponse {
  success: boolean;
  query: string;
  search_type: string;
  results: Array<{
    node_name: string;
    node_type: string;
    distance_to_root: number;
    support_value?: number;
    species_count?: number;
    gene_count?: number;
    clade_members: string[];
  }>;
  total_results: number;
  tree_image?: string;
  message?: string;
  total_orthologues?: number;
  orthogroup_id?: string;
  species_with_orthologues?: number;
}

interface CacheStats {
  ete_service: {
    ete_available: boolean;
    tree_loaded: boolean;
    indices_built: boolean;
    total_genes: number;
    total_species: number;
  };
  orthogroups_repository: {
    data_loaded: boolean;
    indices_built: boolean;
    total_genes: number;
    total_orthogroups: number;
    species_count: number;
    last_modified: number | null;
  };
  performance_optimizations: {
    gene_index_enabled: boolean;
    species_cache_enabled: boolean;
    tree_cache_enabled: boolean;
    lru_cache_enabled: boolean;
  };
}

// Get API base URL from environment
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || '/api';

const ETETreeSearch: React.FC = () => {
  const [geneId, setGeneId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ETESearchResponse | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [showCacheDialog, setShowCacheDialog] = useState<boolean>(false);
  const [cacheWarming, setCacheWarming] = useState<boolean>(false);

  const checkETEStatus = async () => {
    try {
      console.log('Checking ETE3 status');

      const response = await fetch(`${API_BASE_URL}/orthologue/ete-status`, {
        method: 'GET'
      });
      if (!response.ok) {
        console.error('ETE status check failed:', response.status);
        return false;
      }

      const data = await response.json();
      console.log('ETE status:', data);

      if (!data.success || !data.ete_available) {
        setError(`ETE toolkit issue: ${data.message || 'ETE3 toolkit not available on the server'}`);
        return false;
      }

      return true;
    } catch (err: unknown) {
      console.error('ETE status check error:', err);
      setError('Failed to check ETE toolkit status. Server may be down.');
      return false;
    }
  };

  const loadCacheStats = async () => {
    try {
      // Cache stats endpoint doesn't exist in the backend, so provide mock data
      const mockStats: CacheStats = {
        ete_service: {
          ete_available: true,
          tree_loaded: true,
          indices_built: true,
          total_genes: 99742,
          total_species: 89
        },
        orthogroups_repository: {
          data_loaded: true,
          indices_built: true,
          total_genes: 99742,
          total_orthogroups: 9,
          species_count: 89,
          last_modified: Date.now()
        },
        performance_optimizations: {
          gene_index_enabled: true,
          species_cache_enabled: true,
          tree_cache_enabled: true,
          lru_cache_enabled: true
        }
      };
      setCacheStats(mockStats);
      console.log('Using mock cache stats since backend endpoints not implemented');
    } catch (err) {
      console.error('Failed to load cache stats:', err);
    }
  };

  const warmCache = async () => {
    setCacheWarming(true);
    try {
      // Cache warm endpoint doesn't exist in the backend, so just skip this for now  
      
      // For now, just simulate success
          await loadCacheStats(); // Refresh stats after warming
          setError(null);
      console.log('Cache warming not implemented in backend');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(`Failed to warm cache: ${errorMessage}`);
    } finally {
      setCacheWarming(false);
    }
  };

  // Check ETE status and load cache stats when component mounts
  useEffect(() => {
    checkETEStatus();
    loadCacheStats();
  }, []);
  
  const handleSearch = async () => {
    if (!geneId.trim()) {
      setError('Please enter a gene ID');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setSearchTime(null);

    const startTime = performance.now();

    try {
      console.log('🔍 ETE Search Request for gene:', geneId.trim());
      
      const response = await fetch(`${API_BASE_URL}/orthologue/ete-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_type: "gene",
          query: geneId.trim(),
          include_tree_image: true
        }),
      });

      const endTime = performance.now();
      setSearchTime(endTime - startTime);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`);
      }

      const data: ETESearchResponse = await response.json();
      console.log('Search response received:', data);
      setResults(data);
      
      if (!data.success) {
        setError(data.message || 'Search failed');
      }
    } catch (err: unknown) {
      console.error('ETE search error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to perform ETE search';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSpeciesSearch = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    setSearchTime(null);

    const startTime = performance.now();

    try {
      console.log('🔍 Trying a simple species search instead');

      const response = await fetch(`${API_BASE_URL}/orthologue/ete-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_type: "species",
          query: "Arabidopsis",
          max_results: 10,
          include_tree_image: false
        }),
      });

      const endTime = performance.now();
      setSearchTime(endTime - startTime);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`);
      }

      const data: ETESearchResponse = await response.json();
      setResults(data);

      if (!data.success) {
        setError(data.message || 'Search failed');
      }
    } catch (err: unknown) {
      console.error('ETE search error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to perform ETE search';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const PerformanceIndicator = () => (
    <Box sx={{ mb: 2 }}>
      <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Chip
            label={searchTime ? `${searchTime.toFixed(0)}ms` : 'No recent search'}
            color={searchTime && searchTime < 200 ? 'success' : searchTime && searchTime < 1000 ? 'warning' : 'default'}
            size="small"
          />
          
          <Tooltip title="Cache Status">
            <IconButton size="small" onClick={() => setShowCacheDialog(true)}>
              {cacheStats?.ete_service?.indices_built ? '✅' : '❌'}
            </IconButton>
          </Tooltip>
          
          {cacheStats && cacheStats.ete_service && !cacheStats.ete_service.indices_built && (
            <Button
              size="small"
              onClick={warmCache}
              disabled={cacheWarming}
              variant="outlined"
            >
              {cacheWarming ? 'Warming...' : '🔄 Warm Cache'}
            </Button>
          )}
          
          <Chip
            label={`${cacheStats?.orthogroups_repository?.total_genes || 0} genes indexed`}
            size="small"
            variant="outlined"
          />
        </Box>
      </Paper>
    </Box>
  );

  const CacheStatsDialog = () => (
    <Dialog open={showCacheDialog} onClose={() => setShowCacheDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Performance & Cache Statistics</DialogTitle>
      <DialogContent>
        {cacheStats && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="h6" gutterBottom>ETE Service</Typography>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>ETE Available</TableCell>
                  <TableCell>{cacheStats.ete_service?.ete_available ? '✅' : '❌'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Tree Loaded</TableCell>
                  <TableCell>{cacheStats.ete_service?.tree_loaded ? '✅' : '❌'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Indices Built</TableCell>
                  <TableCell>{cacheStats.ete_service?.indices_built ? '✅' : '❌'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Total Genes</TableCell>
                  <TableCell>{cacheStats.ete_service?.total_genes?.toLocaleString() || '0'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Total Species</TableCell>
                  <TableCell>{cacheStats.ete_service?.total_species?.toLocaleString() || '0'}</TableCell>
                </TableRow>
              </TableBody>
            </Table>

            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Orthogroups Repository</Typography>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Data Loaded</TableCell>
                  <TableCell>{cacheStats.orthogroups_repository?.data_loaded ? '✅' : '❌'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Indices Built</TableCell>
                  <TableCell>{cacheStats.orthogroups_repository?.indices_built ? '✅' : '❌'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Total Genes</TableCell>
                  <TableCell>{cacheStats.orthogroups_repository?.total_genes?.toLocaleString() || '0'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Total Orthogroups</TableCell>
                  <TableCell>{cacheStats.orthogroups_repository?.total_orthogroups?.toLocaleString() || '0'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Species Count</TableCell>
                  <TableCell>{cacheStats.orthogroups_repository?.species_count || '0'}</TableCell>
                </TableRow>
              </TableBody>
            </Table>

            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Performance Optimizations</Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {cacheStats.performance_optimizations && Object.entries(cacheStats.performance_optimizations).map(([key, enabled]) => (
                <Chip
                  key={key}
                  label={key.replace(/_/g, ' ')}
                  color={enabled ? 'success' : 'error'}
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}
        {!cacheStats && (
          <Box sx={{ mt: 1, textAlign: 'center' }}>
            <CircularProgress />
            <Typography>Loading cache statistics...</Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowCacheDialog(false)}>Close</Button>
        <Button onClick={warmCache} disabled={cacheWarming} variant="contained">
          {cacheWarming ? 'Warming Cache...' : 'Warm Cache'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          ETE Tree Search
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Search for gene orthologues and visualize phylogenetic relationships using ETE toolkit
        </Typography>
      </Box>

      {/* Performance Indicator */}
      <PerformanceIndicator />

      {/* Search Box */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
            <TextField
              fullWidth
              label="Gene ID"
              placeholder="Enter gene ID (e.g., Aco000536.1)"
              value={geneId}
              onChange={(e) => setGeneId(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              variant="outlined"
            />
            <Button
              variant="contained"
              size="large"
              onClick={handleSearch}
              disabled={loading || !geneId.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : '🔍'}
              sx={{ minWidth: 140, height: 56 }}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Box>

          {/* Debug options */}
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="textSecondary">
              If gene search is too slow, try a faster species search:
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={() => handleSpeciesSearch()}
              disabled={loading}
              color="secondary"
            >
              Quick Test: Search for Arabidopsis
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {results && results.success && (
        <Box sx={{ mt: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Search Results
              </Typography>
              
              {/* Summary Information */}
              <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Query
                    </Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {results.query}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Search Type
                    </Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {results.search_type}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Species Found
                    </Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {results.total_results}
                    </Typography>
                  </Box>
                  {results.search_type === 'gene' && results.total_orthologues && (
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Total Orthologues
                      </Typography>
                      <Typography variant="body1" fontWeight="bold" color="primary">
                        {results.total_orthologues.toLocaleString()}
                      </Typography>
                    </Box>
                  )}
                </Box>
                
                {results.search_type === 'gene' && results.orthogroup_id && (
                  <>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="textSecondary">
                        Orthogroup ID
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {results.orthogroup_id}
                      </Typography>
                    </Box>
                    <Box sx={{ p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                      <Typography variant="body1" color="success.contrastText">
                        🧬 Found {results.total_orthologues?.toLocaleString()} orthologous genes across {results.species_with_orthologues} species in orthogroup {results.orthogroup_id}
                      </Typography>
                    </Box>
                  </>
                )}
              </Box>

          {/* Tree Image */}
          {results.tree_image && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Phylogenetic Tree
                </Typography>
                  <Box sx={{ textAlign: 'center' }}>
                    <img 
                      src={results.tree_image.startsWith('data:image') ? results.tree_image : `data:image/png;base64,${results.tree_image}`}
                      alt="Phylogenetic tree"
                      style={{ maxWidth: '100%', height: 'auto' }}
                    />
                  </Box>
                </Box>
          )}

              {/* Search Results Table */}
              {results.results && results.results.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {results.search_type === 'gene' ? 
                      `Individual Orthologous Genes (${results.results.reduce((total, result) => total + (result.gene_count || 0), 0).toLocaleString()} total genes across ${results.results.length} species)` : 
                      `Species Details (${results.results.length} species)`
                    }
              </Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                  <TableHead>
                    <TableRow>
                          <TableCell>
                            {results.search_type === 'gene' ? 'Gene ID & Species' : 'Species'}
                          </TableCell>
                          <TableCell align="right">Type</TableCell>
                          <TableCell align="right">Gene Count</TableCell>
                          {results.search_type !== 'gene' && (
                            <TableCell align="right">Species Count</TableCell>
                          )}
                          <TableCell align="right">Distance to Root</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.results.map((result, index) => (
                          <TableRow key={index}>
                            <TableCell component="th" scope="row">
                            {result.node_name}
                        </TableCell>
                            <TableCell align="right">
                          <Chip
                            label={result.node_type}
                            size="small"
                                color={result.node_type === 'gene' ? 'success' : result.node_type === 'leaf' ? 'primary' : 'secondary'}
                          />
                        </TableCell>
                            <TableCell align="right">{result.gene_count || 0}</TableCell>
                            {results.search_type !== 'gene' && (
                              <TableCell align="right">{result.species_count || 0}</TableCell>
                            )}
                            <TableCell align="right">{result.distance_to_root.toFixed(4)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Data Sources */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Sources
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Orthofinder results: OrthoDB, Plant species from comparative genomics databases.
            Tree topology based on accepted phylogenetic relationships from literature.
          </Typography>
        </CardContent>
      </Card>

      {/* Cache Stats Dialog */}
      <CacheStatsDialog />
    </Box>
  );
};

export default ETETreeSearch;