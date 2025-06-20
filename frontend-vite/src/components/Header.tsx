import React from 'react';
import { Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material';
import BiotechIcon from '@mui/icons-material/Biotech';

// Define the navigation links - including the new ETE Tree Search
const navLinks = [
  { name: 'Explore', path: '/orthologues' },
  { name: 'Chunked Search', path: '/chunked-search' },
  { name: 'Server Side Rendering', path: '/ete-search' },
];

const Header: React.FC = () => {
  return (
    <AppBar position="static" sx={{ marginBottom: 2 }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Box display="flex" alignItems="center">
            <BiotechIcon sx={{ mr: 1, fontSize: '2rem' }} />
            <Typography
              variant="h6"
              noWrap
              component={Link}
              to="/"
              sx={{
                mr: 2,
                fontWeight: 700,
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              OrthoViewer
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
            {navLinks.map((link) => (
              <Button
                key={link.name}
                component={Link}
                to={link.path}
                sx={{ color: 'white', mx: 1 }}
              >
                {link.name}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;