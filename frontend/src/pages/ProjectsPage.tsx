import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import { Assignment } from '@mui/icons-material';
import Layout from '../components/layout/Layout';

const ProjectsPage: React.FC = () => {
  return (
    <Layout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            py: 8,
          }}
        >
          <Box
            sx={{
              width: 120,
              height: 120,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #006EFF, #26266D)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 3,
              boxShadow: '0 8px 32px rgba(0, 110, 255, 0.3)',
            }}
          >
            <Assignment sx={{ fontSize: 60, color: 'white' }} />
          </Box>

          <Typography
            variant="h3"
            component="h1"
            sx={{
              fontWeight: 700,
              color: 'text.primary',
              mb: 2,
              fontFamily: 'Lato, sans-serif',
            }}
          >
            Projects
          </Typography>

          <Typography
            variant="h6"
            sx={{
              color: 'text.secondary',
              mb: 4,
              fontFamily: 'Lato, sans-serif',
            }}
          >
            Coming Soon
          </Typography>

          <Typography
            variant="body1"
            sx={{
              color: 'text.secondary',
              maxWidth: 600,
              lineHeight: 1.6,
              fontFamily: 'Lato, sans-serif',
            }}
          >
            This section will provide comprehensive project management
            capabilities including project creation, timeline tracking, resource
            requirements, and progress monitoring. Stay tuned for advanced
            project management features.
          </Typography>
        </Box>
      </Container>
    </Layout>
  );
};

export default ProjectsPage;
