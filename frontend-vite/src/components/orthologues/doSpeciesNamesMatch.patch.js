// Helper function to check if two species names match
const doSpeciesNamesMatch = useCallback((name1: string, name2: string): boolean => {
  if (!name1 || !name2) return false;
  
  const normalized1 = name1.toLowerCase().trim();
  const normalized2 = name2.toLowerCase().trim();
  
  // Direct match - primary matching method for strict selection
  if (normalized1 === normalized2) return true;
  
  // For tree visualization, we still need some flexibility to match species
  // in the tree with those in the data, so we'll keep some broader matching
  // but with higher threshold requirements
  
  // Check if full name exactly contains the other (for species variants)
  // E.g. "Brassica napus" should match "Brassica napus (variant BnA)"
  const containsExact = normalized1.includes(normalized2) || normalized2.includes(normalized1);
  if (containsExact && (normalized1.length > 5 || normalized2.length > 5)) {
    return true;
  }
  
  // Try genus matching for tree nodes which often use abbreviated names
  const genus1 = normalized1.split(/[\s_]/)[0];
  const genus2 = normalized2.split(/[\s_]/)[0];
  
  // Only match by genus if the genus is substantial (not 1-2 letter codes)
  // and the species IDs look similar
  if (genus1 === genus2 && genus1.length > 3) {
    // Additional check - the species parts should have some similarity
    const species1 = normalized1.substring(genus1.length).trim();
    const species2 = normalized2.substring(genus2.length).trim();
    
    // If either species part is empty, or they share first 3 letters when substantial
    if (!species1 || !species2 || 
        (species1.length > 3 && species2.length > 3 && 
         species1.substring(0, 3) === species2.substring(0, 3))) {
      return true;
    }
  }
  
  return false;
}, []);