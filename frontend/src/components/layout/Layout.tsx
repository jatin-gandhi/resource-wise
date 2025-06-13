import React from 'react';
import { Box } from '@mui/material';
import Header from '../Header';

interface LayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
  fullHeight?: boolean;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  showHeader = true,
  fullHeight = false,
}) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      {showHeader && <Header />}

      <Box
        component="main"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          ...(fullHeight && {
            height: showHeader ? 'calc(100vh - 80px)' : '100vh',
          }),
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
