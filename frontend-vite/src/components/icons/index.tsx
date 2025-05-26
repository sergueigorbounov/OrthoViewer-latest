import React from 'react';
import { SvgIcon } from '@mui/material';

// Use React.ComponentProps to get the props type from SvgIcon
type IconProps = React.ComponentProps<typeof SvgIcon>;

// Define a set of custom icons as simple SVG paths
const Icons = {
  ExpandMore: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/>
    </SvgIcon>
  ),
  
  AccountTree: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M22 11V3h-7v3H9V3H2v8h7V8h2v10h4v3h7v-8h-7v3h-2V8h2v3z"/>
    </SvgIcon>
  ),
  
  UploadFile: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
    </SvgIcon>
  ),
  
  NavigateNext: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
    </SvgIcon>
  ),
  
  ViewList: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M3,5H21V7H3V5M3,13V11H21V13H3M3,19V17H21V19H3Z"/>
    </SvgIcon>
  ),
  
  Biotech: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M12.5,7C12.5,5.89 13.39,5 14.5,5C15.61,5 16.5,5.89 16.5,7C16.5,8.11 15.61,9 14.5,9C13.39,9 12.5,8.11 12.5,7M14.64,1.5C13.56,1.5 12.68,2.38 12.68,3.46V4.5H16.32V3.46C16.32,2.38 15.44,1.5 14.36,1.5H14.64M8,22A2,2 0 0,1 6,20A2,2 0 0,1 8,18A2,2 0 0,1 10,20A2,2 0 0,1 8,22M7,10.5C5.89,10.5 5,11.39 5,12.5C5,13.61 5.89,14.5 7,14.5C8.11,14.5 9,13.61 9,12.5C9,11.39 8.11,10.5 7,10.5Z"/>
    </SvgIcon>
  ),
  
  Visibility: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"/>
    </SvgIcon>
  ),
  
  CloudUpload: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M14,13V17H10V13H7L12,8L17,13M19.35,10.03C18.67,6.59 15.64,4 12,4C9.11,4 6.6,5.64 5.35,8.03C2.34,8.36 0,10.9 0,14A6,6 0 0,0 6,20H19A5,5 0 0,0 24,15C24,12.36 21.95,10.22 19.35,10.03Z"/>
    </SvgIcon>
  ),
  
  DataObject: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M5,3A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H11V19H5V5H11V3H5M18,10V14L19,13.5V14.5L18,14V18H20V20H18C17.11,20 16.3,19.47 16,18.68V14L15,14.5V13.5L16,14V9.32C16.3,8.53 17.11,8 18,8H20V10H18Z"/>
    </SvgIcon>
  ),
  
  Close: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
    </SvgIcon>
  ),
  
  Search: (props: IconProps) => (
    <SvgIcon {...props}>
      <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
    </SvgIcon>
  ),
};

// Export individual icons WITHOUT Icon suffix
export const ExpandMore = Icons.ExpandMore;
export const AccountTree = Icons.AccountTree;
export const UploadFile = Icons.UploadFile;
export const NavigateNext = Icons.NavigateNext;
export const ViewList = Icons.ViewList;
export const Biotech = Icons.Biotech;
export const Visibility = Icons.Visibility;
export const CloudUpload = Icons.CloudUpload;
export const DataObject = Icons.DataObject;
export const Close = Icons.Close;
export const Search = Icons.Search;

// Export WITH Icon suffix (aliases for components that expect this naming)
export const ExpandMoreIcon = Icons.ExpandMore;
export const AccountTreeIcon = Icons.AccountTree;
export const UploadFileIcon = Icons.UploadFile;
export const NavigateNextIcon = Icons.NavigateNext;
export const ViewListIcon = Icons.ViewList;
export const BiotechIcon = Icons.Biotech;
export const VisibilityIcon = Icons.Visibility;
export const CloudUploadIcon = Icons.CloudUpload;
export const DataObjectIcon = Icons.DataObject;
export const CloseIcon = Icons.Close;
export const SearchIcon = Icons.Search;

// Export default Icons object
export default Icons;
