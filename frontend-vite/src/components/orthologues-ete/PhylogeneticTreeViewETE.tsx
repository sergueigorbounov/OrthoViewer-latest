import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import * as d3 from 'd3';
import type { SpeciesCountData } from '../../api/orthologueETEApi';

interface PhylogeneticTreeViewETEProps {
  newickData: string;
  speciesCounts: SpeciesCountData[];
  selectedSpecies: string | null;
  onSpeciesSelected: (species: string | null) => void;
  onTreeDataLoad: () => void;
}

const PhylogeneticTreeViewETE: React.FC<PhylogeneticTreeViewETEProps> = ({
  newickData,
  speciesCounts,
  selectedSpecies,
  onSpeciesSelected,
  onTreeDataLoad
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!newickData || !svgRef.current) return;

    try {
      // Clear previous tree
      d3.select(svgRef.current).selectAll('*').remove();

      // Parse the Newick data using ETE-specific format
      const treeData = d3.hierarchy(parseETENewick(newickData));

      // Set up the tree layout with ETE-specific configurations
      const width = 800;
      const height = 600;
      const margin = { top: 20, right: 90, bottom: 20, left: 90 };

      const tree = d3.tree()
        .size([height - margin.top - margin.bottom, width - margin.left - margin.right])
        .separation((a, b) => (a.parent === b.parent ? 1 : 2));

      // Create the SVG container
      const svg = d3.select(svgRef.current)
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Generate the tree layout
      const root = tree(treeData);

      // Add links
      svg.selectAll('.link')
        .data(root.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', d3.linkHorizontal()
          .x(d => d.y)
          .y(d => d.x))
        .style('fill', 'none')
        .style('stroke', '#ccc')
        .style('stroke-width', '2px');

      // Add nodes
      const nodes = svg.selectAll('.node')
        .data(root.descendants())
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.y},${d.x})`);

      // Add node circles
      nodes.append('circle')
        .attr('r', 5)
        .style('fill', d => {
          const speciesName = d.data.name;
          const speciesCount = speciesCounts.find(s => s.species_name === speciesName);
          return speciesCount && speciesCount.count > 0 ? '#4caf50' : '#ccc';
        })
        .style('stroke', d => {
          const speciesName = d.data.name;
          return selectedSpecies === speciesName ? '#1976d2' : '#fff';
        })
        .style('stroke-width', d => selectedSpecies === d.data.name ? '3px' : '1.5px');

      // Add node labels
      nodes.append('text')
        .attr('dy', '.31em')
        .attr('x', d => d.children ? -8 : 8)
        .style('text-anchor', d => d.children ? 'end' : 'start')
        .text(d => d.data.name)
        .style('font-size', '12px')
        .style('fill', d => {
          const speciesName = d.data.name;
          return selectedSpecies === speciesName ? '#1976d2' : '#333';
        });

      // Add click handlers
      nodes.style('cursor', 'pointer')
        .on('click', (event, d) => {
          event.stopPropagation();
          onSpeciesSelected(d.data.name);
        });

      setLoading(false);
      onTreeDataLoad();
    } catch (err) {
      console.error('Error rendering ETE tree:', err);
      setError('Error rendering the phylogenetic tree');
      setLoading(false);
    }
  }, [newickData, speciesCounts, selectedSpecies, onSpeciesSelected, onTreeDataLoad]);

  if (error) {
    return (
      <Typography color="error" align="center">
        {error}
      </Typography>
    );
  }

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '600px', overflow: 'auto' }}>
      {loading && (
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
          }}
        >
          <CircularProgress />
        </Box>
      )}
      <svg
        ref={svgRef}
        style={{
          width: '100%',
          height: '100%',
          visibility: loading ? 'hidden' : 'visible',
        }}
      />
    </Box>
  );
};

// Helper function to parse ETE-specific Newick format
function parseETENewick(newick: string) {
  // This is a simplified parser for demonstration
  // In a real implementation, you would need to handle all ETE-specific features
  const parseNode = (str: string) => {
    const node: any = { name: str };
    return node;
  };

  // Basic recursive parsing of the Newick string
  const parseSubtree = (str: string) => {
    if (!str.includes('(')) {
      return parseNode(str);
    }

    const children = [];
    let current = '';
    let depth = 0;
    
    for (let i = 0; i < str.length; i++) {
      const char = str[i];
      if (char === '(' && depth === 0) {
        depth++;
      } else if (char === '(' && depth > 0) {
        current += char;
        depth++;
      } else if (char === ')' && depth > 1) {
        current += char;
        depth--;
      } else if (char === ')' && depth === 1) {
        if (current) {
          children.push(parseSubtree(current));
        }
        current = '';
        depth--;
      } else if (char === ',' && depth === 1) {
        if (current) {
          children.push(parseSubtree(current));
        }
        current = '';
      } else {
        current += char;
      }
    }

    if (current) {
      children.push(parseSubtree(current));
    }

    return { name: '', children };
  };

  // Remove semicolon and whitespace
  const cleanNewick = newick.trim().replace(/;$/, '');
  return parseSubtree(cleanNewick);
}

export default PhylogeneticTreeViewETE; 