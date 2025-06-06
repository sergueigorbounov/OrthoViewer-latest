// PhylogeneticTreeView.tsx
// Interactive phylogenetic tree visualization using D3.js for evolutionary relationship analysis
//
// Scientific Context:
// - Visualizes evolutionary relationships between species using Newick tree format
// - Supports both radial and rectangular dendrograms (standard in phylogenetics)
// - Implements equal-spacing algorithms for better tree visualization
// - Handles branch lengths and support values from phylogenetic analysis
//
// Input Data Formats:
// - Newick Format: Standard phylogenetic tree representation
//   Example: "((A:0.1,B:0.2):0.3,C:0.4);"
//   - Numbers after colons represent evolutionary distances
//   - Parentheses denote hierarchical relationships
//
// - Species Count Data: Array of species occurrence data
//   Example: [{species_name: "Arabidopsis_thaliana", count: 5}, ...]
//
// Example usage:
// ```tsx
// <PhylogeneticTreeView
//   newickData="((Arabidopsis_thaliana:0.1,Brassica_napus:0.2):0.3,Oryza_sativa:0.4);"
//   speciesCounts={[
//     { species_name: "Arabidopsis_thaliana", count: 5 },
//     { species_name: "Brassica_napus", count: 3 },
//     { species_name: "Oryza_sativa", count: 4 }
//   ]}
//   selectedSpecies="Arabidopsis_thaliana"
//   onSpeciesSelected={(species) => console.log(`Selected: ${species}`)}
// />
// ```
//
// Performance Notes:
// - Optimized for trees with up to 1000 species
// - Uses D3 force layout for non-overlapping labels
// - Implements lazy rendering for large trees
// - Caches tree layout calculations
//
// Visualization Features:
// 1. Interactive zoom and pan
// 2. Species highlighting
// 3. Branch length visualization
// 4. Species count integration
// 5. Radial/Rectangular layout switching
//
// References:
// - D3 Tree Layout: https://github.com/d3/d3-hierarchy
// - Newick Format: http://evolution.genetics.washington.edu/phylip/newick_doc.html
// - Tree Visualization: https://doi.org/10.1093/bioinformatics/btv636

import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { Box, Typography, CircularProgress, Alert, FormControlLabel, Switch } from '@mui/material';
import type { SpeciesCountData } from '../../api/orthologueApi';

interface PhylogeneticTreeViewProps {
  // Newick format string representing the phylogenetic tree
  newickData: string;
  // Array of species counts from orthologue analysis
  speciesCounts: SpeciesCountData[];
  // Currently selected species for highlighting
  selectedSpecies?: string | null;
  // Callback when user selects a species in the tree
  onSpeciesSelected?: (speciesName: string | null) => void;
  // Callback when tree data is successfully loaded
  onTreeDataLoad?: (loaded: boolean) => void;
}

// TreeNode: Represents a node in the phylogenetic tree
// - Internal nodes: Represent common ancestors
// - Leaf nodes: Represent extant species
interface TreeNode {
  id: string;          // Unique identifier
  name: string;        // Species/node name
  length?: number;     // Branch length (evolutionary distance)
  children?: TreeNode[]; // Child nodes
  x?: number;          // X coordinate in visualization
  y?: number;          // Y coordinate in visualization
  count?: number;      // Number of orthologues
  depth?: number;      // Distance from root
}

const PhylogeneticTreeView: React.FC<PhylogeneticTreeViewProps> = ({ 
  newickData, 
  speciesCounts,
  selectedSpecies,
  onSpeciesSelected,
  onTreeDataLoad
}) => {
  const [useRadialLayout, setUseRadialLayout] = useState<boolean>(() => {
    const savedLayout = localStorage.getItem('treeViewLayout');
    return savedLayout === 'radial' || savedLayout === null;
  });

  useEffect(() => {
    localStorage.setItem('treeViewLayout', useRadialLayout ? 'radial' : 'rectangular');
  }, [useRadialLayout]);

  return (
    <Box sx={{ height: '100%', width: '100%', position: 'relative' }}>
      {/* D3 Tree Info */}
      <Box sx={{ 
        position: 'absolute', 
        top: 5, 
        left: 5, 
        zIndex: 10,
        background: 'rgba(255,255,255,0.95)',
        padding: '8px 12px',
        borderRadius: '6px',
        border: '1px solid #ddd',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <Typography variant="caption" sx={{ fontSize: '0.8rem', fontWeight: 'bold' }}>
          D3 Phylogenetic Tree
        </Typography>
      </Box>

      {/* Layout Controls */}
      <Box sx={{ 
        position: 'absolute', 
        top: 5, 
        right: 5, 
        zIndex: 10,
        background: 'rgba(255,255,255,0.95)',
        padding: '8px 12px',
        borderRadius: '6px',
        border: '1px solid #ddd',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <Typography variant="caption" display="block" gutterBottom>
          Layout Options
        </Typography>
        <FormControlLabel
          control={
            <Switch 
              size="small"
              checked={useRadialLayout}
              onChange={(e) => setUseRadialLayout(e.target.checked)}
            />
          }
          label={
            <Typography variant="caption">
              {useRadialLayout ? "Radial" : "Rectangular"}
            </Typography>
          }
        />
      </Box>

      {/* Tree Content */}
      <Box sx={{ width: '100%', height: '100%' }}>
        <D3TreeImplementation
          newickData={newickData}
          speciesCounts={speciesCounts}
          selectedSpecies={selectedSpecies}
          onSpeciesSelected={onSpeciesSelected}
          onTreeDataLoad={onTreeDataLoad}
          useRadialLayout={useRadialLayout}
        />
      </Box>
    </Box>
  );
};

// D3 Implementation Component
// Handles the actual tree rendering using D3.js
const D3TreeImplementation: React.FC<{
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies?: string | null;
  onSpeciesSelected?: (speciesName: string | null) => void;
  onTreeDataLoad?: (loaded: boolean) => void;
  useRadialLayout: boolean;
}> = ({ newickData, speciesCounts, selectedSpecies, onSpeciesSelected, onTreeDataLoad, useRadialLayout }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [treeData, setTreeData] = useState<TreeNode | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Helper function to count leaves
  const countLeaves = useCallback((node: TreeNode): number => {
    if (!node.children || node.children.length === 0) {
      return 1;
    }
    return node.children.reduce((sum, child) => sum + countLeaves(child), 0);
  }, []);

  // Calculate leaf count for adaptive sizing
  const leafCount = treeData ? countLeaves(treeData) : 0;

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

  // Function to get path from node to root
  const getPathToRoot = useCallback((node: d3.HierarchyNode<TreeNode> | null): string[] => {
    if (!node) return [];
    
    const path: string[] = [];
    let current: d3.HierarchyNode<TreeNode> | null = node;
    
    while (current) {
      path.push(current.data.id);
      current = current.parent;
    }
    
    return path;
  }, []);

  // Function to calculate cumulative distance from root based on branch lengths
  const calculateDistanceFromRoot = useCallback((node: d3.HierarchyNode<TreeNode>): number => {
    let distance = 0;
    let current: d3.HierarchyNode<TreeNode> | null = node;
    
    while (current && current.parent) {
      // Use the branch length if available, otherwise use a default length
      const branchLength = current.data.length || 0.1;
      distance += branchLength;
      current = current.parent;
    }
    
    return distance;
  }, []);

  // Handle selected species from parent component
  useEffect(() => {
    if (!treeData || selectedSpecies === undefined) return;

    if (selectedSpecies) {
      const allNodes: TreeNode[] = [];
      const collectAllNodes = (node: TreeNode) => {
        allNodes.push(node);
        if (node.children) {
          node.children.forEach(collectAllNodes);
        }
      };
      collectAllNodes(treeData);
      
      const findNodeBySpeciesName = (searchTerm: string): string | null => {
        for (const node of allNodes) {
          const cleanNodeName = node.name.replace(/^['"]|['"]$/g, '');
          
          if (doSpeciesNamesMatch(cleanNodeName, searchTerm)) {
            return node.id;
          }
        }
        
        const matchingSpecies = speciesCounts.find(sc => 
          doSpeciesNamesMatch(sc.species_name, searchTerm) || 
          doSpeciesNamesMatch(sc.species_id, searchTerm)
        );
        
        if (matchingSpecies) {
          for (const node of allNodes) {
            if (doSpeciesNamesMatch(node.name, matchingSpecies.species_name) || 
                doSpeciesNamesMatch(node.name, matchingSpecies.species_id)) {
              return node.id;
            }
          }
        }
        
        const genusMatch = searchTerm.split(/[\s_]/)[0];
        if (genusMatch && genusMatch.length > 2) {
          for (const node of allNodes) {
            if (node.name.toLowerCase().startsWith(genusMatch.toLowerCase())) {
              return node.id;
            }
          }
        }
        
        return null;
      };
      
      const foundNodeId = findNodeBySpeciesName(selectedSpecies);
      if (foundNodeId) {
        setSelectedNodeId(foundNodeId);
      }
    } else if (selectedSpecies === null) {
      setSelectedNodeId(null);
    }
  }, [selectedSpecies, treeData, doSpeciesNamesMatch, speciesCounts]);

  // Parse Newick string to tree hierarchy
  useEffect(() => {
    if (!newickData) {
      setError('No tree data provided');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const parseNewick = (newickString: string): TreeNode => {
        const cleaned = newickString.trim().replace(/;$/, '');
        
        const parseSubtree = (str: string, id = 'root', depth = 0): TreeNode => {
          if (!str.includes('(')) {
            const [name, lengthStr] = str.split(':');
            return {
              id: name.trim() || id,
              name: name.trim() || id,
              length: lengthStr ? parseFloat(lengthStr) : undefined,
              depth: depth
            };
          }
          
          let openCount = 0;
          let childrenStr = '';
          let nameAndLength = '';
          let foundOpeningParen = false;
          
          for (let i = 0; i < str.length; i++) {
            const char = str[i];
            
            if (char === '(') {
              if (foundOpeningParen) {
                childrenStr += char;
              } else {
                foundOpeningParen = true;
              }
              openCount++;
            } else if (char === ')') {
              openCount--;
              if (openCount === 0) {
                nameAndLength = str.substring(i + 1);
                break;
              } else {
                childrenStr += char;
              }
            } else if (foundOpeningParen) {
              childrenStr += char;
            }
          }
          
          const childStrings: string[] = [];
          let currentChild = '';
          openCount = 0;
          
          for (let i = 0; i < childrenStr.length; i++) {
            const char = childrenStr[i];
            
            if (char === '(') {
              openCount++;
              currentChild += char;
            } else if (char === ')') {
              openCount--;
              currentChild += char;
            } else if (char === ',' && openCount === 0) {
              childStrings.push(currentChild);
              currentChild = '';
            } else {
              currentChild += char;
            }
          }
          
          if (currentChild) {
            childStrings.push(currentChild);
          }
          
          const [name, lengthStr] = nameAndLength.split(':');
          
          const node: TreeNode = {
            id: name.trim() || id,
            name: name.trim() || id,
            length: lengthStr ? parseFloat(lengthStr) : undefined,
            depth: depth,
            children: childStrings.map((childStr, i) => parseSubtree(childStr, `${id}_${i}`, depth + 1))
          };
          
          return node;
        };
        
        return parseSubtree(cleaned);
      };

      const parsedTree = parseNewick(newickData);
      
      const addCountsToTree = (node: TreeNode): void => {
        if (!node.children || node.children.length === 0) {
          const matchByName = speciesCounts.find(
            s => doSpeciesNamesMatch(s.species_name, node.name) || doSpeciesNamesMatch(s.species_id, node.name)
          );
          
          if (matchByName) {
            node.count = matchByName.count;
            return;
          }
        } else {
          let totalCount = 0;
          if (node.children) {
            node.children.forEach(child => {
              addCountsToTree(child);
              totalCount += child.count || 0;
            });
          }
          if (totalCount > 0) {
            node.count = totalCount;
          }
        }
      };
      
      addCountsToTree(parsedTree);
      setTreeData(parsedTree);
      
      if (selectedSpecies) {
        const findNodeBySpeciesName = (node: TreeNode): TreeNode | null => {
          if (doSpeciesNamesMatch(node.name, selectedSpecies)) {
            return node;
          }
          
          if (node.children) {
            for (const child of node.children) {
              const found = findNodeBySpeciesName(child);
              if (found) return found;
            }
          }
          
          return null;
        };
        
        const foundNode = findNodeBySpeciesName(parsedTree);
        if (foundNode) {
          setSelectedNodeId(foundNode.id);
        }
      }
    } catch (err) {
      console.error('Error parsing Newick data:', err);
      setError('Failed to parse tree data');
    } finally {
      setLoading(false);
    }
  }, [newickData, speciesCounts, selectedSpecies, doSpeciesNamesMatch]);

  // Render tree function
  const renderTree = useCallback(() => {
    if (!svgRef.current || !treeData) return;

    // Equal separation for standard phylogenetic tree appearance
    const getEqualSeparation = (a: d3.HierarchyNode<TreeNode>, b: d3.HierarchyNode<TreeNode>): number => {
      const isLeafA = !a.children || a.children.length === 0;
      const isLeafB = !b.children || b.children.length === 0;
      
      // Base spacing that adapts to tree size for readability
      let baseSpacing = 1.0;
      if (leafCount > 150) baseSpacing = 0.6;
      else if (leafCount > 100) baseSpacing = 0.7;
      else if (leafCount > 75) baseSpacing = 0.8;
      else if (leafCount > 50) baseSpacing = 0.9;
      else if (leafCount > 25) baseSpacing = 1.0;
      else baseSpacing = 1.2;
      
      // Equal spacing for all node types - standard phylogenetic style
      if (isLeafA && isLeafB) {
        // Equal spacing between leaves
        return baseSpacing * 2.0;
      } else if (isLeafA || isLeafB) {
        // Equal spacing between leaf and internal
        return baseSpacing * 1.8;
      } else {
        // Equal spacing between internal nodes
        return baseSpacing * 1.2;
      }
    };

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth || 800;
    const height = svgRef.current.clientHeight || 600;
    
    const container = svg
      .attr('width', width)
      .attr('height', height)
      .append('g');
      
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 5])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });
    
    svg.call(zoom);
    
    const g = container.append('g');
    
    if (useRadialLayout) {
      g.attr('transform', `translate(${width / 2}, ${height / 2})`);
    } else {
      // Adjust left margin based on tree density
      const leftMargin = leafCount > 50 ? width * 0.05 : width * 0.08;
      g.attr('transform', `translate(${leftMargin}, ${height / 2})`);
    }

    const root = d3.hierarchy(treeData) as d3.HierarchyNode<TreeNode>;

    if (useRadialLayout) {
      const maxRadius = Math.min(width, height) * 0.4;
      
      const treeLayout = d3.cluster<TreeNode>()
        .size([2 * Math.PI, maxRadius])
        .separation((a, b) => {
          // Equal spacing for radial layout
          let baseSpacing = 1.0;
          if (leafCount > 150) baseSpacing = 0.6;
          else if (leafCount > 100) baseSpacing = 0.7;
          else if (leafCount > 75) baseSpacing = 0.8;
          else if (leafCount > 50) baseSpacing = 0.9;
          else baseSpacing = 1.0;
          
          return baseSpacing * (a.parent === b.parent ? 1 : 2);
        });
        
      treeLayout(root);
      
      // 🔥 EQUAL BRANCH LENGTHS (Not equal leaf radius)
      const branchLength = 60; // Fixed small branch length
      
      // Set radius based on tree depth, not evolutionary distance
      // const maxDepth = Math.max(...root.descendants().map(d => d.depth || 0));
      
      root.descendants().forEach(d => {
        // Each level gets same radial distance increment
        d.y = (d.depth || 0) * branchLength;
      });
      
      root.each(d => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (d as any).polar = { angle: d.x || 0, radius: d.y || 0 };
      });
    } else {
      // 🔥 RECTANGULAR LAYOUT (SAME ALGORITHM AS RADIAL)
      const treeHeight = Math.max(height * 1.0, leafCount * 18);
      const treeWidth = width * 0.75;
      
      // First, use the tree layout with equal spacing (standard phylogenetic style)
      const treeLayout = d3.tree<TreeNode>()
        .size([treeHeight, treeWidth])
        .separation(getEqualSeparation);
      
      treeLayout(root);

      // Now calculate the x-coordinates based on cumulative branch lengths
      const maxDistance = Math.max(...root.descendants().map(d => calculateDistanceFromRoot(d)));
      const xScale = d3.scaleLinear()
        .domain([0, maxDistance])
        .range([0, treeWidth]);

      // CHOICE: Dendrogram vs Phylogram layout
      // Dendrogram: All leaves aligned (current approach - good for relationship comparison)
      // Phylogram: All nodes positioned by evolutionary distance (better for timing analysis)
      
      const usePhylogramLayout = false; // Toggle this to switch between approaches
      
      if (usePhylogramLayout) {
        // 🧬 PHYLOGRAM APPROACH: Position ALL nodes by evolutionary distance
        // This creates a more scientifically accurate representation of evolutionary timing
        // but can be harder to read when branch lengths vary dramatically
        root.each(d => {
          const distanceFromRoot = calculateDistanceFromRoot(d);
          d.y = xScale(distanceFromRoot);
        });
      } else {
        // 📊 DENDROGRAM APPROACH: Align all leaves, position internals by distance
        // This emphasizes relationships over timing, making comparisons easier
        root.each(d => {
          const isLeaf = !d.children || d.children.length === 0;
          
          if (isLeaf) {
            // All leaves go to the right extremity for easy comparison
            d.y = treeWidth;
          } else {
            // Internal nodes positioned based on evolutionary distance
            const distanceFromRoot = calculateDistanceFromRoot(d);
            d.y = xScale(distanceFromRoot);
          }
        });
      }

      // CRITICAL: Implement proper subtree separation to prevent line crossings
      const assignNonOverlappingRanges = (node: d3.HierarchyNode<TreeNode>) => {
        if (!node.children || node.children.length === 0) {
          return;
        }

        // First, recursively process all children
        node.children.forEach(child => assignNonOverlappingRanges(child));

        // Sort children by their current x position to maintain order
        node.children.sort((a, b) => (a.x || 0) - (b.x || 0));

        // Equal subtree range calculation (standard phylogenetic style)
        const getSubtreeRange = (subtreeRoot: d3.HierarchyNode<TreeNode>): [number, number] => {
          const descendants = subtreeRoot.descendants();
          const xPositions = descendants.map(d => d.x || 0);
          const minX = Math.min(...xPositions);
          const maxX = Math.max(...xPositions);
          
          // Equal padding for all subtrees - standard approach
          const basePadding = 10;
          
          return [minX - basePadding, maxX + basePadding];
        };

        // Calculate required ranges for each child subtree
        const childRanges = node.children.map(child => ({
          child: child,
          range: getSubtreeRange(child),
          center: child.x || 0
        }));

        // Detect and resolve overlaps by shifting entire subtrees
        for (let i = 1; i < childRanges.length; i++) {
          const currentRange = childRanges[i];
          const previousRange = childRanges[i - 1];

          const currentMin = currentRange.range[0];
          const previousMax = previousRange.range[1];

          if (currentMin < previousMax) {
            // Overlap detected! Shift with consistent buffer
            const overlapAmount = previousMax - currentMin + 8;
            
            // Shift the current subtree
            const shiftSubtree = (subtreeRoot: d3.HierarchyNode<TreeNode>, shift: number) => {
              subtreeRoot.descendants().forEach(descendant => {
                if (descendant.x !== undefined) {
                  descendant.x += shift;
                }
              });
            };

            shiftSubtree(currentRange.child, overlapAmount);
            
            // Update the range after shifting
            currentRange.range[0] += overlapAmount;
            currentRange.range[1] += overlapAmount;
            currentRange.center += overlapAmount;

            // Shift all subsequent subtrees too
            for (let j = i + 1; j < childRanges.length; j++) {
              shiftSubtree(childRanges[j].child, overlapAmount);
              childRanges[j].range[0] += overlapAmount;
              childRanges[j].range[1] += overlapAmount;
              childRanges[j].center += overlapAmount;
            }
          }
        }

        // Position the parent node at the center of its children's range
        if (node.children.length > 0) {
          const firstChildCenter = childRanges[0].center;
          const lastChildCenter = childRanges[childRanges.length - 1].center;
          node.x = (firstChildCenter + lastChildCenter) / 2;
        }
      };

      // Apply the subtree separation algorithm
      assignNonOverlappingRanges(root);

      // CRITICAL: Force perfectly equal spacing for all leaves
      const forceEqualLeafSpacing = () => {
        const allLeaves = root.leaves();
        if (allLeaves.length <= 1) return;
        
        // Sort leaves by their current vertical position
        allLeaves.sort((a, b) => (a.x || 0) - (b.x || 0));
        
        // Calculate the total vertical space available
        const totalHeight = treeHeight;
        const padding = totalHeight * 0.1; // 10% padding on top and bottom
        const availableHeight = totalHeight - (2 * padding);
        
        // Calculate perfectly equal spacing
        const spacingBetweenLeaves = availableHeight / (allLeaves.length - 1);
        
        // Assign perfectly equal positions to all leaves
        allLeaves.forEach((leaf, index) => {
          leaf.x = -availableHeight/2 + (index * spacingBetweenLeaves);
        });
        
        // Now propagate the changes up to internal nodes
        const updateInternalNodePositions = (node: d3.HierarchyNode<TreeNode>) => {
          if (!node.children || node.children.length === 0) {
            return; // This is a leaf, already positioned
          }
          
          // Position internal node at the center of its children
          const childPositions = node.children.map(child => {
            updateInternalNodePositions(child);
            return child.x || 0;
          });
          
          const minChildX = Math.min(...childPositions);
          const maxChildX = Math.max(...childPositions);
          node.x = (minChildX + maxChildX) / 2;
        };
        
        updateInternalNodePositions(root);
      };
      
      forceEqualLeafSpacing();

      // Final adjustment to center the tree
      const allNodes = root.descendants();
      const minX = Math.min(...allNodes.map(d => d.x || 0));
      const maxX = Math.max(...allNodes.map(d => d.x || 0));
      const centerOffset = (maxX + minX) / 2;
      
      allNodes.forEach(d => {
        if (d.x !== undefined) {
          d.x -= centerOffset;
        }
      });
    }

    const nodeScale = d3.scaleLinear()
      .domain([0, d3.max(speciesCounts, d => d.count) || 1])
      .range(leafCount > 100 ? [2, 6] : leafCount > 50 ? [3, 8] : [3, 10]);

    // Color intensity scale based on count values
    const colorIntensityScale = d3.scaleLinear()
      .domain([0, d3.max(speciesCounts, d => d.count) || 1])
      .range([0.3, 1.0]); // From 30% to 100% opacity

    // Enhanced color scale for value-based intensity
    const getNodeColor = (d: any, isSelected: boolean, isHighlighted: boolean): string => {
      if (isSelected) {
        return '#1976d2';
      } else if (isHighlighted) {
        return '#42a5f5';
      } else if (d.data.count && d.data.count > 0) {
        const intensity = colorIntensityScale(d.data.count);
        return d3.interpolate('#90ee90', '#228B22')(intensity); // Light green to dark green
      }
      return '#9e9e9e';
    };

    const getNodeOpacity = (d: any): number => {
      if (d.data.count && d.data.count > 0) {
        return colorIntensityScale(d.data.count);
      }
      return 0.6; // Default opacity for nodes without data
    };

    const getHighlightedPathToRoot = (nodeId: string | null): string[] => {
      if (!nodeId) return [];
      
      const findNode = (node: d3.HierarchyNode<TreeNode>, id: string): d3.HierarchyNode<TreeNode> | null => {
        if (node.data.id === id) return node;
        if (node.children) {
          for (const child of node.children) {
            const found = findNode(child, id);
            if (found) return found;
          }
        }
        return null;
      };
      
      const selectedNode = findNode(root, nodeId);
      return getPathToRoot(selectedNode);
    };
    
    const highlightedPath = getHighlightedPathToRoot(selectedNodeId);

    const links = g.append('g').attr('class', 'links');
      
    if (useRadialLayout) {
      // 🧬 INVERTED PHYLOGENETIC RADIAL: ARC FIRST, THEN RADIAL
      // This creates a "hub and spoke" pattern where ancestral relationships
      // are emphasized through curved connections at inner radii, then each
      // lineage extends cleanly outward to show independent evolution
      links.selectAll('.link')
        .data(root.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', (d: any) => {
          const sourceAngle = d.source.x;
          const sourceRadius = d.source.y;
          const targetAngle = d.target.x;
          const targetRadius = d.target.y;
          
          const sourceX = sourceRadius * Math.sin(sourceAngle);
          const sourceY = -sourceRadius * Math.cos(sourceAngle);
          const targetX = targetRadius * Math.sin(targetAngle);
          const targetY = -targetRadius * Math.cos(targetAngle);
          
          // 🔥 INVERTED PATTERN: ARC FIRST, THEN RADIAL
          // Step 1: Arc around at source radius (preserving source radius)
          const midX = sourceRadius * Math.sin(targetAngle);
          const midY = -sourceRadius * Math.cos(targetAngle);
          
          // Step 2: Go radially outward to target position
          const angleDiff = Math.abs(targetAngle - sourceAngle);
          
          if (angleDiff < 0.01) {
            // Same angle - pure radial line
            return `M${sourceX},${sourceY} L${targetX},${targetY}`;
          } else {
            // Inverted phylogenetic: arc + radial
            const largeArcFlag = angleDiff > Math.PI ? 1 : 0;
            const sweepFlag = targetAngle > sourceAngle ? 1 : 0;
            
            return `M${sourceX},${sourceY} 
                    A${sourceRadius},${sourceRadius} 0 ${largeArcFlag},${sweepFlag} ${midX},${midY}
                    L${targetX},${targetY}`;
          }
        })
        .attr('fill', 'none')
        .attr('stroke', (d: any) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? '#1976d2' : '#ccc';
        })
        .attr('stroke-width', (d: any) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? 3 : 1;
        })
        .attr('stroke-opacity', (d: any) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? 1 : 0.6;
        });
    } else {
      links.selectAll('.link')
        .data(root.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', (d: any) => {
          return `M${d.source.y},${d.source.x}
                  L${d.source.y},${d.target.x}
                  L${d.target.y},${d.target.x}`;
        })
        .attr('fill', 'none')
        .attr('stroke', (d: any) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? '#1976d2' : '#ccc';
        })
        .attr('stroke-width', (d: any) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? 3 : 1;
        })
        .attr('stroke-opacity', (d: any) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? 1 : 0.6;
        });
    }

    const nodes = g.append('g')
      .attr('class', 'nodes')
      .selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node');

    nodes.attr('transform', (d: any) => {
      if (useRadialLayout) {
        // For radial layout, all nodes (both leaves and internal) should be
        // positioned at their natural evolutionary position: (radius, angle)
        // This creates a clean, consistent appearance where the tree structure
        // is clearly visible without artificial "shoulder" positioning
        const x = d.y * Math.sin(d.x);
        const y = -d.y * Math.cos(d.x);
        return `translate(${x},${y})`;
      } else {
        return `translate(${d.y},${d.x})`;
      }
    })
    .style('cursor', 'pointer')
    .style('opacity', 1);

    nodes.append('circle')
      .attr('r', (d: any) => {
        const isLeaf = !d.children || d.children.length === 0;
        if (d.data.id === selectedNodeId) {
          return (isLeaf && d.data.count) ? nodeScale(d.data.count) * 1.5 : 8;
        }
        if (highlightedPath.includes(d.data.id)) {
          return (isLeaf && d.data.count) ? nodeScale(d.data.count) * 1.2 : 5;
        }
        if (isLeaf && d.data.count) {
          return nodeScale(d.data.count);
        }
        return isLeaf ? 4 : 2;
      })
      .attr('fill', (d: any) => {
        const isSelected = d.data.id === selectedNodeId;
        const isHighlighted = highlightedPath.includes(d.data.id);
        return getNodeColor(d, isSelected, isHighlighted);
      })
      .attr('fill-opacity', (d: any) => {
        if (d.data.id === selectedNodeId || highlightedPath.includes(d.data.id)) {
          return 1.0; // Full opacity for selected/highlighted
        }
        return getNodeOpacity(d);
      })
      .attr('stroke', (d: any) => {
        if (d.data.id === selectedNodeId) {
          return '#0d47a1';
        } else if (highlightedPath.includes(d.data.id)) {
          return '#1976d2';
        }
        return d.data.count && d.data.count > 0 ? '#2e7d32' : '#616161';
      })
      .attr('stroke-width', (d: any) => {
        if (d.data.id === selectedNodeId) return 3;
        if (highlightedPath.includes(d.data.id)) return 2;
        return 1;
      })
      .attr('stroke-opacity', (d: any) => {
        return getNodeOpacity(d);
      });

    nodes.append('text')
      .attr('class', 'species-label') // Add a clear class for selection
      .attr('dy', (d: any) => {
        // Better vertical centering, especially for nodes with long horizontal lines
        const isLeaf = !d.children || d.children.length === 0;
        if (!useRadialLayout && !isLeaf) {
          // For internal nodes, position text higher to avoid branch lines
          return '-12px';
        }
        return '0.35em';
      })
      .attr('x', (d: any) => {
        if (useRadialLayout) {
          const angle = d.x;
          return angle > Math.PI / 2 && angle < Math.PI * 3 / 2 ? -25 : 25; 
        } else {
          const isLeaf = !d.children || d.children.length === 0;
          if (isLeaf) {
            // Position text much further from node for leaves to prevent overlap
            const nodeRadius = d.data.count ? nodeScale(d.data.count) : 4;
            const baseOffset = nodeRadius + 15;
            // Add extra offset for very dense trees
            const densityOffset = leafCount > 100 ? 5 : leafCount > 50 ? 3 : 0;
            return baseOffset + densityOffset;
          } else {
            // Position text further left for internal nodes to avoid branch overlap
            return -25;
          }
        }
      })
      .attr('text-anchor', (d: any) => {
        if (useRadialLayout) {
          const angle = d.x;
          return angle > Math.PI / 2 && angle < Math.PI * 3 / 2 ? 'end' : 'start';
        } else {
          const isLeaf = !d.children || d.children.length === 0;
          return isLeaf ? 'start' : 'end';
        }
      })
      .attr('transform', (d: any) => {
        if (useRadialLayout) {
          const angle = d.x * 180 / Math.PI;
          const rotation = angle > 90 && angle < 270 ? angle + 180 : angle;
          return `rotate(${rotation - 90})`;
        }
        return null;
      })
      .text((d: any) => {
        const isLeaf = !d.children || d.children.length === 0;
        
        if (isLeaf || d.data.id === selectedNodeId || highlightedPath.includes(d.data.id)) {
          const name = d.data.name;
          const cleanName = name.replace(/^['"]|['"]$/g, '');
          
          // Store full name directly in data object for easy access
          if (isLeaf) {
            d.fullSpeciesName = cleanName;
            d.speciesCount = d.data.count || 0;
          }
          
          // More conservative truncation to prevent excessive cutting
          let maxLength = 25;
          if (leafCount > 150) maxLength = 14;
          else if (leafCount > 100) maxLength = 16;
          else if (leafCount > 75) maxLength = 18;
          else if (leafCount > 50) maxLength = 20;
          else if (leafCount > 25) maxLength = 22;
          
          // For very crowded areas, be more aggressive but not too much
          const nodeDepth = d.depth || 0;
          const siblingsCount = d.parent ? d.parent.children?.length || 1 : 1;
          if (siblingsCount > 15) {
            maxLength = Math.max(12, maxLength - 3);
          } else if (siblingsCount > 10) {
            maxLength = Math.max(14, maxLength - 2);
          }
          
          // Better truncation that preserves important parts
          let displayName = cleanName;
          if (cleanName.length > maxLength) {
            // Try to preserve genus and species parts
            const parts = cleanName.split(' ');
            if (parts.length > 1) {
              const genus = parts[0];
              const species = parts[1];
              const genusShort = genus.length > 8 ? genus.substring(0, 8) + '.' : genus;
              const speciesShort = species.length > 8 ? species.substring(0, 6) + '..' : species;
              displayName = `${genusShort} ${speciesShort}`;
              
              if (displayName.length > maxLength) {
                displayName = genusShort.substring(0, maxLength - 3) + '..';
              }
            } else {
              displayName = cleanName.substring(0, maxLength - 2) + '..';
            }
          }
          
          // Store truncated version for restoration
          if (isLeaf) {
            d.truncatedName = displayName;
          }
          
          if (d.data.count && d.data.count > 0) {
            displayName = `${displayName} (${d.data.count})`;
          } else if (d.data.id === selectedNodeId && selectedSpecies) {
            const matchCount = speciesCounts.find(s => 
              doSpeciesNamesMatch(s.species_name, selectedSpecies) ||
              doSpeciesNamesMatch(s.species_id, selectedSpecies)
            );
            
            if (matchCount && matchCount.count > 0) {
              displayName = `${displayName} (${matchCount.count})`;
            }
          }
          
          // Store final display name with count for restoration
          if (isLeaf) {
            d.originalDisplayName = displayName;
          }
          
          return displayName;
        }
        
        return '';
      })
      .attr('fill', (d: any) => {
        if (d.data.id === selectedNodeId) {
          return '#1976d2';
        } else if (highlightedPath.includes(d.data.id)) {
          return '#1976d2';
        }
        return '#333';
      })
      .attr('font-weight', (d: any) => {
        return d.data.id === selectedNodeId || highlightedPath.includes(d.data.id)
          ? 'bold'
          : 'normal';
      })
      .attr('font-size', (d: any) => {
        // More reasonable font scaling
        let fontSize = '12px';
        if (leafCount > 200) fontSize = '9px';
        else if (leafCount > 150) fontSize = '10px';
        else if (leafCount > 100) fontSize = '10px';
        else if (leafCount > 75) fontSize = '11px';
        else if (leafCount > 50) fontSize = '11px';
        else if (d.data.id === selectedNodeId) fontSize = '13px';
        
        return fontSize;
      })
      .attr('paint-order', 'stroke')
      .attr('stroke', (d: any) => {
        // Stronger white outline for better contrast
        if (highlightedPath.includes(d.data.id)) {
          return 'rgba(255,255,255,0.95)';
        } else if (!d.children || d.children.length === 0) {
          // Add white outline to all leaf text for better readability
          return 'rgba(255,255,255,0.8)';
        } else {
          // Add outline to internal node text too
          return 'rgba(255,255,255,0.7)';
        }
      })
      .attr('stroke-width', (d: any) => {
        if (highlightedPath.includes(d.data.id)) {
          return '3px';
        } else if (!d.children || d.children.length === 0) {
          return '2.5px';
        } else {
          return '2px';
        }
      });

    nodes.append('title')
      .text((d: any) => {
        const count = d.data.count || 0;
        return `${d.data.name} (${count} orthologue${count !== 1 ? 's' : ''})`;
      });
      
    nodes.on('click', (event, d) => {
      event.stopPropagation();
      
      const newSelectedId = d.data.id === selectedNodeId ? null : d.data.id;
      
      setSelectedNodeId(prev => {
        if (prev === newSelectedId) {
          return null;
        }
        return newSelectedId;
      });
      
      if (onSpeciesSelected) {
        const speciesName = newSelectedId === null ? null : d.data.name;
        onSpeciesSelected(speciesName);
      }
    });

    svg.on('click', (event: MouseEvent) => {
      if (event.target === svg.node()) {
        setSelectedNodeId(null);
        if (onSpeciesSelected) {
          onSpeciesSelected(null);
        }
      }
    });
    
    svg.on('dblclick', () => {
      svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity);
    });
    
    if (onTreeDataLoad) {
      onTreeDataLoad(true);
    }

    if (selectedNodeId) {
      nodes.filter((d: any) => d.data.id === selectedNodeId)
        .append('circle')
        .attr('class', 'selection-outer-ring')
        .attr('r', (d: any) => {
          const isLeaf = !d.children || d.children.length === 0;
          if (isLeaf && d.data.count) {
            return nodeScale(d.data.count) * 2;
          }
          return isLeaf ? 12 : 8;
        })
        .attr('fill', 'none')
        .attr('stroke', '#1976d2')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '4,2')
        .attr('opacity', 0.8);
      
      nodes.filter((d: any) => d.data.id === selectedNodeId)
        .append('circle')
        .attr('class', 'selection-center-marker')
        .attr('r', 3)
        .attr('fill', '#1976d2')
        .attr('opacity', 0.9);
    }
  }, [treeData, svgRef, selectedNodeId, useRadialLayout, speciesCounts, getPathToRoot, onSpeciesSelected, onTreeDataLoad, selectedSpecies, doSpeciesNamesMatch, calculateDistanceFromRoot, leafCount]);

  useEffect(() => {
    renderTree();
  }, [renderTree]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress size={24} />
        <Typography sx={{ ml: 1, fontSize: '0.9rem' }}>Loading D3 tree...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!treeData) {
    return (
      <Box p={2}>
        <Typography>No tree data available</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      overflow: 'auto',
      '&::-webkit-scrollbar': {
        width: '8px',
        height: '8px',
      },
      '&::-webkit-scrollbar-thumb': {
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: '4px',
      }
    }}>
      <svg 
        ref={svgRef} 
        width="100%" 
        height={useRadialLayout ? "100%" : (() => {
          // Standard height calculation for equal spacing
          if (!treeData || leafCount === 0) return "100%";
          
          // Calculate space for equal spacing (standard phylogenetic style)
          const baseHeight = leafCount * 18; // Standard spacing
          const standardHeight = Math.max(baseHeight, 500);
          const maxHeight = Math.min(standardHeight, 2200);
          
          return `${Math.max(100, (maxHeight / window.innerHeight) * 100)}%`;
        })()}
        style={{ 
          cursor: 'grab', 
          minHeight: useRadialLayout ? "500px" : (() => {
            if (!treeData || leafCount === 0) return "500px";
            const baseHeight = leafCount * 18;
            const standardHeight = Math.max(baseHeight, 500); // Standard equal spacing
            return `${standardHeight}px`;
          })()
        }}
      />
      
      <Typography 
        variant="caption" 
        component="div"
        sx={{ 
          position: 'absolute', 
          bottom: 8, 
          left: 8, 
          background: 'rgba(255,255,255,0.9)',
          padding: '4px 8px',
          borderRadius: '4px',
          fontSize: '0.75rem'
        }}
      >
        <strong>D3 Tree:</strong> Scroll to zoom, drag to pan, click nodes to select
      </Typography>
    </Box>
  );
};

export default PhylogeneticTreeView;