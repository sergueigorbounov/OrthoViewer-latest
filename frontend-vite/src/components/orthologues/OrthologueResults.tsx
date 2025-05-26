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
import type { SearchResults } from '../../api/orthologueApi';
import PhylogeneticTreeView from './PhylogeneticTreeView';
import SpeciesDistributionChips from './SpeciesDistributionChips';
import AlignmentsTable from './AlignmentsTable';

// Create a context for species selection to improve synchronization
interface SpeciesSelectionContextType {
  selectedSpecies: string | null;
  setSelectedSpecies: (species: string | null) => void;
  activeTab: number;
  setActiveTab: (tab: number) => void;
}

const SpeciesSelectionContext = createContext<SpeciesSelectionContextType | undefined>(undefined);

// Create a hook to use the species selection context
const useSpeciesSelection = () => {
  const context = useContext(SpeciesSelectionContext);
  if (context === undefined) {
    throw new Error('useSpeciesSelection must be used within a SpeciesSelectionProvider');
  }
  return context;
};

// Create a provider component for the species selection context
const SpeciesSelectionProvider: React.FC<{ children: React.ReactNode, activeTab: number, setActiveTab: (tab: number) => void }> = ({ 
  children, 
  activeTab,
  setActiveTab 
}) => {
  const [selectedSpecies, setSelectedSpecies] = useState<string | null>(null);

  // Log when selectedSpecies changes for debugging
  useEffect(() => {
    console.log("SpeciesSelectionContext - selectedSpecies state:", selectedSpecies);
  }, [selectedSpecies]);

  const value = { selectedSpecies, setSelectedSpecies, activeTab, setActiveTab };
  return <SpeciesSelectionContext.Provider value={value}>{children}</SpeciesSelectionContext.Provider>;
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
      id={`orthologue-tabpanel-${index}`}
      aria-labelledby={`orthologue-tab-${index}`}
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

interface OrthologueResultsProps {
  results: SearchResults;
}

// Tree View wrapper component using the context
const TreeViewWrapper: React.FC<{ newickData: string, speciesCounts: any[] }> = ({ newickData, speciesCounts }) => {
  const { selectedSpecies, setSelectedSpecies } = useSpeciesSelection();
  const [treeData, setTreeData] = useState<boolean>(false);

  const handleTreeSpeciesSelected = useCallback((speciesName: string | null) => {
    console.log("Species selected from tree:", speciesName);
    setSelectedSpecies(speciesName);
  }, [setSelectedSpecies]);

  return (
    <PhylogeneticTreeView 
      newickData={newickData} 
      speciesCounts={speciesCounts}
      selectedSpecies={selectedSpecies}
      onSpeciesSelected={handleTreeSpeciesSelected}
      onTreeDataLoad={() => setTreeData(true)}
    />
  );
};

const OrthologueResults: React.FC<OrthologueResultsProps> = ({ results }) => {
  const [activeTab, setActiveTab] = useState<number>(0);
  
  // Handle tab changes
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Calculate species with orthologues vs total species
  const speciesWithOrthologues = results.counts_by_species.filter(s => s.count > 0).length;
  const totalSpecies = results.counts_by_species.length;
  
  // Get the total number of orthologues (count of items in the array)
  const totalOrthologues = results.orthologues.length;

  return (
    <SpeciesSelectionProvider activeTab={activeTab} setActiveTab={setActiveTab}>
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            aria-label="orthologue results tabs"
          >
            <Tab label="Summary" />
            <Tab label="Tree" />
            <Tab label="Alignments" />
          </Tabs>
        </Box>

        <SummaryTabContent 
          activeTab={activeTab} 
          results={results} 
          totalOrthologues={totalOrthologues}
          speciesWithOrthologues={speciesWithOrthologues}
          totalSpecies={totalSpecies}
        />

        <TreeTabContent 
          activeTab={activeTab} 
          results={results} 
        />

        <AlignmentsTabContent 
          activeTab={activeTab} 
          results={results} 
        />
      </Box>
    </SpeciesSelectionProvider>
  );
};

// Summary tab content (Tab 0)
const SummaryTabContent: React.FC<{ 
  activeTab: number, 
  results: SearchResults,
  totalOrthologues: number,
  speciesWithOrthologues: number,
  totalSpecies: number
}> = ({ activeTab, results, totalOrthologues, speciesWithOrthologues, totalSpecies }) => {
  const { selectedSpecies, setSelectedSpecies, setActiveTab } = useSpeciesSelection();
  
  return (
    <TabPanel value={activeTab} index={0}>
      <TableContainer sx={{ maxHeight: '500px' }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell colSpan={3}>
                <Typography variant="subtitle1">
                  Summary of Orthologues
                </Typography>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell colSpan={3}>
                <Typography variant="body2">
                  Total orthologues found: <strong>{totalOrthologues}</strong>
                </Typography>
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell colSpan={3}>
                <Typography variant="body2">
                  Species with orthologues: <strong>{speciesWithOrthologues}</strong> out of <strong>{totalSpecies}</strong> species
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
                  speciesCounts={results.counts_by_species}
                  selectedSpecies={selectedSpecies}
                  onSpeciesSelected={setSelectedSpecies}
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
              <TableCell>Query Gene</TableCell>
              <TableCell colSpan={2}>
                {results.gene_id}
              </TableCell>
            </TableRow>
            {results.orthogroup_id && (
              <TableRow>
                <TableCell>Orthogroup</TableCell>
                <TableCell colSpan={2}>{results.orthogroup_id}</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <Typography variant="caption" color="textSecondary" sx={{ display: 'none' }}>
        Selected species: {selectedSpecies || 'none'}
      </Typography>
    </TabPanel>
  );
};

// Tree tab content (Tab 1)
const TreeTabContent: React.FC<{ 
  activeTab: number, 
  results: SearchResults 
}> = ({ activeTab, results }) => {
  const { selectedSpecies } = useSpeciesSelection();
  
  return (
    <TabPanel value={activeTab} index={1}>
      <Box sx={{ 
        height: '600px', 
        width: '100%', 
        position: 'relative',
        bgcolor: 'background.paper',
        boxShadow: 1,
        borderRadius: 1,
        p: 1
      }}>
        {results.newick_tree ? (
          <TreeViewWrapper 
            newickData={results.newick_tree}
            speciesCounts={results.counts_by_species}
            key={`tree-view-${activeTab}-${selectedSpecies || 'none'}`}
          />
        ) : (
          <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography>No phylogenetic tree data available</Typography>
          </Box>
        )}
      </Box>
    </TabPanel>
  );
};

// Alignments tab content (Tab 2)
const AlignmentsTabContent: React.FC<{ 
  activeTab: number, 
  results: SearchResults 
}> = ({ activeTab, results }) => {
  const { selectedSpecies, setSelectedSpecies, setActiveTab } = useSpeciesSelection();
  
  return (
    <TabPanel value={activeTab} index={2}>
      <AlignmentsTable 
        orthologues={results.orthologues}
        selectedSpecies={selectedSpecies}
        onSpeciesSelected={setSelectedSpecies}
        onTabChange={setActiveTab}
      />
    </TabPanel>
  );
};

export default OrthologueResults;