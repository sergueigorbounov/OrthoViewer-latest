// OrthologueSearch.tsx
// This component provides a search interface for finding gene orthologues.
// 
// Example usage:
// ```tsx
// <OrthologueSearch />
// ```
//
// Flow:
// 1. User enters a gene ID
// 2. Component validates input
// 3. Makes API call to search orthologues
// 4. Displays results or error
//
// State management:
// ```tsx
// const [geneId, setGeneId] = useState<string>(''); // Stores current gene ID
// const [loading, setLoading] = useState<boolean>(false); // Tracks API call status
// const [error, setError] = useState<string | null>(null); // Stores error messages
// const [searchResults, setSearchResults] = useState<SearchResults | null>(null); // Stores API response
// ```

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
import { searchOrthologues, type SearchResults } from '../../api/orthologueApi';
import OrthologueResults from './OrthologueResults';

const OrthologueSearch: React.FC = () => {
  const [geneId, setGeneId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null);

  // handleSearch: Performs the orthologue search
  // 
  // Example:
  // ```tsx
  // await handleSearch(); // Searches for current geneId
  // ```
  //
  // Error handling:
  // - Network errors: Shows connectivity message
  // - Timeout: Suggests trying again
  // - 404: Invalid gene ID
  // - 500: Server error
  const handleSearch = async () => {
    if (!geneId) {
      setError('Please enter a gene ID');
      return;
    }

    setLoading(true);
    setError(null);
    setSearchResults(null);

    try {
      console.log(`Starting search for gene ID: ${geneId}`);
      const results = await searchOrthologues(geneId);
      console.log(`Search completed for ${geneId}:`, results.success);
      setSearchResults(results);
      if (!results.success) {
        setError(results.message || 'Search failed');
      }
    } catch (err: any) {
      console.error('Error searching for orthologues:', err);

      // Check for specific error types to provide better messages
      if (err.message && err.message.includes('Failed to fetch')) {
        setError('Unable to connect to the backend server. Please check that the backend service is running.');
      } else if (err.message && err.message.includes('timeout')) {
        setError('The search timed out. This may happen for complex queries. You could try a different gene ID or try again later when the server is less busy.');
      } else if (err.message && err.message.includes('404')) {
        setError(`Gene ID "${geneId}" not found. Please check the ID and try again.`);
      } else if (err.message && err.message.includes('500')) {
        setError('The server encountered an error processing this request. The administrators have been notified.');
      } else {
        setError(err.message || 'Failed to search for orthologues. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // handleKeyDown: Enables search on Enter key press
  // 
  // Example:
  // ```tsx
  // <TextField onKeyDown={handleKeyDown} />
  // ```
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && geneId) {
      handleSearch();
    }
  };

  // Render: Component layout
  // 
  // Structure:
  // 1. Title and description
  // 2. Search form with gene ID input
  // 3. Error alerts if any
  // 4. Loading indicator during search
  // 5. Results display when available
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Orthologue Search
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Enter a gene ID to find orthologues and visualize their distribution across species.
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
              Searching for orthologues... This may take up to 2 minutes for complex queries.
            </Typography>
          </Box>
        </Box>
      )}

      {searchResults && (
        <OrthologueResults results={searchResults} />
      )}
    </Box>
  );
};

// Export the component for use in other parts of the application
export default OrthologueSearch;