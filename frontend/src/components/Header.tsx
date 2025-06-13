import React from 'react';
import { AppBar, Toolbar, Typography, Container, Stack } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { CustomButton } from './common';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isOnChatPage = location.pathname === '/chat';

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: '#1e1b4b' }}>
      <Container maxWidth="lg">
        <Toolbar sx={{ justifyContent: 'space-between', py: 1 }}>
          <Typography
            variant="h6"
            component="div"
            onClick={() => handleNavigation('/')}
            sx={{
              fontWeight: 700,
              color: 'white',
              fontSize: '1.5rem',
              cursor: 'pointer',
              '&:hover': {
                opacity: 0.8,
              },
            }}
          >
            ResourceWise
          </Typography>

          <Stack direction="row" spacing={2}>
            {!isOnChatPage && (
              <CustomButton
                customVariant="secondary"
                size="small"
                onClick={() => handleNavigation('/chat')}
                sx={{
                  backgroundColor: 'transparent',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                AI Assistant
              </CustomButton>
            )}
            {isOnChatPage && (
              <CustomButton
                customVariant="secondary"
                size="small"
                onClick={() => handleNavigation('/')}
                sx={{
                  backgroundColor: 'transparent',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                Home
              </CustomButton>
            )}
            <CustomButton
              customVariant="secondary"
              size="small"
              sx={{
                backgroundColor: 'transparent',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              Login
            </CustomButton>
            <CustomButton customVariant="primary" size="small">
              Get Started
            </CustomButton>
          </Stack>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
