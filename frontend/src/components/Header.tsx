import React from 'react';
import { AppBar, Toolbar, Typography, Container, Stack } from '@mui/material';
import { CustomButton } from './common';

const Header: React.FC = () => {
  return (
    <AppBar position="static" sx={{ backgroundColor: '#1e1b4b' }}>
      <Container maxWidth="lg">
        <Toolbar sx={{ justifyContent: 'space-between', py: 1 }}>
          <Typography
            variant="h6"
            component="div"
            sx={{
              fontWeight: 700,
              color: 'white',
              fontSize: '1.5rem',
            }}
          >
            ResourceWise
          </Typography>

          <Stack direction="row" spacing={2}>
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
