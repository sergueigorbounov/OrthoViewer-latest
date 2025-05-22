// Type definitions for MUI icons
declare module '@mui/icons-material/*' {
  import React from 'react';
  import { SvgIconProps } from '@mui/material/SvgIcon';
  
  const Icon: React.ComponentType<SvgIconProps>;
  export default Icon;
}

// Handle overall module imports
declare module '@mui/icons-material' {
  import { SvgIconProps } from '@mui/material/SvgIcon';
  
  // Define all icon exports
  export const AccountTree: React.ComponentType<SvgIconProps>;
  export const CloudUpload: React.ComponentType<SvgIconProps>;
  export const Close: React.ComponentType<SvgIconProps>;
  export const DataObject: React.ComponentType<SvgIconProps>;
  export const ExpandMore: React.ComponentType<SvgIconProps>;
  export const NavigateNext: React.ComponentType<SvgIconProps>;
  export const UploadFile: React.ComponentType<SvgIconProps>;
  export const ViewList: React.ComponentType<SvgIconProps>;
  export const Visibility: React.ComponentType<SvgIconProps>;
  export const Biotech: React.ComponentType<SvgIconProps>;
  
  // Add more icons as needed
} 