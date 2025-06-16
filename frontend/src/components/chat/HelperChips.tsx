import React from 'react';
import { Box, Chip } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Book as BookIcon,
} from '@mui/icons-material';

interface HelperChipsProps {
  onChipClick: (text: string) => void;
  disabled?: boolean;
}

const HelperChips: React.FC<HelperChipsProps> = ({
  onChipClick,
  disabled = false,
}) => {
  const helperQueries = [
    {
      id: 'utilization',
      text: 'Give me the utilization of KD India team',
      icon: <TrendingUpIcon fontSize="small" />,
      color: 'primary' as const,
    },
    {
      id: 'top-projects',
      text: 'Give me the top 5 projects with highest cost per developer',
      icon: <AssessmentIcon fontSize="small" />,
      color: 'secondary' as const,
    },
    {
      id: 'dev-partners',
      text: 'All Dev Partners currently working in KD',
      icon: <BookIcon fontSize="small" />,
      color: 'primary' as const,
    },
  ];

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1,
        flexWrap: 'wrap',
        justifyContent: 'flex-start',
        py: 0,
        px: 2,
        pb: 1,
        opacity: disabled ? 0.5 : 1,
        transition: 'opacity 0.2s ease-in-out',
      }}
    >
      {helperQueries.map(query => (
        <Chip
          key={query.id}
          label={query.text}
          icon={query.icon}
          onClick={() => !disabled && onChipClick(query.text)}
          disabled={disabled}
          variant="filled"
          size="small"
          sx={{
            borderRadius: 2,
            px: 0.5,
            height: 28,
            fontSize: '0.75rem',
            fontWeight: 500,
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease-in-out',
            backgroundColor: 'rgba(19, 7, 56, 0.8)',
            color: 'white',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            '&:hover': {
              backgroundColor: disabled
                ? 'rgba(19, 7, 56, 0.8)'
                : 'rgba(19, 7, 56, 0.9)',
              borderColor: disabled
                ? 'rgba(255, 255, 255, 0.1)'
                : 'rgba(255, 255, 255, 0.3)',
              transform: disabled ? 'none' : 'translateY(-1px)',
              boxShadow: disabled ? 'none' : '0 2px 8px rgba(19, 7, 56, 0.3)',
            },
            '&:active': {
              transform: disabled ? 'none' : 'translateY(0)',
            },
            '& .MuiChip-icon': {
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '0.875rem',
            },
            '& .MuiChip-label': {
              px: 0.5,
              color: 'white',
            },
            '&.Mui-disabled': {
              backgroundColor: 'rgba(19, 7, 56, 0.5)',
              color: 'rgba(255, 255, 255, 0.5)',
              '& .MuiChip-icon': {
                color: 'rgba(255, 255, 255, 0.3)',
              },
            },
          }}
        />
      ))}
    </Box>
  );
};

export default HelperChips;
