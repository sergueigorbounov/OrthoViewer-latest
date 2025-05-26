import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { Box, Typography, CircularProgress, Alert, FormControl, FormControlLabel, Switch } from '@mui/material';
import type { SpeciesCountData } from '../api/orthologueApi';

interface PhylogeneticTreeViewProps {
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies?: string | null;
  onSpeciesSelected?: (speciesName: string | null) => void;
  onTreeDataLoad?: (loaded: boolean) => void;
}

interface TreeNode {
  id: string;
  name: string;
  length?: number;
  children?: TreeNode[];
  x?: number;
  y?: number;
  count?: number;
  depth?: number;
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
      g.attr('transform', `translate(${width * 0.08}, ${height / 2})`);
    }

    const root = d3.hierarchy(treeData) as d3.HierarchyNode<TreeNode>;

    if (useRadialLayout) {
      const radius = Math.min(width, height) * 0.4;
      
      const treeLayout = d3.cluster<TreeNode>()
        .size([2 * Math.PI, radius])
        .separation((a, b) => {
          const isLeafA = !a.children || a.children.length === 0;
          const isLeafB = !b.children || b.children.length === 0;
          
          if (isLeafA && isLeafB) {
            return 2.5;
          } else if (isLeafA || isLeafB) {
            return 2.0;
          } else {
            return 1.5;
          }
        });
        
      treeLayout(root);
      
      const maxRadius = radius;
      root.each(d => {
        (d as any).polar = { angle: d.x, radius: d.y };
        
        if (!d.children || d.children.length === 0) {
          d.y = maxRadius;
        }
      });
    } else {
      const treeHeight = height * 2.5;
      const treeWidth = width * 0.75;
      
      const treeLayout = d3.tree<TreeNode>()
        .size([treeHeight, treeWidth])
        .separation((a, b) => {
          const isLeafA = !a.children || a.children.length === 0;
          const isLeafB = !b.children || b.children.length === 0;
          
          if (isLeafA && isLeafB) {
            return 3.5;
          } else if (isLeafA || isLeafB) {
            return 2.5;
          } else {
            return 1.5;
          }
        });
      
      treeLayout(root);

      const minimizeCrossings = (node: d3.HierarchyNode<TreeNode>) => {
        if (!node.children || node.children.length === 0) return;
        
        node.children.sort((a, b) => (a.x || 0) - (b.x || 0));
        
        node.children.forEach(child => minimizeCrossings(child));
      };
      
      minimizeCrossings(root);
      treeLayout(root);
      root.each(d => {
        if (d.x !== undefined) {
          d.x -= treeHeight / 3;
        }
      });
      
      const maxDepth = treeWidth;
      root.each(d => {
        if (!d.children || d.children.length === 0) {
          d.y = maxDepth;
        }
      });
    }

    const nodeScale = d3.scaleLinear()
      .domain([0, d3.max(speciesCounts, d => d.count) || 1])
      .range([3, 10]);

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
          
          const midX = targetRadius * Math.sin(sourceAngle);
          const midY = -targetRadius * Math.cos(sourceAngle);
          
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
      .attr('class', 'node')
      .attr('transform', (d: any) => {
        if (useRadialLayout) {
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
        if (d.data.id === selectedNodeId) {
          return '#1976d2';
        } else if (highlightedPath.includes(d.data.id)) {
          return '#42a5f5';
        } else if (d.data.count && d.data.count > 0) {
          return '#4caf50';
        }
        return '#9e9e9e';
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
      });

    nodes.append('text')
      .attr('dy', '.31em')
      .attr('x', (d: any) => {
        if (useRadialLayout) {
          const angle = d.x;
          return angle > Math.PI / 2 && angle < Math.PI * 3 / 2 ? -20 : 20; 
        } else {
          const isLeaf = !d.children || d.children.length === 0;
          if (isLeaf) {
            return 20;
          } else {
            return -20;
          }
        }
      })
      .attr('text-anchor', (d: any) => {
        if (useRadialLayout) {
          const angle = d.x;
          return angle > Math.PI / 2 && angle < Math.PI * 3 / 2 ? 'end' : 'start';
        } else {
          const isLeaf = !d.children || d.children.length === 0;
          if (isLeaf) {
            return 'start';
          } else {
            return 'end';
          }
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
          
          let displayName = cleanName.length > 16 ? cleanName.substring(0, 14) + '...' : cleanName;
          
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
        return d.data.id === selectedNodeId ? '13px' : '12px';
      })
      .attr('paint-order', 'stroke')
      .attr('stroke', (d: any) => {
        return highlightedPath.includes(d.data.id) ? 'rgba(255,255,255,0.7)' : 'none';
      })
      .attr('stroke-width', (d: any) => {
        return highlightedPath.includes(d.data.id) ? '2px' : '0';
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
  }, [treeData, svgRef, selectedNodeId, useRadialLayout, speciesCounts, getPathToRoot, onSpeciesSelected, onTreeDataLoad, selectedSpecies, doSpeciesNamesMatch]);

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

export default PhylogeneticTreeView;