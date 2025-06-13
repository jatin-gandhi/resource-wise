import React from 'react';
import { Box, Container, Typography, Stack, Avatar } from '@mui/material';
import { CheckCircleOutline as CheckIcon } from '@mui/icons-material';
import { CustomCard } from './common';

const About: React.FC = () => {
  return (
    <Box
      component="section"
      id="about"
      sx={{
        py: { xs: 8, md: 12 },
        backgroundColor: '#f9fafb',
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
            gap: { xs: 6, lg: 12 },
            alignItems: 'center',
          }}
        >
          <Stack spacing={4}>
            <Typography
              variant="h2"
              component="h2"
              sx={{
                fontSize: { xs: '2rem', md: '2.5rem' },
                fontWeight: 700,
                color: '#111827',
              }}
            >
              Revolutionizing Resource Management with Intelligence
            </Typography>

            <Typography
              variant="h6"
              component="p"
              sx={{
                color: '#6b7280',
                lineHeight: 1.7,
                fontSize: '1.125rem',
              }}
            >
              ResourceWise was born from the understanding that traditional
              resource allocation methods are inefficient and time-consuming.
              Our platform leverages AI to transform how organizations manage
              their most valuable asset: their people.
            </Typography>

            <Typography
              variant="body1"
              component="p"
              sx={{
                color: '#6b7280',
                lineHeight: 1.7,
                fontSize: '1.125rem',
              }}
            >
              By analyzing skills, experience, and team dynamics, ResourceWise
              creates optimal team compositions that drive project success while
              maximizing employee satisfaction.
            </Typography>

            <Stack spacing={3}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: '#dbeafe',
                    color: '#2563eb',
                  }}
                >
                  <CheckIcon sx={{ fontSize: 20 }} />
                </Avatar>
                <Box>
                  <Typography
                    variant="h6"
                    sx={{ color: '#111827', fontWeight: 600, mb: 0.5 }}
                  >
                    Data-Driven Decisions
                  </Typography>
                  <Typography variant="body1" sx={{ color: '#6b7280' }}>
                    Make informed resource allocation decisions backed by
                    comprehensive analytics and AI insights.
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: '#dbeafe',
                    color: '#2563eb',
                  }}
                >
                  <CheckIcon sx={{ fontSize: 20 }} />
                </Avatar>
                <Box>
                  <Typography
                    variant="h6"
                    sx={{ color: '#111827', fontWeight: 600, mb: 0.5 }}
                  >
                    Scalable Solution
                  </Typography>
                  <Typography variant="body1" sx={{ color: '#6b7280' }}>
                    From startups to enterprises, our platform scales to meet
                    your organization's unique needs.
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: '#dbeafe',
                    color: '#2563eb',
                  }}
                >
                  <CheckIcon sx={{ fontSize: 20 }} />
                </Avatar>
                <Box>
                  <Typography
                    variant="h6"
                    sx={{ color: '#111827', fontWeight: 600, mb: 0.5 }}
                  >
                    Employee-Centric
                  </Typography>
                  <Typography variant="body1" sx={{ color: '#6b7280' }}>
                    Optimize for both project success and employee growth,
                    satisfaction, and career development.
                  </Typography>
                </Box>
              </Box>
            </Stack>
          </Stack>

          <CustomCard>
            <Stack spacing={4}>
              <Box sx={{ backgroundColor: '#dbeafe', borderRadius: 2, p: 3 }}>
                <Typography
                  variant="h5"
                  component="h4"
                  sx={{ color: '#111827', fontWeight: 600, mb: 1 }}
                >
                  Our Mission
                </Typography>
                <Typography variant="body1" sx={{ color: '#6b7280' }}>
                  To empower organizations with intelligent resource management
                  tools that maximize both project outcomes and human potential
                  through the power of AI.
                </Typography>
              </Box>

              <Box sx={{ backgroundColor: '#e0e7ff', borderRadius: 2, p: 3 }}>
                <Typography
                  variant="h5"
                  component="h4"
                  sx={{ color: '#111827', fontWeight: 600, mb: 1 }}
                >
                  Our Vision
                </Typography>
                <Typography variant="body1" sx={{ color: '#6b7280' }}>
                  A world where every employee is perfectly matched to projects
                  that challenge, inspire, and develop their skills while
                  driving organizational success.
                </Typography>
              </Box>

              <Box sx={{ backgroundColor: '#dbeafe', borderRadius: 2, p: 3 }}>
                <Typography
                  variant="h5"
                  component="h4"
                  sx={{ color: '#111827', fontWeight: 600, mb: 1 }}
                >
                  Our Values
                </Typography>
                <Typography variant="body1" sx={{ color: '#6b7280' }}>
                  Innovation, transparency, employee empowerment, and
                  data-driven decision making are at the core of everything we
                  build and deliver.
                </Typography>
              </Box>
            </Stack>
          </CustomCard>
        </Box>
      </Container>
    </Box>
  );
};

export default About;
