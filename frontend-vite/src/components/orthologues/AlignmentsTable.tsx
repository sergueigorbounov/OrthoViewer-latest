import React, { useCallback } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import type { OrthologueInfo } from '../../api/orthologueApi';

interface AlignmentsTableProps {
  orthologues: OrthologueInfo[];
  selectedSpecies: string | null;
  onSpeciesSelected: (species: string | null) => void;
  onTabChange?: (tabIndex: number) => void;
}

const AlignmentsTable: React.FC<AlignmentsTableProps> = ({
  orthologues,
  selectedSpecies,
  onSpeciesSelected,
  onTabChange
}) => {
  // FIXED: Create a function to check if a species is selected - using strict matching
  const isSpeciesSelected = useCallback((speciesName: string): boolean => {
    if (!selectedSpecies || !speciesName) return false;
    
    // Use strict matching - only exact matches (case-insensitive)
    const normalized1 = speciesName.toLowerCase().trim();
    const normalized2 = selectedSpecies.toLowerCase().trim();
    
    // Only return true for an exact match
    return normalized1 === normalized2;
    
  }, [selectedSpecies]);

  const handleRowClick = useCallback((species: string) => {
    console.log(`Alignment row clicked: ${species}`);
    
    // Toggle selection - if already selected, clear it; otherwise set the new species
    if (selectedSpecies === species) {
      onSpeciesSelected(null);
    } else {
      onSpeciesSelected(species);
      // Navigate to tree tab when selecting a species
      if (onTabChange) {
        console.log("Navigating to tree tab after row selection");
        onTabChange(1); // Switch to Tree tab
      }
    }
  }, [selectedSpecies, onSpeciesSelected, onTabChange]);

  return (
    <TableContainer sx={{ maxHeight: '600px' }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell>Species</TableCell>
            <TableCell>Gene ID</TableCell>
            <TableCell>Species ID</TableCell>
            <TableCell>Orthogroup</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {orthologues.map((ortho, idx) => {
            // Get fresh selection state for this render
            const isSelected = isSpeciesSelected(ortho.species_name);
            
            return (
              <TableRow 
                key={`orthologue-${ortho.gene_id}-${idx}`}
                hover
                onClick={() => handleRowClick(ortho.species_name)}
                selected={isSelected}
                sx={{ 
                  cursor: 'pointer',
                  backgroundColor: isSelected ? 'rgba(25, 118, 210, 0.08)' : undefined
                }}
              >
                <TableCell>{ortho.species_name}</TableCell>
                <TableCell>{ortho.gene_id}</TableCell>
                <TableCell>{ortho.species_id}</TableCell>
                <TableCell>{ortho.orthogroup_id}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default AlignmentsTable;