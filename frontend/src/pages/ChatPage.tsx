import React from 'react';
import { Box, Container, Typography, Paper } from '@mui/material';
import ChatInterface from '../components/chat/ChatInterface';

const ChatPage: React.FC = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Container maxWidth="lg" sx={{ flex: 1, p: 0 }}>
        <ChatInterface />
      </Container>
    </Box>
  );
};

export default ChatPage; 