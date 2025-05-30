import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Divider
} from '@mui/material';
import type { SearchResults } from '../../api/orthologueETEApi';
import PhylogeneticTreeViewETE from './PhylogeneticTreeViewETE';
import SpeciesDistributionChips from '../orthologues/SpeciesDistributionChips';
import AlignmentsTableETE from './AlignmentsTableETE';

// Create a context for species selection
interface SpeciesSelectionContextType {
  selectedSpecies: string | null;
  setSelectedSpecies: (species: string | null) => void;
  activeTab: number;
  setActiveTab: (tab: number) => void;
}

const SpeciesSelectionContext = createContext<SpeciesSelectionContextType>({
  selectedSpecies: null,
  setSelectedSpecies: () => {},
  activeTab: 0,
  setActiveTab: () => {},
});

const useSpeciesSelection = () => useContext(SpeciesSelectionContext);

interface SpeciesSelectionProviderProps {
  children: React.ReactNode;
  activeTab: number;
  setActiveTab: (tab: number) => void;
}

const SpeciesSelectionProvider: React.FC<SpeciesSelectionProviderProps> = ({ children, activeTab, setActiveTab }) => {
  const [selectedSpecies, setSelectedSpecies] = useState<string | null>(null);
  return (
    <SpeciesSelectionContext.Provider value={{ selectedSpecies, setSelectedSpecies, activeTab, setActiveTab }}>
      {children}
    </SpeciesSelectionContext.Provider>
  );
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`orthologue-ete-tabpanel-${index}`}
      aria-labelledby={`orthologue-ete-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

interface OrthologueETEResultsProps {
  results: SearchResults;
}

// Tree View wrapper component using the context
const TreeViewWrapper: React.FC<{ newickData: string, speciesCounts: any[] }> = ({ newickData, speciesCounts }) => {
  const { selectedSpecies, setSelectedSpecies } = useSpeciesSelection();
  const [treeData, setTreeData] = useState<boolean>(false);

  const handleTreeSpeciesSelected = useCallback((speciesName: string | null) => {
    console.log("Species selected from ETE tree:", speciesName);
    setSelectedSpecies(speciesName);
  }, [setSelectedSpecies]);

  return (
    <PhylogeneticTreeViewETE 
      newickData={newickData} 
      speciesCounts={speciesCounts}
      selectedSpecies={selectedSpecies}
      onSpeciesSelected={handleTreeSpeciesSelected}
      onTreeDataLoad={() => setTreeData(true)}
    />
  );
};

const OrthologueETEResults: React.FC<OrthologueETEResultsProps> = ({ results }) => {
  const [activeTab, setActiveTab] = useState<number>(0);
  
  // Handle tab changes
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Convert ETE results to species counts if needed
  const speciesCounts = results.counts_by_species || (results.results?.map(r => ({
    species_name: r.node_name,
    count: r.gene_count || 0
  })) || []);
  
  // Calculate species with orthologues vs total species
  const speciesWithOrthologues = speciesCounts.filter(s => s.count > 0).length;
  const totalSpecies = speciesCounts.length;
  
  // Get the total number of orthologues (either from orthologues array or results array)
  const totalOrthologues = results.orthologues?.length || results.results?.length || 0;

  return (
    <SpeciesSelectionProvider activeTab={activeTab} setActiveTab={setActiveTab}>
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            aria-label="orthologue ETE results tabs"
          >
            <Tab label="Summary" />
            <Tab label="ETE Tree" />
            <Tab label="Alignments" />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <Box>
            <Typography variant="h6" gutterBottom>
              Search Results Summary
            </Typography>
            <TableContainer>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell colSpan={3}>
                      <Typography variant="body2">
                        Total results found: <strong>{totalOrthologues}</strong>
                      </Typography>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={3}>
                      <Typography variant="body2">
                        Species with matches: <strong>{speciesWithOrthologues}</strong> out of <strong>{totalSpecies}</strong> species
                      </Typography>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={3}>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Species Distribution
                      </Typography>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                        Click on a species to highlight it in all views
                      </Typography>
                      <SpeciesDistributionChips 
                        speciesCounts={speciesCounts}
                        selectedSpecies={null}
                        onSpeciesSelected={() => {}}
                        onTabChange={setActiveTab}
                      />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={3}>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="subtitle2">
                        Details
                      </Typography>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Query</TableCell>
                    <TableCell colSpan={2}>
                      {results.gene_id || results.query}
                    </TableCell>
                  </TableRow>
                  {results.orthogroup_id && (
                    <TableRow>
                      <TableCell>Orthogroup</TableCell>
                      <TableCell colSpan={2}>
                        {results.orthogroup_id}
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {results.ete_tree || results.tree_image ? (
            <TreeViewWrapper 
              newickData={results.ete_tree || results.tree_image || ''} 
              speciesCounts={speciesCounts}
            />
          ) : (
            <Typography color="text.secondary">
              No phylogenetic tree data available
            </Typography>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <AlignmentsTableETE 
            orthologues={results.orthologues || results.results || []}
            selectedSpecies={null}
            onSpeciesSelected={() => {}}
            onTabChange={setActiveTab}
          />
        </TabPanel>
      </Box>
    </SpeciesSelectionProvider>
  );
};

export default OrthologueETEResults; 