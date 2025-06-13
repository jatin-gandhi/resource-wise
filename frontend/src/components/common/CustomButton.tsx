import React from 'react';
import { Button } from '@mui/material';
import type { ButtonProps } from '@mui/material';
import { styled } from '@mui/material/styles';

interface CustomButtonProps extends ButtonProps {
  customVariant?: 'primary' | 'secondary' | 'outline';
}

const StyledButton = styled(Button)<CustomButtonProps>(({ customVariant }) => ({
  textTransform: 'none',
  fontWeight: 500,
  borderRadius: 8,
  padding: '12px 24px',
  transition: 'all 0.2s ease-in-out',

  ...(customVariant === 'primary' && {
    backgroundColor: '#2563eb',
    color: '#ffffff',
    '&:hover': {
      backgroundColor: '#1d4ed8',
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
    },
  }),

  ...(customVariant === 'secondary' && {
    backgroundColor: '#f3f4f6',
    color: '#111827',
    '&:hover': {
      backgroundColor: '#e5e7eb',
      transform: 'translateY(-1px)',
    },
  }),

  ...(customVariant === 'outline' && {
    backgroundColor: 'transparent',
    color: '#2563eb',
    border: '2px solid #2563eb',
    '&:hover': {
      backgroundColor: '#2563eb',
      color: '#ffffff',
      transform: 'translateY(-1px)',
    },
  }),
}));

const CustomButton: React.FC<CustomButtonProps> = ({
  customVariant = 'primary',
  children,
  ...props
}) => {
  const variant = customVariant === 'outline' ? 'outlined' : 'contained';

  return (
    <StyledButton variant={variant} customVariant={customVariant} {...props}>
      {children}
    </StyledButton>
  );
};

export default CustomButton;
