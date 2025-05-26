import React, { useCallback, useMemo } from 'react';
import { Box, Chip } from '@mui/material';
import type { SpeciesCountData } from '../../api/orthologueApi';

interface SpeciesDistributionChipsProps {
  speciesCounts: SpeciesCountData[];
  selectedSpecies: string | null;
  onSpeciesSelected: (species: string | null) => void;
  onTabChange?: (tabIndex: number) => void;
}

const SpeciesDistributionChips: React.FC<SpeciesDistributionChipsProps> = ({
  speciesCounts,
  selectedSpecies,
  onSpeciesSelected,
  onTabChange
}) => {
  // Create a function to check if a species is selected - FIXED VERSION
  const isSpeciesSelected = useCallback((speciesName: string): boolean => {
    if (!selectedSpecies || !speciesName) return false;
    
    // For strict matching, we'll only use exact matching (case-insensitive)
    const normalized1 = speciesName.toLowerCase().trim();
    const normalized2 = selectedSpecies.toLowerCase().trim();
    
    // Only return true for an exact match
    return normalized1 === normalized2;
    
  }, [selectedSpecies]);

  const handleSpeciesClick = useCallback((species: string) => {
    console.log(`Species chip clicked: ${species}`);
    
    // Toggle selection - if already selected, clear it; otherwise set the new species
    if (selectedSpecies === species) {
      onSpeciesSelected(null);
    } else {
      onSpeciesSelected(species);
      // Navigate to tree tab when selecting a species
      if (onTabChange) {
        console.log("Navigating to tree tab after species selection");
        onTabChange(1); // Switch to Tree tab
      }
    }
  }, [selectedSpecies, onSpeciesSelected, onTabChange]);

  // Memoize the filtered and sorted species to avoid recalculation on each render
  const processedSpecies = useMemo(() => {
    // Create a map to deduplicate species with the same name
    const uniqueSpeciesMap = new Map();

    // Process all species, combining counts for duplicates
    speciesCounts
      .filter(s => s.count > 0)
      .forEach(species => {
        const name = species.species_name || species.species_id;

        if (uniqueSpeciesMap.has(name)) {
          // If we already have this species, add the count
          const existing = uniqueSpeciesMap.get(name);
          existing.count += species.count;
        } else {
          // Otherwise, add it to the map
          uniqueSpeciesMap.set(name, {...species});
        }
      });

    // Convert back to array and sort by count
    return Array.from(uniqueSpeciesMap.values())
      .sort((a, b) => b.count - a.count);
  }, [speciesCounts]);

  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, maxHeight: '400px', overflow: 'auto' }}>
      {processedSpecies.map((species, index) => {
        // Always use the full species name
        const speciesName = species.species_name || species.species_id;
        const displayName = speciesName.length > 30 ? 
          `${speciesName.substring(0, 27)}...` : 
          speciesName;
        
        // Determine if this species is selected
        const isSelected = isSpeciesSelected(speciesName);
        
        // Create a truly unique key using both the index and the species ID
        const uniqueKey = `species-${species.species_id}-${index}`;
        
        return (
          <Chip
            key={uniqueKey}
            label={`${displayName} (${species.count})`}
            size="small"
            onClick={() => handleSpeciesClick(speciesName)}
            color={isSelected ? "primary" : "default"}
            variant={isSelected ? "filled" : "outlined"}
            sx={{ 
              cursor: 'pointer',
              '&:hover': { backgroundColor: '#e3f2fd' }
            }}
            title={`${speciesName} (${species.count} orthologues)`}
          />
        );
      })}
    </Box>
  );
};

export default SpeciesDistributionChips;