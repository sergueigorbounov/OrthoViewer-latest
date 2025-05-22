import React from 'react';
import { Box, Typography } from '@mui/material';
import { 
  CloudUploadIcon, 
  VisibilityIcon,
  BiotechIcon,
  AccountTreeIcon,
  ExpandMoreIcon,
  NavigateNextIcon,
  ViewListIcon,
  DataObjectIcon,
  CloseIcon,
  UploadFileIcon
} from './icons';

const IconTest = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Icon Test</Typography>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <CloudUploadIcon />
        <VisibilityIcon />
        <BiotechIcon />
        <AccountTreeIcon />
        <ExpandMoreIcon />
        <NavigateNextIcon />
        <ViewListIcon />
        <DataObjectIcon />
        <CloseIcon />
        <UploadFileIcon />
      </Box>
    </Box>
  );
};

export default IconTest; 