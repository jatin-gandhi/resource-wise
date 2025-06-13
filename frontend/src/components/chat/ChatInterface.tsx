import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Typography,
  Avatar,
  Stack,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as UserIcon,
} from '@mui/icons-material';
import { CustomButton } from '../common';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  type?: 'text' | 'thinking' | 'error';
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! How can I help you today?',
      sender: 'ai',
      timestamp: new Date(),
      type: 'text',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Add thinking message
    const thinkingMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: 'Thinking...',
      sender: 'ai',
      timestamp: new Date(),
      type: 'thinking',
    };

    setMessages((prev) => [...prev, thinkingMessage]);

    // Simulate API call
    try {
      // TODO: Replace with actual API call to backend
      await new Promise(resolve => setTimeout(resolve, 2000));

      const aiResponse: Message = {
        id: (Date.now() + 2).toString(),
        content: `I received your message: "${userMessage.content}". The AI system is being set up and will provide intelligent responses soon!`,
        sender: 'ai',
        timestamp: new Date(),
        type: 'text',
      };

      setMessages((prev) =>
        prev.filter((msg) => msg.type !== 'thinking').concat(aiResponse)
      );
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 3).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
        type: 'error',
      };

      setMessages((prev) =>
        prev.filter((msg) => msg.type !== 'thinking').concat(errorMessage)
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
    const isUser = message.sender === 'user';
    const isThinking = message.type === 'thinking';
    const isError = message.type === 'error';

    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Stack
          direction={isUser ? 'row-reverse' : 'row'}
          spacing={1}
          alignItems="flex-start"
          sx={{ maxWidth: '70%' }}
        >
          <Avatar
            sx={{
              bgcolor: isUser ? 'warning.main' : 'primary.main',
              width: 32,
              height: 32,
            }}
          >
            {isUser ? (
              <UserIcon fontSize="small" />
            ) : (
              <AIIcon fontSize="small" />
            )}
          </Avatar>

          <Paper
            elevation={1}
            sx={{
              p: 2,
              bgcolor: isUser
                ? 'primary.main'
                : isError
                  ? 'error.light'
                  : 'background.paper',
              color: isUser ? 'primary.contrastText' : 'text.primary',
              borderRadius: 2,
              border: isError ? '1px solid' : 'none',
              borderColor: isError ? 'error.main' : 'transparent',
            }}
          >
            {isThinking ? (
              <Stack direction="row" alignItems="center" spacing={1}>
                <CircularProgress size={16} />
                <Typography variant="body2">{message.content}</Typography>
              </Stack>
            ) : (
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {message.content}
              </Typography>
            )}

            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 1,
                opacity: 0.7,
                fontSize: '0.75rem',
              }}
            >
              {message.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Typography>
          </Paper>
        </Stack>
      </Box>
    );
  };

  return (
    <Container
      maxWidth="md"
      sx={{ height: '100vh', display: 'flex', flexDirection: 'column', py: 2 }}
    >
      {/* Chat Header */}
      <Paper elevation={1} sx={{ p: 2, mb: 2, borderRadius: 2 }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <AIIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              AI Assistant
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                label="Online"
                size="small"
                color="success"
                sx={{ height: 20, fontSize: '0.75rem' }}
              />
              <Typography variant="caption" color="text.secondary">
                Ready to help with resource allocation
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </Paper>

      {/* Messages Container */}
      <Paper
        elevation={1}
        sx={{
          flex: 1,
          p: 2,
          mb: 2,
          borderRadius: 2,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            pr: 1,
            '&::-webkit-scrollbar': {
              width: 6,
            },
            '&::-webkit-scrollbar-track': {
              backgroundColor: 'secondary.light',
              borderRadius: 3,
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: 'secondary.main',
              borderRadius: 3,
            },
          }}
        >
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </Box>
      </Paper>

      {/* Input Area */}
      <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
        <Stack direction="row" spacing={1} alignItems="flex-end">
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Enter prompt for the Librarian"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
          />
          <CustomButton
            customVariant="primary"
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            sx={{
              minWidth: 48,
              height: 40,
              borderRadius: 2,
            }}
          >
            <SendIcon fontSize="small" />
          </CustomButton>
        </Stack>
      </Paper>
    </Container>
  );
};

export default ChatInterface;
