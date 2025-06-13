import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Stack,
  Box,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { Logout } from '@mui/icons-material';
import { CustomButton } from './common';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const navigationItems = [
    { label: 'Chat', path: '/chat' },
    { label: 'Employees', path: '/employees' },
    { label: 'Projects', path: '/projects' },
    { label: 'Allocations', path: '/allocations' },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleAvatarClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleClose();
    navigate('/');
  };

  return (
    <AppBar position="static" elevation={0}>
      <Container maxWidth="lg">
        <Toolbar sx={{ justifyContent: 'space-between', py: 1 }}>
          <Typography
            variant="h6"
            component="div"
            onClick={() => navigate('/')}
            sx={{
              fontWeight: 700,
              fontSize: '1.5rem',
              cursor: 'pointer',
              transition: 'color 0.2s ease-in-out',
              '&:hover': {
                color: 'primary.light',
              },
            }}
          >
            ResourceWise
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Navigation Items */}
            <Stack direction="row" spacing={1} sx={{ mr: 2 }}>
              {navigationItems.map(item => (
                <CustomButton
                  key={item.path}
                  customVariant={isActive(item.path) ? 'primary' : 'ghost'}
                  size="small"
                  onClick={() => navigate(item.path)}
                  sx={{
                    minWidth: 'auto',
                    px: 2,
                    py: 1,
                    fontSize: '0.875rem',
                  }}
                >
                  {item.label}
                </CustomButton>
              ))}
            </Stack>

            {/* User Avatar */}
            <Avatar
              onClick={handleAvatarClick}
              sx={{
                width: 36,
                height: 36,
                cursor: 'pointer',
                bgcolor: 'primary.main',
                fontSize: '0.875rem',
                fontWeight: 600,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  bgcolor: 'primary.dark',
                  transform: 'scale(1.05)',
                },
              }}
            >
              U
            </Avatar>

            {/* Dropdown Menu */}
            <Menu
              anchorEl={anchorEl}
              open={open}
              onClose={handleClose}
              onClick={handleClose}
              PaperProps={{
                elevation: 3,
                sx: {
                  overflow: 'visible',
                  filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                  mt: 1.5,
                  minWidth: 120,
                  '& .MuiAvatar-root': {
                    width: 32,
                    height: 32,
                    ml: -0.5,
                    mr: 1,
                  },
                  '&:before': {
                    content: '""',
                    display: 'block',
                    position: 'absolute',
                    top: 0,
                    right: 14,
                    width: 10,
                    height: 10,
                    bgcolor: 'background.paper',
                    transform: 'translateY(-50%) rotate(45deg)',
                    zIndex: 0,
                  },
                },
              }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <Logout fontSize="small" />
                </ListItemIcon>
                <ListItemText>Logout</ListItemText>
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
