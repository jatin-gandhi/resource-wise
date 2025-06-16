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
          alignItems: 'center',
          '& .dot': {
            width: 5,
            height: 5,
            borderRadius: '50%',
            backgroundColor: 'primary.main',
            animation: 'bounce 1.4s ease-in-out infinite',
          },
          '& .dot:nth-of-type(1)': { animationDelay: '0s' },
          '& .dot:nth-of-type(2)': { animationDelay: '0.2s' },
          '& .dot:nth-of-type(3)': { animationDelay: '0.4s' },
          '@keyframes bounce': {
            '0%, 60%, 100%': {
              transform: 'translateY(0)',
            },
            '30%': {
              transform: 'translateY(-8px)',
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
