import React, { useState, useCallback, useRef, useEffect, createContext, useContext } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
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
import {
  Search as SearchIcon,
  Stop as StopIcon,
  Download as DownloadIcon,
  AccountTree as AccountTreeIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  History as HistoryIcon,
  BookmarkBorder as BookmarkIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { chunkedSearchService, ChunkMessage, ChunkData } from '../../services/api/chunkedSearch';
import PhylogeneticTreeView from '../orthologues/PhylogeneticTreeView';
import SpeciesDistributionChips from '../orthologues/SpeciesDistributionChips';
import AlignmentsTable from '../orthologues/AlignmentsTable';

// Add the same SpeciesSelectionContext as explore page
interface SpeciesSelectionContextType {
  selectedSpecies: string | null;
  setSelectedSpecies: (species: string | null) => void;
  activeTab: number;
  setActiveTab: (tab: number) => void;
}

const SpeciesSelectionContext = createContext<SpeciesSelectionContextType | undefined>(undefined);

const useSpeciesSelection = () => {
  const context = useContext(SpeciesSelectionContext);
  if (context === undefined) {
    throw new Error('useSpeciesSelection must be used within a SpeciesSelectionProvider');
  }
  return context;
};

const SpeciesSelectionProvider: React.FC<{ children: React.ReactNode, activeTab: number, setActiveTab: (tab: number) => void }> = ({ 
  children, 
  activeTab,
  setActiveTab 
}) => {
  const [selectedSpecies, setSelectedSpecies] = useState<string | null>(null);

  useEffect(() => {
    console.log("ChunkedSearch SpeciesSelectionContext - selectedSpecies:", selectedSpecies);
  }, [selectedSpecies]);

  const value = { selectedSpecies, setSelectedSpecies, activeTab, setActiveTab };
  return <SpeciesSelectionContext.Provider value={value}>{children}</SpeciesSelectionContext.Provider>;
};

interface SearchResult {
  gene_id: string;
  orthogroup_id: string;
}

const ChunkedGeneSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [filteredResults, setFilteredResults] = useState<SearchResult[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chunkSize, setChunkSize] = useState(50);
  const [streamStats, setStreamStats] = useState({
    chunksReceived: 0,
    totalResults: 0,
    isComplete: false
  });
  const [currentChunkNumber, setCurrentChunkNumber] = useState(1);
  const [selectedGeneForTree, setSelectedGeneForTree] = useState<SearchResult | null>(null);
  const [treeData, setTreeData] = useState<any>(null);
  const [treeLoading, setTreeLoading] = useState(false);
  const [treeProgress, setTreeProgress] = useState(0);
  const [treeActiveTab, setTreeActiveTab] = useState(0);

  // New state for enhanced features
  const [searchHistory, setSearchHistory] = useState<string[]>(() => {
    const saved = localStorage.getItem('geneSearchHistory');
    return saved ? JSON.parse(saved) : [];
  });
  const [savedSearches, setSavedSearches] = useState<{[key: string]: SearchResult[]}>(() => {
    const saved = localStorage.getItem('savedGeneSearches');
    return saved ? JSON.parse(saved) : {};
  });
  const [sortBy, setSortBy] = useState<'relevance' | 'gene_id' | 'orthogroup'>('relevance');
  const [filterText, setFilterText] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const abortControllerRef = useRef<AbortController | null>(null);
  const treeAbortControllerRef = useRef<AbortController | null>(null);

  const handleViewTree = async (result: SearchResult) => {
    setSelectedGeneForTree(result);
    setTreeLoading(true);
    setTreeData(null);
    
    try {
      console.log(`Getting full species tree for: ${result.gene_id}, orthogroup: ${result.orthogroup_id}`);
      
      // Get the same tree data as the main search - full species tree with orthogroup data
      const [orthologueResponse, treeResponse] = await Promise.all([
        // Get the full orthologue data for this gene (same as main search)
        fetch(`/api/orthologue/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ gene_id: result.gene_id })
        }).then(res => res.json()),
        
        // Get the full species tree (same as main search)
        fetch('/api/orthologue/tree').then(res => res.json())
      ]);
      
      if (orthologueResponse.success && treeResponse.success) {
        // Use the same tree structure as main search
        setTreeData({
          success: true,
          newick: treeResponse.newick,                    // Full species tree
          species_counts: orthologueResponse.counts_by_species, // Full species data
          orthologues: orthologueResponse.orthologues,   // Detailed orthologue data for Alignments tab
          total_species: orthologueResponse.counts_by_species.length,
          gene_id: result.gene_id,
          orthogroup_id: result.orthogroup_id,
          is_main_search_tree: true // Flag to indicate this is the same as main search
        });
        console.log('Full species tree loaded (same as main search)');
      } else {
        setError(`Failed to load tree: ${orthologueResponse.message || treeResponse.message}`);
      }
      
    } catch (err) {
      console.error('Error loading tree:', err);
      setError(`Failed to load tree for ${result.gene_id}: ${err}`);
    } finally {
      setTreeLoading(false);
    }
  };

  const handleTreeMessage = useCallback((message: any, allSpecies: any[]) => {
    // Remove this function since we're not using progressive loading anymore
  }, []);

  const handleCloseTree = () => {
    if (treeAbortControllerRef.current) {
      treeAbortControllerRef.current.abort();
    }
    setSelectedGeneForTree(null);
    setTreeData(null);
  };

  const handleStreamMessage = useCallback((message: ChunkMessage) => {
    switch (message.type) {
      case 'metadata':
        console.log('Stream started:', message);
        break;
        
      case 'chunk':
        const chunkData = message as ChunkData;
        setResults(prev => [...prev, ...chunkData.results]);
        setStreamStats(prev => ({
          chunksReceived: prev.chunksReceived + 1,
          totalResults: chunkData.total_sent,
          isComplete: false
        }));
        setCurrentChunkNumber(chunkData.chunk_number);
        console.log(`Chunk ${chunkData.chunk_number}: +${chunkData.count} results`);
        break;
        
      case 'complete':
        setStreamStats(prev => ({
          ...prev,
          isComplete: true
        }));
        console.log('Stream complete:', message);
        break;
    }
  }, []);

  // Enhanced search with history tracking
  const startStreamingSearch = useCallback(async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    // Add to search history
    const newHistory = [query, ...searchHistory.filter(h => h !== query)].slice(0, 10);
    setSearchHistory(newHistory);
    localStorage.setItem('geneSearchHistory', JSON.stringify(newHistory));

    // Reset state
    setResults([]);
    setFilteredResults([]);
    setError(null);
    setIsStreaming(true);
    setStreamStats({ chunksReceived: 0, totalResults: 0, isComplete: false });

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      const stream = chunkedSearchService.streamSearch(query, chunkSize);
      
      for await (const message of stream) {
        // Check if cancelled
        if (abortControllerRef.current?.signal.aborted) {
          break;
        }

        handleStreamMessage(message);
      }
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setError(`Stream error: ${err.message}`);
      }
    } finally {
      setIsStreaming(false);
    }
  }, [query, chunkSize, handleStreamMessage, searchHistory]);

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  }, []);

  const exportResults = useCallback(() => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `gene_search_${query}_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [results, query]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Handle species selection in tree
  const handleTreeSpeciesSelected = (species: string | null) => {
    console.log('Species selected in chunked search tree:', species);
  };

  // Filter and sort results
  useEffect(() => {
    let filtered = [...results];
    
    // Apply text filter
    if (filterText) {
      filtered = filtered.filter(result => 
        result.gene_id.toLowerCase().includes(filterText.toLowerCase()) ||
        result.orthogroup_id.toLowerCase().includes(filterText.toLowerCase())
      );
    }

    // Apply sorting
    switch (sortBy) {
      case 'gene_id':
        filtered.sort((a, b) => a.gene_id.localeCompare(b.gene_id));
        break;
      case 'orthogroup':
        filtered.sort((a, b) => a.orthogroup_id.localeCompare(b.orthogroup_id));
        break;
      case 'relevance':
      default:
        // Keep original order (relevance from search)
        break;
    }

    setFilteredResults(filtered);
  }, [results, filterText, sortBy]);

  // Save current search
  const saveCurrentSearch = useCallback(() => {
    if (query && results.length > 0) {
      const newSaved = { ...savedSearches, [query]: results };
      setSavedSearches(newSaved);
      localStorage.setItem('savedGeneSearches', JSON.stringify(newSaved));
    }
  }, [query, results, savedSearches]);

  // Load saved search
  const loadSavedSearch = useCallback((searchQuery: string) => {
    const savedResults = savedSearches[searchQuery];
    if (savedResults) {
      setQuery(searchQuery);
      setResults(savedResults);
      setStreamStats({
        chunksReceived: Math.ceil(savedResults.length / chunkSize),
        totalResults: savedResults.length,
        isComplete: true
      });
    }
  }, [savedSearches, chunkSize]);

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
      <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
        Gene Search with Streaming Results
      </Typography>
      
      <Typography variant="subtitle1" gutterBottom sx={{ mb: 3 }}>
        Search for gene orthologues with real-time result streaming and comprehensive phylogenetic analysis.
      </Typography>

      {/* Enhanced Search Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, md: 6 }}>
              <Box sx={{ position: 'relative' }}>
                <TextField
                  fullWidth
                  label="Gene Identifier"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={isStreaming}
                  placeholder="Enter gene ID (e.g., AT1G01010, Os01g, Zm00001d)"
                  variant="outlined"
                  InputProps={{
                    endAdornment: (
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton
                          size="small"
                          onClick={() => setShowHistory(!showHistory)}
                          title="Search History"
                        >
                          <HistoryIcon fontSize="small" />
                        </IconButton>
                        {query && results.length > 0 && (
                          <IconButton
                            size="small"
                            onClick={saveCurrentSearch}
                            title="Save Search"
                          >
                            <BookmarkIcon fontSize="small" />
                          </IconButton>
                        )}
                      </Box>
                    )
                  }}
                />
                
                {/* Search History Dropdown */}
                {showHistory && searchHistory.length > 0 && (
                  <Paper sx={{ 
                    position: 'absolute', 
                    top: '100%', 
                    left: 0, 
                    right: 0, 
                    zIndex: 10,
                    maxHeight: 200,
                    overflow: 'auto'
                  }}>
                    <List dense>
                      {searchHistory.map((historyItem, index) => (
                        <ListItem 
                          key={index}
                          sx={{ 
                            cursor: 'pointer',
                            '&:hover': { backgroundColor: 'action.hover' }
                          }}
                          onClick={() => {
                            setQuery(historyItem);
                            setShowHistory(false);
                          }}
                        >
                          <ListItemText primary={historyItem} />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                )}
              </Box>
            </Grid>
            
            <Grid size={{ xs: 6, md: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Results per Chunk</InputLabel>
                <Select
                  value={chunkSize}
                  onChange={(e) => setChunkSize(Number(e.target.value))}
                  disabled={isStreaming}
                  label="Results per Chunk"
                >
                  <MenuItem value={10}>10 results</MenuItem>
                  <MenuItem value={25}>25 results</MenuItem>
                  <MenuItem value={50}>50 results</MenuItem>
                  <MenuItem value={100}>100 results</MenuItem>
                  <MenuItem value={200}>200 results</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid size={{ xs: 6, md: 2 }}>
              <Button
                variant="outlined"
                onClick={() => setShowAdvanced(!showAdvanced)}
                startIcon={<FilterIcon />}
                fullWidth
                size="small"
              >
                {showAdvanced ? 'Hide' : 'Show'} Filters
              </Button>
            </Grid>
            
            <Grid size={{ xs: 12, md: 2 }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={isStreaming ? <StopIcon /> : <SearchIcon />}
                  onClick={isStreaming ? stopStream : startStreamingSearch}
                  color={isStreaming ? "error" : "primary"}
                  fullWidth
                >
                  {isStreaming ? 'Stop Search' : 'Search'}
                </Button>
              </Box>
            </Grid>
          </Grid>

          {/* Advanced Filters */}
          {showAdvanced && (
            <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Filter Results"
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    placeholder="Filter by gene ID or orthogroup"
                    InputProps={{
                      startAdornment: <FilterIcon sx={{ mr: 1, color: 'action.active' }} />
                    }}
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 3 }}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Sort By</InputLabel>
                    <Select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as any)}
                      label="Sort By"
                      startAdornment={<SortIcon sx={{ mr: 1, color: 'action.active' }} />}
                    >
                      <MenuItem value="relevance">Relevance</MenuItem>
                      <MenuItem value="gene_id">Gene ID</MenuItem>
                      <MenuItem value="orthogroup">Orthogroup</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid size={{ xs: 12, md: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    Showing {filteredResults.length} of {results.length} results
                  </Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 2 }}>
                  <Button
                    size="small"
                    startIcon={<RefreshIcon />}
                    onClick={() => {
                      setFilterText('');
                      setSortBy('relevance');
                    }}
                  >
                    Reset
                  </Button>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Saved Searches */}
          {Object.keys(savedSearches).length > 0 && (
            <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle2" gutterBottom>
                Saved Searches:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {Object.keys(savedSearches).map(savedQuery => (
                  <Chip
                    key={savedQuery}
                    label={`${savedQuery} (${savedSearches[savedQuery].length})`}
                    size="small"
                    onClick={() => loadSavedSearch(savedQuery)}
                    color="secondary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Stream Status */}
      {isStreaming && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress sx={{ height: 8, borderRadius: 4 }} />
          <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
            Processing search results... Chunks: {streamStats.chunksReceived} | Results: {streamStats.totalResults.toLocaleString()}
          </Typography>
        </Box>
      )}

      {/* Results Summary */}
      {results.length > 0 && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h6">
                  Search Results Summary
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                  <Chip 
                    label={`${results.length.toLocaleString()} orthologues found`} 
                    color="primary" 
                    size="small"
                  />
                  <Chip 
                    label={`${streamStats.chunksReceived} data chunks`} 
                    color="secondary" 
                    size="small"
                  />
                  {streamStats.isComplete ? (
                    <Chip 
                      label="Search Complete" 
                      color="success" 
                      size="small"
                    />
                  ) : (
                    <Chip 
                      label="Processing..." 
                      color="info" 
                      size="small"
                    />
                  )}
                </Box>
                {!streamStats.isComplete && results.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Additional results are being processed...
                    </Typography>
                  </Box>
                )}
              </Box>
              
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={exportResults}
                  variant="outlined"
                  disabled={results.length === 0}
                >
                  Export Data
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Enhanced Results List */}
      {filteredResults.length > 0 && (
        <Paper sx={{ 
          maxHeight: 600, 
          overflow: 'auto',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#f1f1f1',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#c1c1c1',
            borderRadius: '4px',
            '&:hover': {
              background: '#a8a8a8',
            },
          },
        }}>
          {/* Sticky header with result count */}
          <Box sx={{ 
            position: 'sticky', 
            top: 0, 
            bgcolor: 'background.paper', 
            borderBottom: 1, 
            borderColor: 'divider',
            p: 1,
            zIndex: 1
          }}>
            <Typography variant="body2" color="text.secondary">
              {filteredResults.length} results {filterText && `(filtered from ${results.length})`}
              {sortBy !== 'relevance' && ` • Sorted by ${sortBy.replace('_', ' ')}`}
            </Typography>
          </Box>
          
          <List dense sx={{ pb: 0 }}>
            {filteredResults.map((result, index) => (
              <ListItem 
                key={`${result.gene_id}-${index}`}
                divider
                sx={{ 
                  '&:hover': { backgroundColor: 'action.hover' },
                  opacity: index < results.length - chunkSize ? 0.8 : 1,
                  transition: 'all 0.2s ease-in-out',
                  borderLeft: index >= results.length - chunkSize ? '3px solid' : 'none',
                  borderLeftColor: 'success.main',
                  pl: index >= results.length - chunkSize ? 2 : 2,
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontFamily: 'monospace', 
                          fontWeight: 'bold',
                          fontSize: { xs: '0.9rem', md: '1rem' }
                        }}
                      >
                        {result.gene_id}
                      </Typography>
                      {index >= results.length - chunkSize && (
                        <Chip 
                          label="NEW" 
                          size="small" 
                          color="success" 
                          sx={{ 
                            height: 20,
                            fontSize: '0.7rem',
                            animation: 'pulse 2s infinite'
                          }} 
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Orthogroup: {result.orthogroup_id}
                      </Typography>
                      <Typography variant="caption" color="text.disabled">
                        Result #{results.findIndex(r => r.gene_id === result.gene_id) + 1}
                      </Typography>
                    </Box>
                  }
                />
                <IconButton
                  size="medium"
                  onClick={() => handleViewTree(result)}
                  sx={{ 
                    color: 'success.main',
                    '&:hover': { 
                      backgroundColor: 'success.light',
                      color: 'success.dark',
                      transform: 'scale(1.1)'
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  <Tooltip title="View Phylogenetic Tree" placement="top">
                    <AccountTreeIcon />
                  </Tooltip>
                </IconButton>
              </ListItem>
            ))}
          </List>
          
          {/* Load more indicator for large datasets */}
          {filteredResults.length > 100 && (
            <Box sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.50' }}>
              <Typography variant="caption" color="text.secondary">
                Showing {filteredResults.length} results. Use filters to refine your search.
              </Typography>
            </Box>
          )}
        </Paper>
      )}

      {/* Empty State */}
      {!isStreaming && results.length === 0 && !error && (
        <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: 'grey.50' }}>
          <Typography variant="h6" color="text.secondary">
            Ready to Search
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Enter a gene identifier to search for orthologues across all species in the database.
          </Typography>
        </Paper>
      )}

      {/* Enhanced Tree Dialog - Same as Explore */}
      {selectedGeneForTree && (
        <Dialog 
          open={!!selectedGeneForTree} 
          onClose={handleCloseTree}
          maxWidth="xl"
          fullWidth
          sx={{ '& .MuiDialog-paper': { height: '90vh' } }}
        >
          <DialogTitle>
            Phylogenetic Analysis - {selectedGeneForTree.gene_id}
            <Chip 
              label={`Orthogroup: ${selectedGeneForTree.orthogroup_id}`} 
              size="small" 
              color="primary"
              sx={{ ml: 1 }} 
            />
            {treeData && (
              <Chip 
                label={`${treeData.total_species} species • ${treeData.species_counts?.filter((s: any) => s.count > 0).length || 0} with orthologues`}
                size="small" 
                color="info"
                sx={{ ml: 1 }} 
              />
            )}
            <IconButton
              size="small"
              onClick={handleCloseTree}
              sx={{ position: 'absolute', right: 8, top: 8 }}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </DialogTitle>
          
          <DialogContent sx={{ p: 0, height: '100%' }}>
            {treeData && treeData.success && treeData.newick ? (
              <SpeciesSelectionProvider activeTab={treeActiveTab} setActiveTab={setTreeActiveTab}>
                <Box sx={{ width: '100%', height: '100%' }}>
                  {/* Tabs */}
                  <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs 
                      value={treeActiveTab} 
                      onChange={(_, newValue) => setTreeActiveTab(newValue)}
                      aria-label="phylogenetic analysis tabs"
                    >
                      <Tab label="Summary" />
                      <Tab label="Phylogenetic Tree" />
                      <Tab label="Sequence Alignments" />
                    </Tabs>
                  </Box>

                  <SummaryTabContent 
                    activeTab={treeActiveTab}
                    treeData={treeData}
                    selectedGeneForTree={selectedGeneForTree}
                  />

                  <TreeTabContent 
                    activeTab={treeActiveTab}
                    treeData={treeData}
                  />

                  <AlignmentsTabContent 
                    activeTab={treeActiveTab}
                    treeData={treeData}
                  />
                </Box>
              </SpeciesSelectionProvider>
            ) : treeLoading ? (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <LinearProgress 
                  variant="indeterminate"
                  sx={{ mb: 3, height: 8, borderRadius: 4 }}
                />
                <Typography variant="h6" gutterBottom>
                  Loading Phylogenetic Data...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Retrieving evolutionary relationships for {selectedGeneForTree.gene_id}
                </Typography>
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Alert severity="info">
                  <Typography variant="h6" gutterBottom>
                    Preparing Phylogenetic Analysis...
                  </Typography>
                  <Typography variant="body2">
                    Loading comprehensive orthologue data for {selectedGeneForTree.gene_id}
                  </Typography>
                </Alert>
              </Box>
            )}
          </DialogContent>
          
          <DialogActions sx={{ p: 2, gap: 1 }}>
            <Button onClick={handleCloseTree} variant="outlined">
              Close
            </Button>
            {treeData && (
              <Chip 
                label={`Comprehensive phylogenetic analysis`}
                size="small" 
                color="success"
              />
            )}
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

// Tab Panel component (same as explore page)
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
      id={`tree-tabpanel-${index}`}
      aria-labelledby={`tree-tab-${index}`}
      {...other}
    >
      {value === index && children}
    </div>
  );
};

// Summary tab content (Tab 0)
const SummaryTabContent: React.FC<{ 
  activeTab: number, 
  treeData: any,
  selectedGeneForTree: SearchResult
}> = ({ activeTab, treeData, selectedGeneForTree }) => {
  const { selectedSpecies, setSelectedSpecies, setActiveTab } = useSpeciesSelection();
  
  return (
    <TabPanel value={activeTab} index={0}>
      <Box sx={{ p: 3, height: 'calc(100% - 48px)', overflow: 'auto' }}>
        <TableContainer sx={{ maxHeight: '400px' }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell colSpan={3}>
                  <Typography variant="subtitle1">
                    Orthologue Distribution Analysis
                  </Typography>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell colSpan={3}>
                  <Typography variant="body2">
                    Total species in phylogeny: <strong>{treeData.total_species}</strong>
                  </Typography>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell colSpan={3}>
                  <Typography variant="body2">
                    Species with orthologues: <strong>{treeData.species_counts?.filter((s: any) => s.count > 0).length || 0}</strong> of <strong>{treeData.total_species}</strong>
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
                    Select a species to highlight across all analyses
                  </Typography>
                  <SpeciesDistributionChips 
                    speciesCounts={treeData.species_counts || []}
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
                    Analysis Details
                  </Typography>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Query Gene</TableCell>
                <TableCell colSpan={2}>
                  <Chip label={treeData.gene_id} size="small" />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Orthogroup</TableCell>
                <TableCell colSpan={2}>
                  <Chip label={treeData.orthogroup_id} size="small" color="primary" />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Analysis Type</TableCell>
                <TableCell colSpan={2}>
                  <Chip label="Complete Phylogenetic Analysis" size="small" color="success" />
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
        
        {selectedSpecies && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Selected species: <strong>{selectedSpecies}</strong> - View in Phylogenetic Tree tab for detailed positioning
          </Alert>
        )}
      </Box>
    </TabPanel>
  );
};

// Tree tab content (Tab 1)
const TreeTabContent: React.FC<{ 
  activeTab: number, 
  treeData: any 
}> = ({ activeTab, treeData }) => {
  const { selectedSpecies, setSelectedSpecies } = useSpeciesSelection();
  
  return (
    <TabPanel value={activeTab} index={1}>
      <Box sx={{ 
        height: 'calc(100% - 48px)', 
        width: '100%', 
        position: 'relative',
        bgcolor: 'background.paper',
        p: 1
      }}>
        <PhylogeneticTreeView
          newickData={treeData.newick}
          speciesCounts={treeData.species_counts || []}
          selectedSpecies={selectedSpecies}
          onSpeciesSelected={setSelectedSpecies}
          onTreeDataLoad={(loaded) => console.log('Phylogenetic tree loaded:', loaded)}
        />
      </Box>
    </TabPanel>
  );
};

// Alignments tab content (Tab 2)
const AlignmentsTabContent: React.FC<{ 
  activeTab: number, 
  treeData: any 
}> = ({ activeTab, treeData }) => {
  const { selectedSpecies, setSelectedSpecies, setActiveTab } = useSpeciesSelection();
  
  return (
    <TabPanel value={activeTab} index={2}>
      <Box sx={{ p: 3, height: 'calc(100% - 48px)', overflow: 'auto' }}>
        {treeData && treeData.orthologues ? (
          <AlignmentsTable
            orthologues={treeData.orthologues}
            selectedSpecies={selectedSpecies}
            onSpeciesSelected={setSelectedSpecies}
            onTabChange={setActiveTab}
          />
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary">
              Loading Sequence Alignment Data...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Retrieving detailed orthologue sequences for {treeData.gene_id}
            </Typography>
          </Box>
        )}
      </Box>
    </TabPanel>
  );
};

export default ChunkedGeneSearch; 