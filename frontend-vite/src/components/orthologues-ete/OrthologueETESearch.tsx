import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Divider,
  Grid
} from '@mui/material';
import { searchOrthologuesETE, type SearchResults } from '../../api/orthologueETEApi';
import OrthologueETEResults from './OrthologueETEResults';

const OrthologueETESearch: React.FC = () => {
  const [geneId, setGeneId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null);

  const handleSearch = async () => {
    if (!geneId) {
      setError('Please enter a gene ID');
      return;
    }

    setLoading(true);
    setError(null);
    setSearchResults(null);

    try {
      console.log(`Starting ETE search for gene ID: ${geneId}`);
      const results = await searchOrthologuesETE(geneId);
      console.log(`ETE search completed for ${geneId}:`, results.success);
      setSearchResults(results);
      if (!results.success) {
        setError(results.message || 'Search failed');
      }
    } catch (error) {
      console.error('Error during ETE search:', error);
      setError('An error occurred during the search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !loading) {
      handleSearch();
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Orthologue Search (ETE)
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Enter a gene ID to find orthologues and visualize their distribution using ETE Toolkit's advanced phylogenetic analysis.
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 8', md: 'span 6' } }}>
            <TextField
              fullWidth
              label="Gene ID"
              variant="outlined"
              value={geneId}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGeneId(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g., Aco000536.1"
              InputProps={{
                endAdornment: loading ? (
                  <CircularProgress size={24} />
                ) : null,
              }}
              disabled={loading}
            />
          </Grid>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 4', md: 'span 2' } }}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={handleSearch}
              disabled={loading || !geneId}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
            <Typography variant="caption" color="textSecondary">
              Example gene IDs: Aco000536.1, AT1G01010.1, Traes_4AL_F00707FAF.1
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={60} />
            <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
              Searching for orthologues using ETE Toolkit... This may take up to 2 minutes for complex queries.
            </Typography>
          </Box>
        </Box>
      )}

      {searchResults && (
        <OrthologueETEResults results={searchResults} />
      )}
    </Box>
  );
};

export default OrthologueETESearch; 