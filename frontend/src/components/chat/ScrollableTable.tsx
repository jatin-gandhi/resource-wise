import React from 'react';
import { Box } from '@mui/material';

interface SimpleTableProps {
  children: React.ReactNode;
}

const SimpleTable: React.FC<SimpleTableProps> = ({ children, ...props }) => {
  return (
    <Box
      sx={{
        width: '100%',
        marginBottom: '1rem',
        border: '1px solid',
        borderColor: 'grey.300',
        borderRadius: '6px',
        backgroundColor: 'background.paper',
        overflow: 'hidden', // Just to maintain border radius
      }}
    >
      <table
        {...props}
        style={{
          borderCollapse: 'collapse',
          width: '100%',
          margin: 0,
          border: 'none',
        }}
      >
        {children}
      </table>
    </Box>
  );
};

export default SimpleTable;
