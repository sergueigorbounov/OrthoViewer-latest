import React, { useCallback } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  IconButton
} from '@mui/material';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import type { OrthologueInfo } from '../../api/orthologueETEApi';

interface AlignmentsTableETEProps {
  orthologues: OrthologueInfo[];
  selectedSpecies: string | null;
  onSpeciesSelected: (species: string | null) => void;
  onTabChange?: (tabIndex: number) => void;
}

const AlignmentsTableETE: React.FC<AlignmentsTableETEProps> = ({
  orthologues,
  selectedSpecies,
  onSpeciesSelected,
  onTabChange
}) => {
  const isSpeciesSelected = useCallback((speciesName: string): boolean => {
    if (!selectedSpecies || !speciesName) return false;
    const normalized1 = speciesName.toLowerCase().trim();
    const normalized2 = selectedSpecies.toLowerCase().trim();
    return normalized1 === normalized2;
  }, [selectedSpecies]);

  const handleRowClick = useCallback((species: string) => {
    console.log(`ETE Alignment row clicked: ${species}`);
    if (selectedSpecies === species) {
      onSpeciesSelected(null);
    } else {
      onSpeciesSelected(species);
      if (onTabChange) {
        console.log("Navigating to ETE tree tab after row selection");
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
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {orthologues.map((ortho, idx) => {
            const isSelected = isSpeciesSelected(ortho.species_name);
            
            return (
              <TableRow 
                key={`orthologue-ete-${ortho.gene_id}-${idx}`}
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
                <TableCell>
                  {ortho.ete_tree_data && (
                    <Tooltip title="View in ETE Tree">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onTabChange?.(1);
                        }}
                      >
                        <AccountTreeIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default AlignmentsTableETE; 