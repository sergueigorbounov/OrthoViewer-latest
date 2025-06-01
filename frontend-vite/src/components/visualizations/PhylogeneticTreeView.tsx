import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { Box, Typography, CircularProgress, Alert, FormControlLabel, Switch, Tabs, Tab } from '@mui/material';
import type { SpeciesCountData } from '../../api/orthologueApi';
import * as Phylocanvas from '@phylocanvas/phylocanvas.gl';

// Enhanced interfaces with better type definitions
interface TreeNode {
  id: string;
  name: string;
  length?: number;
  depth?: number;
  children?: TreeNode[];
  count?: number;
}

interface ExtendedTreeNode extends TreeNode {
  polar?: {
    angle: number;
    radius: number;
  };
  textRotation?: number;
  textAnchor?: 'start' | 'middle' | 'end';
}

// D3 specific type definitions
type D3TreeNode = d3.HierarchyNode<ExtendedTreeNode>;
type D3TreeLink = d3.HierarchyLink<ExtendedTreeNode>;
type D3Selection = d3.Selection<SVGGElement, unknown, null, undefined>;
type D3TreeSelection = d3.Selection<SVGGElement, D3TreeNode, SVGGElement, unknown>;
type D3LinkSelection = d3.Selection<SVGPathElement, D3TreeLink, SVGGElement, unknown>;

interface PhylogeneticTreeViewProps {
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies?: string | null;
  onSpeciesSelected?: (speciesName: string | null) => void;
  onTreeDataLoad?: (loaded: boolean) => void;
}

const PhylogeneticTreeView: React.FC<PhylogeneticTreeViewProps> = ({ 
  newickData, 
  speciesCounts,
  selectedSpecies,
  onSpeciesSelected,
  onTreeDataLoad
}) => {
  const [activeTreeTab, setActiveTreeTab] = useState<number>(0); // 0 = D3, 1 = Phylocanvas
  const [phylocanvasAvailable, setPhylocanvasAvailable] = useState<boolean>(false);
  const [useRadialLayout, setUseRadialLayout] = useState<boolean>(() => {
    const savedLayout = localStorage.getItem('treeViewLayout');
    return savedLayout === 'radial' || savedLayout === null;
  });

  // Check if Phylocanvas is available - now using synchronous check
  useEffect(() => {
    const checkPhylocanvas = () => {
      try {
        // Check if Phylocanvas and its createTree function exist
        if (Phylocanvas && typeof Phylocanvas.createTree === 'function') {
          setPhylocanvasAvailable(true);
        } else {
          throw new Error('Phylocanvas not properly loaded');
        }
      } catch (error) {
        console.log('Phylocanvas not available, using D3 only');
        setPhylocanvasAvailable(false);
        setActiveTreeTab(0); // Force to D3 tab
      }
    };
    
    checkPhylocanvas();
  }, []);

  const handleTreeTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTreeTab(newValue);
  };

  useEffect(() => {
    localStorage.setItem('treeViewLayout', useRadialLayout ? 'radial' : 'rectangular');
  }, [useRadialLayout]);

  return (
    <Box sx={{ height: '100%', width: '100%', position: 'relative' }}>
      {/* Tree Implementation Tabs - Only show if we have multiple options */}
      {phylocanvasAvailable && (
        <Box sx={{ 
          position: 'absolute', 
          top: 5, 
          left: 5, 
          zIndex: 10,
          background: 'rgba(255,255,255,0.95)',
          borderRadius: '6px',
          border: '1px solid #ddd',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <Tabs 
            value={activeTreeTab} 
            onChange={handleTreeTabChange}
            sx={{ minHeight: '36px' }}
          >
            <Tab label="D3 Tree" sx={{ minHeight: '36px', py: 1, fontSize: '0.8rem' }} />
            <Tab label="Phylocanvas" sx={{ minHeight: '36px', py: 1, fontSize: '0.8rem' }} />
          </Tabs>
        </Box>
      )}

      {/* Show D3 implementation info if Phylocanvas not available */}
      {!phylocanvasAvailable && (
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
      )}

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
      <Box sx={{ width: '100%', height: '100%', pt: phylocanvasAvailable ? '50px' : '0px' }}>
        {(activeTreeTab === 0 || !phylocanvasAvailable) && (
          <D3TreeImplementation
            newickData={newickData}
            speciesCounts={speciesCounts}
            selectedSpecies={selectedSpecies}
            onSpeciesSelected={onSpeciesSelected}
            onTreeDataLoad={onTreeDataLoad}
            useRadialLayout={useRadialLayout}
          />
        )}
        {phylocanvasAvailable && activeTreeTab === 1 && (
          <PhylocanvasImplementation
            newickData={newickData}
            speciesCounts={speciesCounts}
            selectedSpecies={selectedSpecies}
            onSpeciesSelected={onSpeciesSelected}
            onTreeDataLoad={onTreeDataLoad}
            useRadialLayout={useRadialLayout}
          />
        )}
      </Box>
    </Box>
  );
};

// D3 Implementation Component
const D3TreeImplementation: React.FC<{
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies?: string | null;
  onSpeciesSelected?: (speciesName: string | null) => void;
  onTreeDataLoad?: (loaded: boolean) => void;
  useRadialLayout: boolean;
}> = ({ newickData, speciesCounts, selectedSpecies, onSpeciesSelected, onTreeDataLoad, useRadialLayout }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [treeData, setTreeData] = useState<ExtendedTreeNode | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [leafCount, setLeafCount] = useState(0);

  // Helper function to check if two species names match
  const doSpeciesNamesMatch = useCallback((name1: string, name2: string): boolean => {
    if (!name1 || !name2) return false;
    
    const normalized1 = name1.toLowerCase().trim();
    const normalized2 = name2.toLowerCase().trim();
    
    if (normalized1 === normalized2) return true;
    if (normalized1.includes(normalized2) || normalized2.includes(normalized1)) return true;
    
    const genus1 = normalized1.split(/[\s_]/)[0];
    const genus2 = normalized2.split(/[\s_]/)[0];
    
    return genus1 === genus2 && genus1.length > 2;
  }, []);

  // Get the path from a node to the root
  const getPathToRoot = useCallback((node: D3TreeNode | null): string[] => {
    if (!node) return [];
    
    const path: string[] = [];
    let current: D3TreeNode | null = node;
    
    while (current) {
      path.push(current.data.id);
      current = current.parent;
    }
    
    return path;
  }, []);

  // Calculate distance from root based on branch lengths
  const calculateDistanceFromRoot = useCallback((node: D3TreeNode): number => {
    let distance = 0;
    let current: D3TreeNode | null = node;
    
    while (current && current.parent) {
      // Use actual branch length if available, else default value
      distance += current.data.length || 0.1;
      current = current.parent;
    }
    
    return distance;
  }, []);

  // Render tree with enhanced visuals
  const renderTree = useCallback(() => {
    if (!svgRef.current || !treeData) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth || 800;
    const height = svgRef.current.clientHeight || 600;
    
    // Add gradient and filter definitions
    const defs = svg.append('defs');

    // Node gradient
    const nodeGradient = defs.append('radialGradient')
      .attr('id', 'node-gradient')
      .attr('cx', '30%')
      .attr('cy', '30%')
      .attr('r', '70%');

    nodeGradient.append('stop')
      .attr('offset', '0%')
      .attr('style', 'stop-color:rgb(124,252,0);stop-opacity:1');

    nodeGradient.append('stop')
      .attr('offset', '100%')
      .attr('style', 'stop-color:rgb(34,139,34);stop-opacity:1');

    // Glow effect for highlighting
    const glow = defs.append('filter')
      .attr('id', 'glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    glow.append('feGaussianBlur')
      .attr('stdDeviation', '2')
      .attr('result', 'coloredBlur');

    const glowMerge = glow.append('feMerge');
    glowMerge.append('feMergeNode').attr('in', 'coloredBlur');
    glowMerge.append('feMergeNode').attr('in', 'SourceGraphic');

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
      const leftMargin = Math.max(width * 0.05, Math.min(width * 0.15, 20 + Math.log(leafCount) * 15));
      g.attr('transform', `translate(${leftMargin}, ${height / 2})`);
    }

    const root = d3.hierarchy(treeData) as D3TreeNode;

    if (useRadialLayout) {
      const radius = Math.min(width, height) * 0.42;
      
      const treeLayout = d3.cluster<ExtendedTreeNode>()
        .size([2 * Math.PI, radius])
        .separation((a, b) => {
          const isLeafA = !a.children || a.children.length === 0;
          const isLeafB = !b.children || b.children.length === 0;
          
          const depthFactor = Math.max(1, 3 - Math.min(a.depth || 0, b.depth || 0) * 0.5);
          const neighborCount = isLeafA && isLeafB ? 
            Math.max(a.parent?.children?.length || 1, b.parent?.children?.length || 1) : 1;
          const densityFactor = 1 + Math.log(neighborCount) * 0.2;
          
          if (isLeafA && isLeafB) {
            return 2.5 * depthFactor * densityFactor;
          } else if (isLeafA || isLeafB) {
            return 2.0 * depthFactor;
          }
          return 1.5 * depthFactor;
        });
      
      treeLayout(root);
      
      // Store polar coordinates for smooth transitions
      root.each(node => {
        if (node.x !== undefined) {
          const angle = (node.x - Math.PI / 2) / Math.PI * 180;
          node.data.textRotation = angle > 90 && angle < 270 ? angle + 180 : angle;
          node.data.textAnchor = angle > 90 && angle < 270 ? 'end' : 'start';
          node.data.polar = {
            angle: node.x,
            radius: node.y || 0
          };
        }
      });

    } else {
      const treeHeight = height * 2.5;
      const treeWidth = width * 0.75;
      
      const treeLayout = d3.tree<ExtendedTreeNode>()
        .size([treeHeight, treeWidth])
        .separation((a, b) => {
          const isLeafA = !a.children || a.children.length === 0;
          const isLeafB = !b.children || b.children.length === 0;
          
          if (isLeafA && isLeafB) {
            return 3.5;
          } else if (isLeafA || isLeafB) {
            return 2.5;
          }
          return 1.5;
        });
      
      treeLayout(root);
    }

    const getHighlightedPathToRoot = (nodeId: string | null): string[] => {
      if (!nodeId) return [];
      
      const findNode = (node: D3TreeNode, id: string): D3TreeNode | null => {
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

    // Enhanced node scale based on count values
    const nodeScale = d3.scaleLinear()
      .domain([0, d3.max(speciesCounts, d => d.count) || 1])
      .range(leafCount > 100 ? [3, 8] : [4, 12]);

    // Color scale for count-based intensity
    const colorIntensityScale = d3.scaleLinear()
      .domain([0, d3.max(speciesCounts, d => d.count) || 1])
      .range([0.3, 1.0]);

    const links = g.append('g').attr('class', 'links');
    
    if (useRadialLayout) {
      links.selectAll('.link')
        .data(root.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', (d: D3TreeLink) => {
          const sourceAngle = d.source.data.polar?.angle || 0;
          const sourceRadius = d.source.data.polar?.radius || 0;
          const targetAngle = d.target.data.polar?.angle || 0;
          const targetRadius = d.target.data.polar?.radius || 0;
          
          const sourceX = sourceRadius * Math.sin(sourceAngle);
          const sourceY = -sourceRadius * Math.cos(sourceAngle);
          const targetX = targetRadius * Math.sin(targetAngle);
          const targetY = -targetRadius * Math.cos(targetAngle);
          
          const midRadius = targetRadius;
          const midAngle = sourceAngle;
          const midX = midRadius * Math.sin(midAngle);
          const midY = -midRadius * Math.cos(midAngle);
          
          if (Math.abs(sourceAngle - targetAngle) < 0.1) {
            return `M${sourceX},${sourceY} L${targetX},${targetY}`;
          }
          
          return `M${sourceX},${sourceY} 
                  L${midX},${midY} 
                  A${targetRadius},${targetRadius} 0 
                  ${Math.abs(targetAngle - sourceAngle) > Math.PI ? 1 : 0} 
                  ${targetAngle > sourceAngle ? 1 : 0} 
                  ${targetX},${targetY}`;
        })
        .attr('fill', 'none')
        .attr('stroke', (d: D3TreeLink) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? '#1976d2' : '#ccc';
        })
        .attr('stroke-width', (d: D3TreeLink) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? 3 : 1;
        })
        .attr('stroke-opacity', (d: D3TreeLink) => {
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
        .attr('d', (d: D3TreeLink) => {
          return `M${d.source.y},${d.source.x || 0}
                  L${d.source.y},${d.target.x || 0}
                  L${d.target.y},${d.target.x || 0}`;
        })
        .attr('fill', 'none')
        .attr('stroke', (d: D3TreeLink) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? '#1976d2' : '#ccc';
        })
        .attr('stroke-width', (d: D3TreeLink) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? 3 : 1;
        })
        .attr('stroke-opacity', (d: D3TreeLink) => {
          const isHighlighted = highlightedPath.includes(d.source.data.id) && 
                             highlightedPath.includes(d.target.data.id);
          return isHighlighted ? 1 : 0.6;
        });
    }

    // Add nodes with enhanced visuals
    const nodes = g.append('g')
      .attr('class', 'nodes')
      .selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', (d: D3TreeNode) => {
        if (useRadialLayout) {
          const x = (d.y || 0) * Math.sin(d.x || 0);
          const y = -(d.y || 0) * Math.cos(d.x || 0);
          return `translate(${x},${y})`;
        }
        return `translate(${d.y},${d.x || 0})`;
      })
      .style('cursor', 'pointer');

    // Add node circles with gradients and effects
    nodes.append('circle')
      .attr('r', (d: D3TreeNode) => {
        const isLeaf = !d.children || d.children.length === 0;
        if (d.data.id === selectedNodeId) {
          return (isLeaf && d.data.count) ? nodeScale(d.data.count) * 1.5 : 8;
        }
        if (highlightedPath.includes(d.data.id)) {
          return (isLeaf && d.data.count) ? nodeScale(d.data.count) * 1.2 : 5;
        }
        return isLeaf && d.data.count ? nodeScale(d.data.count) : 3;
      })
      .attr('fill', (d: D3TreeNode) => {
        if (d.data.id === selectedNodeId) {
          return 'url(#node-gradient)';
        }
        if (highlightedPath.includes(d.data.id)) {
          return '#42a5f5';
        }
        if (d.data.count && d.data.count > 0) {
          const intensity = colorIntensityScale(d.data.count);
          return d3.interpolateRgb('#90caf9', '#1565c0')(intensity);
        }
        return '#9e9e9e';
      })
      .attr('stroke', (d: D3TreeNode) => {
        if (d.data.id === selectedNodeId) {
          return '#0d47a1';
        }
        if (highlightedPath.includes(d.data.id)) {
          return '#1976d2';
        }
        return '#757575';
      })
      .attr('stroke-width', (d: D3TreeNode) => {
        if (d.data.id === selectedNodeId) return 2;
        if (highlightedPath.includes(d.data.id)) return 1.5;
        return 1;
      })
      .attr('filter', (d: D3TreeNode) => {
        return d.data.id === selectedNodeId ? 'url(#glow)' : 'none';
      });

    // Add node labels with improved positioning
    nodes.append('text')
      .attr('dy', '.31em')
      .attr('x', (d: D3TreeNode) => {
        if (useRadialLayout) {
          return d.data.textAnchor === 'end' ? -12 : 12;
        }
        const isLeaf = !d.children || d.children.length === 0;
        return isLeaf ? 8 : -8;
      })
      .attr('text-anchor', (d: D3TreeNode) => {
        if (useRadialLayout) {
          return d.data.textAnchor || 'start';
        }
        const isLeaf = !d.children || d.children.length === 0;
        return isLeaf ? 'start' : 'end';
      })
      .attr('transform', (d: D3TreeNode) => {
        if (useRadialLayout && d.data.textRotation !== undefined) {
          return `rotate(${d.data.textRotation})`;
        }
        return null;
      })
      .text((d: D3TreeNode) => {
        const isLeaf = !d.children || d.children.length === 0;
        if (isLeaf || d.data.id === selectedNodeId || highlightedPath.includes(d.data.id)) {
          let displayName = d.data.name.replace(/^['"]|['"]$/g, '');
          if (d.data.count && d.data.count > 0) {
            displayName = `${displayName} (${d.data.count})`;
          }
          return displayName;
        }
        return '';
      })
      .attr('fill', (d: D3TreeNode) => {
        if (d.data.id === selectedNodeId || highlightedPath.includes(d.data.id)) {
          return '#1976d2';
        }
        return '#333';
      })
      .attr('font-weight', (d: D3TreeNode) => {
        return d.data.id === selectedNodeId || highlightedPath.includes(d.data.id) ? 
          'bold' : 'normal';
      })
      .attr('font-size', (d: D3TreeNode) => {
        return d.data.id === selectedNodeId ? '13px' : '12px';
      });

    // Add interactive behaviors
    nodes.on('click', (event: MouseEvent, d: D3TreeNode) => {
      event.stopPropagation();
      const newSelectedId = d.data.id === selectedNodeId ? null : d.data.id;
      setSelectedNodeId(newSelectedId);
      
      if (onSpeciesSelected) {
        onSpeciesSelected(newSelectedId === null ? null : d.data.name);
      }
    });

    svg.on('click', () => {
      setSelectedNodeId(null);
      if (onSpeciesSelected) {
        onSpeciesSelected(null);
      }
    });

    // Add animation for highlighted paths
    if (selectedNodeId) {
      nodes.filter((d: D3TreeNode) => d.data.id === selectedNodeId)
        .append('circle')
        .attr('class', 'selection-outer-ring')
        .attr('r', (d: D3TreeNode) => {
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
    }

  }, [treeData, svgRef, selectedNodeId, useRadialLayout, speciesCounts, getPathToRoot, 
      onSpeciesSelected, onTreeDataLoad, selectedSpecies, doSpeciesNamesMatch, leafCount]);

  useEffect(() => {
    renderTree();
  }, [renderTree]);

  // Process Newick data
  useEffect(() => {
    if (!newickData) {
      setError('No tree data provided');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const parseNewick = (newickString: string): ExtendedTreeNode => {
        const cleaned = newickString.trim().replace(/;$/, '');
        
        const parseSubtree = (str: string, id = 'root', depth = 0): ExtendedTreeNode => {
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
              foundOpeningParen = true;
              openCount++;
            } else if (char === ')') {
              openCount--;
              if (openCount === 0 && foundOpeningParen) {
                nameAndLength = str.slice(i + 1);
                break;
              }
            }
            if (foundOpeningParen) {
              childrenStr += char;
            }
          }
          
          const children = childrenStr
            .slice(1) // Remove leading '('
            .split(/,(?![^(]*\))/)
            .filter(Boolean)
            .map((childStr, index) => parseSubtree(childStr.trim(), `${id}_${index}`, depth + 1));

          const [name, lengthStr] = nameAndLength.split(':');
          
          return {
            id: name.trim() || id,
            name: name.trim() || id,
            length: lengthStr ? parseFloat(lengthStr) : undefined,
            depth: depth,
            children: children
          };
        };

        const parsedTree = parseSubtree(cleaned);
        
        // Count leaves and add IDs
        let leafId = 0;
        const countLeaves = (node: ExtendedTreeNode): number => {
          if (!node.children || node.children.length === 0) {
            node.id = `leaf_${leafId++}`;
            return 1;
          }
          const count = node.children.reduce((sum, child) => sum + countLeaves(child), 0);
          node.id = `node_${node.name}_${count}`;
          return count;
        };
        
        const totalLeaves = countLeaves(parsedTree);
        setLeafCount(totalLeaves);

        // Add species counts
        const addCountsToTree = (node: ExtendedTreeNode) => {
          const nodeName = node.name.replace(/^['"]|['"]$/g, '');
          const speciesCount = speciesCounts.find(s => 
            doSpeciesNamesMatch(s.species_name, nodeName) ||
            doSpeciesNamesMatch(s.species_id, nodeName)
          );
          
          if (speciesCount) {
            node.count = speciesCount.count;
          }
          
          if (node.children) {
            node.children.forEach(addCountsToTree);
          }
        };
        
        addCountsToTree(parsedTree);
        setTreeData(parsedTree);

        if (selectedSpecies) {
          const findNodeBySpecies = (node: ExtendedTreeNode): ExtendedTreeNode | null => {
            if (doSpeciesNamesMatch(node.name, selectedSpecies)) {
              return node;
            }
            
            if (node.children) {
              for (const child of node.children) {
                const found = findNodeBySpecies(child);
                if (found) return found;
              }
            }
            return null;
          };

          const foundNode = findNodeBySpecies(parsedTree);
          if (foundNode) {
            setSelectedNodeId(foundNode.id);
          }
        }

        return parsedTree;
      };

      parseNewick(newickData);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error parsing tree data';
      console.error('Error parsing Newick data:', errorMessage);
      setError('Failed to parse tree data');
    } finally {
      setLoading(false);
    }
  }, [newickData, speciesCounts, selectedSpecies, doSpeciesNamesMatch]);

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
        height={useRadialLayout ? "100%" : "250%"}
        style={{ cursor: 'grab', minHeight: useRadialLayout ? "500px" : "1500px" }}
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

// Phylocanvas Implementation Component - Modified to use static import
interface PhylocanvasNode {
  id: string;
  label: string;
  originalLabel?: string;
  selected: boolean;
  radius: number;
}

interface PhylocanvasTree {
  source: string;
  type: 'rectangular' | 'radial';
  canvas: HTMLCanvasElement;
  destroy(): void;
  render(): void;
  getLeafNodes(): PhylocanvasNode[];
  on(event: 'click' | 'loaded', callback: (event: {node: PhylocanvasNode}) => void): void;
  on(event: 'error', callback: (error: PhylocanvasError) => void): void;
}

interface PhylocanvasEvent {
  node: PhylocanvasNode;
}

interface PhylocanvasError {
  message: string;
}

const PhylocanvasImplementation: React.FC<{
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies?: string | null;
  onSpeciesSelected?: (speciesName: string | null) => void;
  onTreeDataLoad?: (loaded: boolean) => void;
  useRadialLayout: boolean;
}> = ({ newickData, speciesCounts, selectedSpecies, onSpeciesSelected, onTreeDataLoad, useRadialLayout }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const treeInstanceRef = useRef<PhylocanvasTree | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const doSpeciesNamesMatch = useCallback((name1: string, name2: string): boolean => {
    if (!name1 || !name2) return false;
    
    const normalized1 = name1.toLowerCase().trim();
    const normalized2 = name2.toLowerCase().trim();
    
    if (normalized1 === normalized2) return true;
    if (normalized1.includes(normalized2) || normalized2.includes(normalized1)) return true;
    
    const genus1 = normalized1.split(/[\s_]/)[0];
    const genus2 = normalized2.split(/[\s_]/)[0];
    
    return genus1 === genus2 && genus1.length > 2;
  }, []);

  // Initialize Phylocanvas
  useEffect(() => {
    const initializeTree = () => {
      if (!containerRef.current || !newickData) return;

      try {
        setLoading(true);
        setError(null);

        if (treeInstanceRef.current) {
          treeInstanceRef.current.destroy();
          treeInstanceRef.current = null;
        }

        containerRef.current.innerHTML = '';

        // Create new tree instance
        const tree = Phylocanvas.createTree(containerRef.current, {
          type: useRadialLayout ? 'radial' : 'rectangular',
          source: newickData,
          alignLabels: true,
          showLabels: true,
          showLeafLabels: true,
          showInternalLabels: false,
          interactive: true,
          zoom: true,
          pan: true,
          showScale: false,
          nodeSize: 4,
          fontSize: 12,
          fontFamily: 'Arial, sans-serif',
          strokeWidth: 1,
          strokeColour: '#ccc',
          fillColour: '#4caf50',
          selectedFillColour: '#1976d2',
          highlightColour: '#42a5f5',
          padding: 20
        }) as PhylocanvasTree;

        treeInstanceRef.current = tree;

        tree.on('loaded', () => {
          const leaves = tree.getLeafNodes();
          leaves.forEach((node: PhylocanvasNode) => {
            const nodeName = node.originalLabel || node.label;
            const matchingSpecies = speciesCounts.find(s => 
              doSpeciesNamesMatch(s.species_name, nodeName) || 
              doSpeciesNamesMatch(s.species_id, nodeName)
            );
            if (matchingSpecies && matchingSpecies.count > 0) {
              node.label = `${nodeName} (${matchingSpecies.count})`;
              node.radius = Math.max(3, Math.min(10, matchingSpecies.count / 10));
            }
          });
          
          tree.render();
          
          if (onTreeDataLoad) {
            onTreeDataLoad(true);
          }
          
          setLoading(false);
        });

        tree.on('click', (event: PhylocanvasEvent) => {
          if (event.node) {
            const nodeName = event.node.originalLabel || event.node.label;
            
            tree.getLeafNodes().forEach((node: PhylocanvasNode) => {
              node.selected = false;
            });
            
            event.node.selected = true;
            tree.render();
            
            if (onSpeciesSelected) {
              onSpeciesSelected(nodeName);
            }
          }
        });

        tree.on('error', (error: PhylocanvasError) => {
          console.error('Phylocanvas error:', error);
          setError('Failed to render phylogenetic tree');
          setLoading(false);
        });

      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error initializing Phylocanvas';
        console.error('Error initializing Phylocanvas:', errorMessage);
        setError('Phylocanvas library not available');
        setLoading(false);
      }
    };

    initializeTree();

    return () => {
      if (treeInstanceRef.current) {
        treeInstanceRef.current.destroy();
        treeInstanceRef.current = null;
      }
    };
  }, [newickData, useRadialLayout, speciesCounts, doSpeciesNamesMatch, onSpeciesSelected, onTreeDataLoad]);

  // Handle species selection from parent
  useEffect(() => {
    if (!treeInstanceRef.current || !selectedSpecies) return;

    try {
      const tree = treeInstanceRef.current;
      const leaves = tree.getLeafNodes();
      
      leaves.forEach((node: PhylocanvasNode) => {
        node.selected = false;
      });
      
      const targetNode = leaves.find((node: PhylocanvasNode) => {
        const nodeName = node.originalLabel || node.label;
        return doSpeciesNamesMatch(nodeName, selectedSpecies);
      });
      
      if (targetNode) {
        targetNode.selected = true;
      }
      
      tree.render();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error selecting species';
      console.error('Error selecting species in Phylocanvas:', errorMessage);
    }
  }, [selectedSpecies, doSpeciesNamesMatch]);

  // Render loading or error state
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress size={24} />
        <Typography sx={{ ml: 1, fontSize: '0.9rem' }}>Loading Phylocanvas...</Typography>
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

  return (
    <Box 
      ref={containerRef}
      sx={{ 
        width: '100%', 
        height: '100%',
        '& canvas': {
          borderRadius: '4px'
        }
      }}
    />
  );
};

export default PhylogeneticTreeView;