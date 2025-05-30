import React from 'react';
import { Box, Container, Typography, Paper, Divider } from '@mui/material';
import OrthologueETESearch from '../orthologues-ete/OrthologueETESearch';

const OrthologueETEPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gene Orthologue Search (ETE Toolkit)
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Search for orthologous genes using ETE Toolkit for advanced phylogenetic analysis.
          Enter a gene ID to find its orthogroup members and view their phylogenetic relationships with enhanced tree visualization.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Paper elevation={2} sx={{ p: 0, mt: 3 }}>
          <OrthologueETESearch />
        </Paper>
      </Box>
    </Container>
  );
};

export default OrthologueETEPage; 