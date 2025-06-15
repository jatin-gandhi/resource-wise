import React from 'react';
import { Box, Typography } from '@mui/material';

interface ThinkingIndicatorProps {
  text?: string;
  sx?: object;
}

const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({
  text = 'AI is thinking...',
  sx = {},
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        p: 1,
        backgroundColor: 'primary.50',
        borderRadius: 1,
        border: '1px solid',
        borderColor: 'primary.200',
        ...sx,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          gap: 0.5,
          '& .dot': {
            width: 6,
            height: 6,
            borderRadius: '50%',
            backgroundColor: 'primary.main',
            animation: 'pulse 1.4s ease-in-out infinite both',
          },
          '& .dot:nth-of-type(1)': { animationDelay: '-0.32s' },
          '& .dot:nth-of-type(2)': { animationDelay: '-0.16s' },
          '@keyframes pulse': {
            '0%, 80%, 100%': {
              transform: 'scale(0)',
            },
            '40%': {
              transform: 'scale(1)',
            },
          },
        }}
      >
        <div className="dot" />
        <div className="dot" />
        <div className="dot" />
      </Box>
      <Typography variant="caption" color="primary.main" fontWeight={500}>
        {text}
      </Typography>
    </Box>
  );
};

export default ThinkingIndicator;
