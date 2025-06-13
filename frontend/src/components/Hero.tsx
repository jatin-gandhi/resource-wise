import React from 'react';
import { Box, Container, Typography } from '@mui/material';

const Hero: React.FC = () => {
  return (
    <Box
      component="section"
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        py: { xs: 10, md: 16 },
        textAlign: 'center',
      }}
    >
      <Container maxWidth="lg">
        <Typography
          variant="h1"
          component="h1"
          sx={{
            fontSize: { xs: '3rem', md: '4rem', lg: '5rem' },
            fontWeight: 700,
            lineHeight: 1.1,
            mb: 4,
          }}
        >
          ResourceWise
        </Typography>

        <Typography
          variant="h4"
          component="p"
          sx={{
            fontSize: { xs: '1.5rem', md: '2rem' },
            color: 'rgba(255, 255, 255, 0.9)',
            fontWeight: 300,
            maxWidth: '4xl',
            mx: 'auto',
            lineHeight: 1.4,
          }}
        >
          Intelligent Resource Allocation for Our Organization
        </Typography>
      </Container>
    </Box>
  );
};

export default Hero;
