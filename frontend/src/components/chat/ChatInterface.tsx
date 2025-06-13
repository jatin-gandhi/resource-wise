import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'bot' | 'error' | 'system';
  timestamp: Date;
  metadata?: any;
}

interface ChatInterfaceProps {
  onNewSession?: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onNewSession }) => {
  const theme = useTheme();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize WebSocket connection
  useEffect(() => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    connectWebSocket(newSessionId);

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const connectWebSocket = (sessionId: string) => {
    try {
      const wsUrl = `ws://localhost:8001/api/v1/chat/ws/${sessionId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
        addSystemMessage('Connected to ResourceWise AI Assistant');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
        addSystemMessage('Disconnected from AI Assistant');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addErrorMessage('Connection error. Please refresh the page.');
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      addErrorMessage('Failed to connect to AI Assistant');
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'chat_response':
        addBotMessage(data.content, data.metadata);
        setIsLoading(false);
        break;
      case 'streaming_start':
        setIsLoading(true);
        break;
      case 'streaming_chunk':
        updateLastBotMessage(data.content);
        break;
      case 'streaming_complete':
        setIsLoading(false);
        break;
      case 'error':
        addErrorMessage(data.message);
        setIsLoading(false);
        break;
      case 'pong':
        // Handle ping/pong for connection health
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const addSystemMessage = (content: string) => {
    const message: Message = {
      id: generateMessageId(),
      content,
      type: 'system',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, message]);
  };

  const addUserMessage = (content: string) => {
    const message: Message = {
      id: generateMessageId(),
      content,
      type: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, message]);
  };

  const addBotMessage = (content: string, metadata?: any) => {
    const message: Message = {
      id: generateMessageId(),
      content,
      type: 'bot',
      timestamp: new Date(),
      metadata,
    };
    setMessages(prev => [...prev, message]);
  };

  const addErrorMessage = (content: string) => {
    const message: Message = {
      id: generateMessageId(),
      content,
      type: 'error',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, message]);
  };

  const updateLastBotMessage = (newContent: string) => {
    setMessages(prev => {
      const lastMessage = prev[prev.length - 1];
      if (lastMessage && lastMessage.type === 'bot') {
        return [
          ...prev.slice(0, -1),
          { ...lastMessage, content: lastMessage.content + newContent }
        ];
      } else {
        // Create new bot message if last message wasn't from bot
        return [...prev, {
          id: generateMessageId(),
          content: newContent,
          type: 'bot' as const,
          timestamp: new Date(),
        }];
      }
    });
  };

  const generateMessageId = (): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || !isConnected || isLoading) return;

    const message = inputValue.trim();
    addUserMessage(message);
    setInputValue('');
    setIsLoading(true);

    // Send message via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat_message',
        message: message,
      }));
    } else {
      addErrorMessage('Not connected to AI Assistant');
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    addSystemMessage('Chat cleared');
  };

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user';
    const isSystem = message.type === 'system';
    const isError = message.type === 'error';

    return (
      <ListItem
        key={message.id}
        sx={{
          display: 'flex',
          flexDirection: isUser ? 'row-reverse' : 'row',
          alignItems: 'flex-start',
          gap: 1,
          mb: 1,
        }}
      >
        <Avatar
          sx={{
            bgcolor: isUser ? theme.palette.primary.main : 
                     isError ? theme.palette.error.main :
                     isSystem ? theme.palette.info.main :
                     theme.palette.secondary.main,
            width: 32,
            height: 32,
          }}
        >
          {isUser ? <PersonIcon fontSize="small" /> : 
           isSystem ? '🔧' : <BotIcon fontSize="small" />}
        </Avatar>
        
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '70%',
            bgcolor: isUser ? theme.palette.primary.light :
                     isError ? theme.palette.error.light :
                     isSystem ? theme.palette.info.light :
                     theme.palette.grey[100],
            color: isUser ? theme.palette.primary.contrastText :
                   isError ? theme.palette.error.contrastText :
                   theme.palette.text.primary,
          }}
        >
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {message.content}
          </Typography>
          
          {message.metadata && (
            <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {message.metadata.intent && (
                <Chip 
                  label={`Intent: ${message.metadata.intent}`} 
                  size="small" 
                  variant="outlined" 
                />
              )}
              {message.metadata.execution_time_ms && (
                <Chip 
                  label={`${message.metadata.execution_time_ms}ms`} 
                  size="small" 
                  variant="outlined" 
                />
              )}
            </Box>
          )}
          
          <Typography 
            variant="caption" 
            sx={{ 
              display: 'block', 
              mt: 0.5, 
              opacity: 0.7,
              textAlign: isUser ? 'right' : 'left'
            }}
          >
            {message.timestamp.toLocaleTimeString()}
          </Typography>
        </Paper>
      </ListItem>
    );
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: theme.palette.background.default,
      }}
    >
      {/* Header */}
      <Paper
        elevation={2}
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderRadius: 0,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <BotIcon color="primary" />
          <Typography variant="h6" color="primary">
            ResourceWise AI Assistant
          </Typography>
          <Chip
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            size="small"
          />
        </Box>
        
        <IconButton onClick={clearChat} color="primary">
          <ClearIcon />
        </IconButton>
      </Paper>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 1,
        }}
      >
        <List sx={{ width: '100%' }}>
          {messages.map(renderMessage)}
          {isLoading && (
            <ListItem sx={{ justifyContent: 'center' }}>
              <CircularProgress size={24} />
              <Typography variant="body2" sx={{ ml: 1 }}>
                AI is thinking...
              </Typography>
            </ListItem>
          )}
        </List>
        <div ref={messagesEndRef} />
      </Box>

      <Divider />

      {/* Input Area */}
      <Paper
        elevation={3}
        sx={{
          p: 2,
          display: 'flex',
          gap: 1,
          alignItems: 'flex-end',
          borderRadius: 0,
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about resource allocation, employee availability, project teams..."
          disabled={!isConnected || isLoading}
          variant="outlined"
          size="small"
        />
        <IconButton
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || !isConnected || isLoading}
          color="primary"
          sx={{ p: 1 }}
        >
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  );
};

export default ChatInterface; 