import React from 'react';
import { Box, Container, Typography, Stack, Avatar } from '@mui/material';
import {
  PsychologyOutlined as BrainIcon,
  AnalyticsOutlined as AnalyticsIcon,
  GroupsOutlined as TeamIcon,
  TrendingUpOutlined as GrowthIcon,
  SecurityOutlined as SecurityIcon,
  IntegrationInstructionsOutlined as IntegrationIcon,
} from '@mui/icons-material';
import { CustomCard } from './common';

const features = [
  {
    icon: BrainIcon,
    title: 'AI-Powered Matching',
    description:
      'Our advanced algorithms analyze skills, experience, and availability to match the perfect resources to your projects.',
    color: '#2563eb',
  },
  {
    icon: AnalyticsIcon,
    title: 'Real-time Analytics',
    description:
      'Get instant insights into resource utilization, project progress, and team performance with our comprehensive dashboard.',
    color: '#7c3aed',
  },
  {
    icon: TeamIcon,
    title: 'Team Optimization',
    description:
      'Build high-performing teams by leveraging data-driven insights about team dynamics and collaboration patterns.',
    color: '#059669',
  },
  {
    icon: GrowthIcon,
    title: 'Predictive Planning',
    description:
      'Forecast future resource needs and identify potential bottlenecks before they impact your projects.',
    color: '#dc2626',
  },
  {
    icon: SecurityIcon,
    title: 'Enterprise Security',
    description:
      'Bank-grade security with SOC 2 compliance, SSO integration, and role-based access control.',
    color: '#ea580c',
  },
  {
    icon: IntegrationIcon,
    title: 'Seamless Integration',
    description:
      'Connect with your existing tools and workflows through our extensive API and pre-built integrations.',
    color: '#0891b2',
  },
];

const Features: React.FC = () => {
  return (
    <Box
      component="section"
      id="features"
      sx={{
        py: { xs: 8, md: 12 },
        backgroundColor: '#f9fafb',
      }}
    >
      <Container maxWidth="lg">
        <Stack spacing={6} alignItems="center">
          <Box textAlign="center" maxWidth="3xl">
            <Typography
              variant="h2"
              component="h2"
              sx={{
                fontSize: { xs: '2rem', md: '2.5rem' },
                fontWeight: 700,
                color: '#111827',
                mb: 2,
              }}
            >
              Powerful Features for Modern Teams
            </Typography>
            <Typography
              variant="h6"
              component="p"
              sx={{
                color: '#6b7280',
                lineHeight: 1.6,
              }}
            >
              Everything you need to optimize your resource allocation and
              maximize team productivity
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                md: 'repeat(2, 1fr)',
                lg: 'repeat(3, 1fr)',
              },
              gap: 4,
              width: '100%',
            }}
          >
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <CustomCard key={index} hover>
                  <Stack spacing={3} alignItems="center" textAlign="center">
                    <Avatar
                      sx={{
                        width: 64,
                        height: 64,
                        backgroundColor: feature.color,
                        color: 'white',
                      }}
                    >
                      <IconComponent sx={{ fontSize: 32 }} />
                    </Avatar>

                    <Typography
                      variant="h5"
                      component="h3"
                      sx={{
                        fontWeight: 600,
                        color: '#111827',
                      }}
                    >
                      {feature.title}
                    </Typography>

                    <Typography
                      variant="body1"
                      sx={{
                        color: '#6b7280',
                        lineHeight: 1.6,
                      }}
                    >
                      {feature.description}
                    </Typography>
                  </Stack>
                </CustomCard>
              );
            })}
          </Box>
        </Stack>
      </Container>
    </Box>
  );
};

export default Features;
