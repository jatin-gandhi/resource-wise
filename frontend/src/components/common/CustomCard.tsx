import React from 'react';
import { Card, CardContent } from '@mui/material';
import type { CardProps } from '@mui/material';
import { styled } from '@mui/material/styles';

interface CustomCardProps extends CardProps {
  hover?: boolean;
}

const StyledCard = styled(Card)<CustomCardProps>(({ hover }) => ({
  boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  borderRadius: 8,
  border: '1px solid #e5e7eb',
  transition: 'all 0.3s ease-in-out',

  ...(hover && {
    '&:hover': {
      boxShadow:
        '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
      transform: 'translateY(-2px)',
    },
  }),
}));

const StyledCardContent = styled(CardContent)({
  padding: '24px',
  '&:last-child': {
    paddingBottom: '24px',
  },
});

const CustomCard: React.FC<CustomCardProps> = ({
  children,
  hover = false,
  ...props
}) => {
  return (
    <StyledCard hover={hover} {...props}>
      <StyledCardContent>{children}</StyledCardContent>
    </StyledCard>
  );
};

export default CustomCard;
