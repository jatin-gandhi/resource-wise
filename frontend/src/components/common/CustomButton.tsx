import React from 'react';
import { Button } from '@mui/material';
import type { ButtonProps } from '@mui/material';
import { styled } from '@mui/material/styles';

interface CustomButtonProps extends Omit<ButtonProps, 'variant'> {
  customVariant?: 'primary' | 'secondary' | 'outline' | 'ghost';
}

const StyledButton = styled(Button)<CustomButtonProps>(({
  theme,
  customVariant,
}) => {
  const baseStyles = {
    borderRadius: 8,
    textTransform: 'none' as const,
    fontWeight: 500,
    padding: '10px 24px',
    fontSize: '0.875rem',
    transition: 'all 0.2s ease-in-out',
  };

  switch (customVariant) {
    case 'primary':
      return {
        ...baseStyles,
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.primary.contrastText,
        border: `2px solid ${theme.palette.primary.main}`,
        '&:hover': {
          backgroundColor: theme.palette.primary.dark,
          borderColor: theme.palette.primary.dark,
          boxShadow: '0 4px 12px rgba(38, 38, 109, 0.3)',
          transform: 'translateY(-1px)',
        },
        '&:active': {
          transform: 'translateY(0)',
        },
      };
    case 'secondary':
      return {
        ...baseStyles,
        backgroundColor: theme.palette.secondary.light,
        color: theme.palette.text.primary,
        border: `2px solid ${theme.palette.secondary.main}`,
        '&:hover': {
          backgroundColor: theme.palette.secondary.main,
          borderColor: theme.palette.secondary.dark,
          transform: 'translateY(-1px)',
        },
        '&:active': {
          transform: 'translateY(0)',
        },
      };
    case 'outline':
      return {
        ...baseStyles,
        backgroundColor: 'transparent',
        color: theme.palette.primary.main,
        border: `2px solid ${theme.palette.primary.main}`,
        '&:hover': {
          backgroundColor: theme.palette.primary.main,
          color: theme.palette.primary.contrastText,
          transform: 'translateY(-1px)',
        },
        '&:active': {
          transform: 'translateY(0)',
        },
      };
    case 'ghost':
      return {
        ...baseStyles,
        backgroundColor: 'transparent',
        color: theme.palette.text.primary,
        border: '2px solid transparent',
        '&:hover': {
          backgroundColor: theme.palette.secondary.light,
          borderColor: theme.palette.secondary.main,
          transform: 'translateY(-1px)',
        },
        '&:active': {
          transform: 'translateY(0)',
        },
      };
    default:
      return baseStyles;
  }
});

export const CustomButton: React.FC<CustomButtonProps> = ({
  customVariant = 'primary',
  children,
  ...props
}) => {
  return (
    <StyledButton customVariant={customVariant} {...props}>
      {children}
    </StyledButton>
  );
};
