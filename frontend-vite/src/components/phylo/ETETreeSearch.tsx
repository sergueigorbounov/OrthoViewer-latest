import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  AccountTree as TreeIcon,
  Timeline as GeneIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface OrthologueData {
  species: string;
  gene_count: number;
  genes: string[];
}

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
}

const ETETreeSearch: React.FC = () => {
  const [geneId, setGeneId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ETESearchResponse | null>(null);

  const checkETEStatus = async () => {
    try {
      console.log('Checking ETE3 status');

      const response = await fetch('http://localhost:8003/api/orthologue/ete-status', {
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
    } catch (err: any) {
      console.error('ETE status check error:', err);
      setError('Failed to check ETE toolkit status. Server may be down.');
      return false;
    }
  };

  // Check ETE status when component mounts
  useEffect(() => {
    checkETEStatus();
  }, []);
  
  const handleSearch = async () => {
    if (!geneId.trim()) {
      setError('Please enter a gene ID');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('🔍 ETE Search Request for gene:', geneId.trim());
      // Create an AbortController with a timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // Increased to 60 second timeout

      console.log('Sending request with payload:', {
          search_type: "gene",
          query: geneId.trim(),
          max_results: 50,
          include_tree_image: true
      });
      const response = await fetch('http://localhost:8003/api/orthologue/ete-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_type: "gene",
          query: geneId.trim(),
          max_results: 50,
          include_tree_image: true
        }),
        signal: controller.signal
      });

      // Clear the timeout as we got a response
      clearTimeout(timeoutId);

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
    } catch (err: any) {
      console.error('ETE search error:', err);
      if (err.name === 'AbortError') {
        setError('Search timed out after 60 seconds. The server may be processing a complex query. You can try again or use a different gene ID.');
      } else {
        setError(err.message || 'Failed to perform ETE search');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSpeciesSearch = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('🔍 Trying a simple species search instead');

      // Create an AbortController with a timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // Increased to 30 second timeout

      // Try a species search instead which might be faster
      const response = await fetch('http://localhost:8003/api/orthologue/ete-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_type: "species",
          query: "Arabidopsis",  // Common species, should be quick to find
          max_results: 10,
          include_tree_image: false
        }),
        signal: controller.signal
      });

      // Clear the timeout as we got a response
      clearTimeout(timeoutId);

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
    } catch (err: any) {
      console.error('ETE search error:', err);
      if (err.name === 'AbortError') {
        setError('Search timed out after 30 seconds. The server may be overloaded.');
      } else {
        setError(err.message || 'Failed to perform ETE search');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <TreeIcon color="primary" sx={{ fontSize: 40 }} />
          ETE Tree Search
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Search for gene orthologues and visualize phylogenetic relationships using ETE toolkit
        </Typography>
      </Box>

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
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
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
        <Box>
          {/* Results Summary */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <InfoIcon />
                Search Results
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={`Gene: ${results.query}`}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`Type: ${results.search_type}`}
                  color="secondary"
                  variant="outlined"
                />
                <Chip
                  label={`${results.total_results} results`}
                  color="info"
                  variant="outlined"
                />
              </Box>
              {results.message && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  {results.message}
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Tree Image */}
          {results.tree_image && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TreeIcon />
                  Phylogenetic Tree
                </Typography>
                <Box sx={{
                  mt: 2,
                  display: 'flex',
                  justifyContent: 'center',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  p: 2
                }}>
                  <img
                    src={results.tree_image}
                    alt="Phylogenetic Tree"
                    style={{ maxWidth: '100%', maxHeight: '600px' }}
                  />
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Results Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <GeneIcon />
                Search Results ({results.total_results})
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Node Name</strong></TableCell>
                      <TableCell><strong>Type</strong></TableCell>
                      <TableCell align="center"><strong>Distance to Root</strong></TableCell>
                      <TableCell align="center"><strong>Species Count</strong></TableCell>
                      <TableCell align="center"><strong>Gene Count</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.results.map((result, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                            {result.node_name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={result.node_type}
                            size="small"
                            color={result.node_type === 'leaf' ? 'success' : 'primary'}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="center">
                          {result.distance_to_root.toFixed(4)}
                        </TableCell>
                        <TableCell align="center">
                          {result.species_count || '—'}
                        </TableCell>
                        <TableCell align="center">
                          {result.gene_count || '—'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Typography variant="caption" color="textSecondary" component="div">
                  <strong>Data Sources:</strong>
                  <br />• Orthogroups: data/orthofinder/Orthogroups_clean_121124.txt
                  <br />• Species tree: data/orthofinder/SpeciesTree_nameSp_completeGenome110124.tree
                  <br />• Species mapping: data/orthofinder/Table_S1_Metadata_angiosperm_species.csv
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {results.results.length === 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              No results found for gene "{results.query}". 
              The gene may not be present in the dataset.
            </Alert>
          )}
        </Box>
      )}

      {/* Example/Help Section */}
      {!results && !loading && (
        <Card sx={{ bgcolor: 'grey.50' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Example Usage
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Try searching for: <strong>Aco000536.1</strong>
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              This will:
            </Typography>
            <Typography variant="body2" color="textSecondary" component="ul" sx={{ pl: 2 }}>
              <li>Search for the gene across all species in the tree</li>
              <li>Display a visualization of the phylogenetic tree</li>
              <li>Show species containing this gene and their relationships</li>
              <li>Use ETE toolkit for advanced tree analysis</li>
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  setGeneId('Aco000536.1');
                }}
              >
                Try Example: Aco000536.1
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ETETreeSearch;