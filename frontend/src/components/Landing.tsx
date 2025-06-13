import React from 'react';
import { Box, Typography, Container, keyframes } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { CustomButton } from './common/CustomButton';
import kickdrumLogo from '../assets/logo-kickdrum-white.png';

// Dynamic gradient animation
const gradientAnimation = keyframes`
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
`;

const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #130738 0%, #000000 100%)',
        backgroundSize: '400% 400%',
        animation: `${gradientAnimation} 6s ease infinite`,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header with Kickdrum Logo */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-start',
          alignItems: 'center',
          p: 3,
        }}
      >
        <Box
          component="img"
          src={kickdrumLogo}
          alt="Kickdrum Logo"
          sx={{
            height: 50,
            width: 'auto',
            filter: 'drop-shadow(0 2px 10px rgba(255, 255, 255, 0.2))',
          }}
        />
      </Box>

      {/* Main Content - Centered */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Container maxWidth="md">
          <Box
            sx={{
              textAlign: 'center',
              color: 'white',
            }}
          >
            {/* ResourceWise Title */}
            <Typography
              variant="h1"
              component="h1"
              sx={{
                fontWeight: 700,
                mb: 4,
                fontSize: { xs: '3rem', md: '4.5rem', lg: '5.5rem' },
                fontFamily: 'Lato, sans-serif',
                lineHeight: 1.1,
                textShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
                color: 'white',
              }}
            >
              ResourceWise
            </Typography>

            {/* Descriptive Text */}
            <Typography
              variant="h5"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                mb: 6,
                fontWeight: 300,
                fontSize: { xs: '1.2rem', md: '1.5rem' },
                lineHeight: 1.6,
                fontFamily: 'Lato, sans-serif',
                textShadow: '0 2px 10px rgba(0, 0, 0, 0.3)',
                maxWidth: '800px',
                mx: 'auto',
              }}
            >
              AI-powered resource allocation platform that transforms your
              project management with intelligent team assignments, skill
              matching, and real-time insights for better decision making.
            </Typography>

            {/* Try it out Button */}
            <CustomButton
              customVariant="primary"
              size="large"
              onClick={() => navigate('/chat')}
              sx={{
                px: 8,
                py: 3,
                fontSize: '1.3rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #ffffff, #f8f9fa)',
                color: '#0A014F',
                border: 'none',
                borderRadius: 3,
                boxShadow: '0 8px 24px rgba(255, 255, 255, 0.2)',
                textTransform: 'none',
                minWidth: '200px',
                '&:hover': {
                  background: 'linear-gradient(135deg, #f8f9fa, #e9ecef)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 12px 28px rgba(255, 255, 255, 0.3)',
                },
              }}
            >
              Try it out
            </CustomButton>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing;
