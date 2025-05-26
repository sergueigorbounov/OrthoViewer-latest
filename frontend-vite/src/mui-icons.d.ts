import React from 'react';
import { SvgIcon } from '@mui/material';

// Use React.ComponentProps instead of importing SvgIconProps
type IconProps = React.ComponentProps<typeof SvgIcon>;

declare module './components/icons' {
  const Icon: React.ComponentType<IconProps>;
  export default Icon;
}

declare module './components/icons/index' {
  export const AccountTree: React.ComponentType<IconProps>;
  export const CloudUpload: React.ComponentType<IconProps>;
  export const Close: React.ComponentType<IconProps>;
  export const DataObject: React.ComponentType<IconProps>;
  export const ExpandMore: React.ComponentType<IconProps>;
  export const NavigateNext: React.ComponentType<IconProps>;
  export const UploadFile: React.ComponentType<IconProps>;
  export const ViewList: React.ComponentType<IconProps>;
  export const Visibility: React.ComponentType<IconProps>;
  export const Biotech: React.ComponentType<IconProps>;
}
