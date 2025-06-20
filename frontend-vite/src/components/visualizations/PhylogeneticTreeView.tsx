import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as d3 from 'd3';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Alert, 
  AlertTitle,
  FormControl, 
  FormControlLabel, 
  Switch, 
  Tabs, 
  Tab, 
  Paper, 
  Chip, 
  Breadcrumbs, 
  IconButton, 
  Tooltip, 
  Grid,
  Slider,
  Card,
  CardContent
} from '@mui/material';
import { 
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  CenterFocusStrong as CenterIcon,
  Fullscreen as FullscreenIcon,
  Navigation as NavigationIcon,
  Home as HomeIcon,
  Map as MapIcon
} from '@mui/icons-material';
import type { SpeciesCountData } from '../../api/orthologueApi';
// Phylocanvas import removed to prevent componentName error

interface PhylogeneticTreeViewProps {
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies?: string | null;
  onSpeciesSelected?: (speciesName: string | null) => void;
  onTreeDataLoad?: (loaded: boolean) => void;
  orthoGroup: string;
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
  onTreeDataLoad,
  orthoGroup
}) => {
  const [phylocanvasAvailable, setPhylocanvasAvailable] = useState<boolean>(false); // Force D3 only
  const [activeTreeTab, setActiveTreeTab] = useState<number>(0);
  const [useRadialLayout, setUseRadialLayout] = useState<boolean>(() => {
    return localStorage.getItem('treeViewLayout') === 'radial';
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [treeData, setTreeData] = useState<TreeNode | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [showMiniMap, setShowMiniMap] = useState(false);
  const [navigationHistory, setNavigationHistory] = useState<string[]>([]);
  const phylocanvasRef = useRef<any>(null);

  // Temporarily disable Phylocanvas due to compatibility issues
  useEffect(() => {
    // Force D3 only to avoid Phylocanvas componentName error
    setPhylocanvasAvailable(false);
    setActiveTreeTab(0);
  }, []);

  const handleTreeTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTreeTab(newValue);
  };

  useEffect(() => {
    localStorage.setItem('treeViewLayout', useRadialLayout ? 'radial' : 'rectangular');
  }, [useRadialLayout]);

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 25, 300));
    if (phylocanvasRef.current) {
      phylocanvasRef.current.zoom(zoomLevel / 100);
    }
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 25, 25));
    if (phylocanvasRef.current) {
      phylocanvasRef.current.zoom(zoomLevel / 100);
    }
  };

  const handleCenter = () => {
    if (phylocanvasRef.current) {
      phylocanvasRef.current.fitInPanel();
    }
    setZoomLevel(100);
  };

  const handleFullscreen = () => {
    const element = document.getElementById('tree-container');
    if (element) {
      element.requestFullscreen?.();
    }
  };

  const addToNavigationHistory = (nodeId: string) => {
    setNavigationHistory(prev => [...prev.slice(-4), nodeId]); // Keep last 5 items
  };

  // Helper function to check if two species names match
  const doSpeciesNamesMatch = useCallback((name1: string, name2: string): boolean => {
    if (!name1 || !name2) return false;
    
    const normalized1 = name1.toLowerCase().trim();
    const normalized2 = name2.toLowerCase().trim();
    
    // Direct match
    if (normalized1 === normalized2) return true;
    
    // Check if one contains the other
    if (normalized1.includes(normalized2) || normalized2.includes(normalized1)) return true;
    
    // Try genus matching
    const genus1 = normalized1.split(/[\s_]/)[0];
    const genus2 = normalized2.split(/[\s_]/)[0];
    
    if (genus1 === genus2 && genus1.length > 2) {
      return true;
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
    if (!phylocanvasRef.current || !treeData) return;

    const svg = d3.select(phylocanvasRef.current);
    svg.selectAll('*').remove();

    const width = svg.node()?.clientWidth || 800;
    const height = svg.node()?.clientHeight || 600;
    
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
  }, [treeData, phylocanvasRef, selectedNodeId, useRadialLayout, speciesCounts, getPathToRoot, onSpeciesSelected, onTreeDataLoad, selectedSpecies, doSpeciesNamesMatch]);

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
    <Box sx={{ width: '100%', minHeight: '600px' }}>
      {/* Navigation Controls */}
      <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
            <Breadcrumbs aria-label="navigation">
              <Chip
                icon={<HomeIcon />}
                label="Tree View"
                variant="outlined"
                size="small"
              />
              <Chip
                label={orthoGroup}
                color="primary"
                size="small"
              />
            </Breadcrumbs>
            
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Tooltip title="Zoom In">
                <IconButton onClick={handleZoomIn} disabled={zoomLevel >= 300}>
                  <ZoomInIcon />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Zoom Out">
                <IconButton onClick={handleZoomOut} disabled={zoomLevel <= 25}>
                  <ZoomOutIcon />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Center Tree">
                <IconButton onClick={handleCenter}>
                  <CenterIcon />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Fullscreen">
                <IconButton onClick={handleFullscreen}>
                  <FullscreenIcon />
                </IconButton>
              </Tooltip>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={showMiniMap}
                    onChange={(e) => setShowMiniMap(e.target.checked)}
                    size="small"
                  />
                }
                label="Mini-map"
                sx={{ ml: 1 }}
              />
            </Box>
          </Box>
        
          {/* Zoom Control */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" sx={{ minWidth: '80px' }}>
              Zoom: {zoomLevel}%
            </Typography>
            <Slider
              value={zoomLevel}
              onChange={(_, value) => setZoomLevel(value as number)}
              min={25}
              max={300}
              step={25}
              marks
              sx={{ flexGrow: 1 }}
            />
          </Box>
        
          {/* Navigation History */}
          {navigationHistory.length > 0 && (
            <Box>
              <Typography variant="caption" color="textSecondary">
                Recent Navigation:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                {navigationHistory.map((nodeId, index) => (
                  <Chip
                    key={index}
                    label={nodeId}
                    size="small"
                    variant="outlined"
                    icon={<NavigationIcon />}
                    onClick={() => {
                      // Navigate to node functionality
                      console.log('Navigate to:', nodeId);
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Main Tree View */}
      <Paper elevation={2} sx={{ position: 'relative' }}>
        <Tabs value={activeTreeTab} onChange={(e, newValue) => setActiveTreeTab(newValue)}>
          <Tab label="Radial Layout" />
          <Tab label="Rectangular Layout" />
        </Tabs>

        <Box 
          id="tree-container"
          sx={{ 
            position: 'relative',
            height: '600px',
            overflow: 'hidden',
            backgroundColor: '#fafafa'
          }}
        >
          {/* Mini-map overlay */}
          {showMiniMap && (
            <Card 
              sx={{ 
                position: 'absolute',
                top: 10,
                right: 10,
                width: 200,
                height: 150,
                zIndex: 1000,
                opacity: 0.9
              }}
            >
              <CardContent sx={{ p: 1 }}>
                <Typography variant="caption">Tree Overview</Typography>
                <Box sx={{ 
                  width: '100%', 
                  height: 100, 
                  backgroundColor: '#e0e0e0',
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <MapIcon color="disabled" />
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Tree content */}
          <Box
            sx={{
              width: '100%',
              height: '100%',
              overflow: 'auto',
              '&::-webkit-scrollbar': {
                width: '8px',
                height: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: '#f1f1f1',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#888',
                borderRadius: '4px',
              },
              '&::-webkit-scrollbar-thumb:hover': {
                background: '#555',
              },
            }}
          >
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading phylogenetic tree...</Typography>
              </Box>
            ) : error ? (
              <Alert severity="error" sx={{ m: 2 }}>
                <AlertTitle>Tree Visualization Error</AlertTitle>
                {error}
              </Alert>
            ) : (
              <svg
                ref={phylocanvasRef}
                width="100%"
                height="100%"
                style={{ 
                  transform: `scale(${zoomLevel / 100})`,
                  transformOrigin: 'top left',
                  transition: 'transform 0.3s ease'
                }}
              />
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

// Phylocanvas Implementation Component - Now shows fallback since import is removed
const PhylocanvasImplementation: React.FC<{
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies?: string | null;
  onSpeciesSelected?: (speciesName: string | null) => void;
  onTreeDataLoad?: (loaded: boolean) => void;
  useRadialLayout: boolean;
}> = ({ newickData, speciesCounts, selectedSpecies, onSpeciesSelected, onTreeDataLoad, useRadialLayout }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>('Phylocanvas library removed to prevent compatibility errors');

  useEffect(() => {
    // Phylocanvas has been removed to prevent componentName errors
    if (onTreeDataLoad) {
      onTreeDataLoad(false);
    }
    setLoading(false);
  }, [onTreeDataLoad]);

  const renderFallbackMessage = () => (
    <Box sx={{ p: 3, textAlign: 'center' }}>
      <Typography variant="h6" gutterBottom>
        Phylocanvas Temporarily Disabled
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        Phylocanvas has been temporarily disabled due to compatibility issues.
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        The D3 tree implementation provides excellent phylogenetic tree visualization as an alternative.
      </Typography>
      <Box sx={{ 
        bgcolor: 'grey.100', 
        p: 2, 
        borderRadius: 1, 
        fontFamily: 'monospace',
        fontSize: '0.9em',
        mt: 2 
      }}>
        Please use the D3 Tree tab for visualization
      </Box>
    </Box>
  );

  return (
    <Box p={2}>
      <Alert severity="info" sx={{ mb: 2 }}>
        Phylocanvas temporarily disabled to prevent browser console errors
      </Alert>
      {renderFallbackMessage()}
    </Box>
  );
};

export default PhylogeneticTreeView;