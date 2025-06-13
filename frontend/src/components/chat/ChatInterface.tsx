/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Drawer,
  AppBar,
  Toolbar,
  Avatar,
  Menu,
  MenuItem,
  Chip,
  CircularProgress,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  Add as AddIcon,
  Menu as MenuIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  ContentCopy as CopyIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import {
  createConversation,
  setActiveConversation,
  deleteConversation,
  selectActiveConversation,
  selectConversations,
  selectIsStreaming,
  selectChatError,
} from '../../store/slices/chatSlice';
import { useStreamingChat } from '../../hooks/useStreamingChat';
import { useChatPersistence } from '../../hooks/useChatPersistence';
import { useNavigate } from 'react-router-dom';
import type { RootState } from '../../store';

// Import highlight.js CSS for code syntax highlighting
import 'highlight.js/styles/github-dark.css';

const DRAWER_WIDTH = 280;

// Custom component for code blocks with copy functionality
const CodeBlock = ({ children, className, ...props }: any) => {
  const [copied, setCopied] = useState(false);
  const language = className?.replace('language-', '') || '';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(children);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <Box sx={{ position: 'relative', mb: 2 }}>
      {language && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: '#2d3748',
            color: 'white',
            px: 2,
            py: 1,
            fontSize: '0.75rem',
            fontWeight: 500,
            borderTopLeftRadius: '6px',
            borderTopRightRadius: '6px',
          }}
        >
          <span>{language.toUpperCase()}</span>
          <Tooltip title={copied ? 'Copied!' : 'Copy code'}>
            <IconButton
              size="small"
              onClick={handleCopy}
              sx={{
                color: 'white',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' },
              }}
            >
              <CopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )}
      <pre
        style={{
          backgroundColor: '#1a202c',
          color: '#e2e8f0',
          padding: '1rem',
          borderRadius: language ? '0 0 6px 6px' : '6px',
          overflow: 'auto',
          margin: 0,
          fontSize: '0.875rem',
          lineHeight: 1.5,
        }}
        {...props}
      >
        <code className={className}>{children}</code>
      </pre>
    </Box>
  );
};

// Custom component for inline code
const InlineCode = ({ children, ...props }: any) => (
  <code
    style={{
      backgroundColor: 'rgba(175, 184, 193, 0.2)',
      color: '#e53e3e',
      padding: '0.2em 0.4em',
      borderRadius: '3px',
      fontSize: '0.875em',
      fontFamily: 'Monaco, Consolas, "Courier New", monospace',
      fontWeight: 600,
    }}
    {...props}
  >
    {children}
  </code>
);

const ChatInterface: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const activeConversation = useSelector((state: RootState) =>
    selectActiveConversation(state)
  );
  const conversations = useSelector((state: RootState) =>
    selectConversations(state)
  );
  const isStreaming = useSelector((state: RootState) =>
    selectIsStreaming(state)
  );
  const error = useSelector((state: RootState) => selectChatError(state));

  // Debug: Log when activeConversation changes
  // useEffect(() => {
  //   if (activeConversation) {
  //     console.log('Active conversation updated:', {
  //       id: activeConversation.id,
  //       messageCount: activeConversation.messages.length,
  //       lastMessage: activeConversation.messages[activeConversation.messages.length - 1]?.content?.slice(0, 50) + '...'
  //     });
  //   }
  // }, [activeConversation]);

  const [message, setMessage] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedConversationId, setSelectedConversationId] = useState<
    string | null
  >(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage } = useStreamingChat();
  useChatPersistence();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConversation?.messages]);

  // Create initial conversation if none exists
  useEffect(() => {
    if (conversations.length === 0) {
      dispatch(createConversation({ title: 'New Conversation' }));
    }
  }, [conversations.length, dispatch]);

  const handleSendMessage = async () => {
    if (!message.trim() || !activeConversation || isStreaming) return;

    const messageText = message.trim();
    setMessage('');

    try {
      await sendMessage(
        activeConversation.id,
        messageText,
        activeConversation.session_id
      );
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewConversation = () => {
    dispatch(createConversation({ title: 'New Conversation' }));
  };

  const handleSelectConversation = (conversationId: string) => {
    dispatch(setActiveConversation(conversationId));
  };

  const handleDeleteConversation = (conversationId: string) => {
    dispatch(deleteConversation(conversationId));
    setAnchorEl(null);
  };

  const handleMenuClick = (
    event: React.MouseEvent<HTMLElement>,
    conversationId: string
  ) => {
    setAnchorEl(event.currentTarget);
    setSelectedConversationId(conversationId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedConversationId(null);
  };

  const formatTimestamp = (timestamp: string) => {
    const now = new Date();
    const timestampDate = new Date(timestamp);
    const diff = now.getTime() - timestampDate.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return timestampDate.toLocaleDateString();
  };

  const renderMessage = (msg: any) => {
    return (
      <Box
        key={msg.id}
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 2,
          mb: 3,
          px: 2,
          animation: 'fadeInUp 0.3s ease-out',
          '@keyframes fadeInUp': {
            '0%': {
              opacity: 0,
              transform: 'translateY(20px)',
            },
            '100%': {
              opacity: 1,
              transform: 'translateY(0)',
            },
          },
        }}
      >
        <Avatar
          sx={{
            width: 36,
            height: 36,
            bgcolor: msg.role === 'user' ? 'primary.main' : 'secondary.main',
            boxShadow: 2,
            transition: 'transform 0.2s ease-in-out',
            '&:hover': {
              transform: 'scale(1.05)',
            },
          }}
        >
          {msg.role === 'user' ? <PersonIcon /> : <BotIcon />}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            {msg.role === 'user' ? 'You' : 'ResourceWise AI'}
            <Typography
              component="span"
              variant="caption"
              sx={{ ml: 1, opacity: 0.7 }}
            >
              {formatTimestamp(msg.timestamp)}
            </Typography>
          </Typography>

          {/* Enhanced markdown rendering for AI responses */}
          {msg.role === 'assistant' ? (
            <Paper
              elevation={0}
              sx={{
                p: 2,
                backgroundColor: 'grey.50',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'grey.200',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  boxShadow: 1,
                  borderColor: 'grey.300',
                },
                '& .markdown-content': {
                  fontFamily: 'inherit',
                  fontSize: '0.95rem',
                  lineHeight: 1.6,
                  color: 'text.primary',
                },
                '& .markdown-content h1': {
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  marginTop: '1.5rem',
                  marginBottom: '0.75rem',
                  color: 'primary.main',
                  borderBottom: '2px solid',
                  borderColor: 'primary.main',
                  paddingBottom: '0.5rem',
                },
                '& .markdown-content h2': {
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  marginTop: '1.25rem',
                  marginBottom: '0.5rem',
                  color: 'text.primary',
                },
                '& .markdown-content h3': {
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  marginTop: '1rem',
                  marginBottom: '0.5rem',
                  color: 'text.primary',
                },
                '& .markdown-content p': {
                  marginBottom: '1rem',
                  '&:last-child': { marginBottom: 0 },
                },
                '& .markdown-content ul, & .markdown-content ol': {
                  marginBottom: '1rem',
                  paddingLeft: '1.5rem',
                },
                '& .markdown-content li': {
                  marginBottom: '0.25rem',
                },
                '& .markdown-content blockquote': {
                  borderLeft: '4px solid',
                  borderColor: 'primary.main',
                  paddingLeft: '1rem',
                  marginLeft: 0,
                  marginBottom: '1rem',
                  backgroundColor: 'primary.50',
                  padding: '1rem',
                  borderRadius: '0 6px 6px 0',
                  fontStyle: 'italic',
                },
                '& .markdown-content table': {
                  borderCollapse: 'collapse',
                  width: '100%',
                  marginBottom: '1rem',
                  border: '1px solid',
                  borderColor: 'grey.300',
                  borderRadius: '6px',
                  overflow: 'hidden',
                },
                '& .markdown-content th': {
                  backgroundColor: 'primary.50',
                  fontWeight: 600,
                  padding: '0.75rem',
                  textAlign: 'left',
                  borderBottom: '1px solid',
                  borderColor: 'grey.300',
                },
                '& .markdown-content td': {
                  padding: '0.75rem',
                  borderBottom: '1px solid',
                  borderColor: 'grey.200',
                },
                '& .markdown-content strong': {
                  fontWeight: 700,
                  color: 'text.primary',
                },
                '& .markdown-content em': {
                  fontStyle: 'italic',
                  color: 'text.secondary',
                },
                '& .markdown-content hr': {
                  border: 'none',
                  borderTop: '2px solid',
                  borderColor: 'grey.300',
                  margin: '2rem 0',
                },
              }}
            >
              <div className="markdown-content">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                  components={{
                    pre: CodeBlock,
                    code: ({ children, className, ...props }: any) =>
                      className ? (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      ) : (
                        <InlineCode {...props}>{children}</InlineCode>
                      ),
                  }}
                >
                  {msg.content || '[No content]'}
                </ReactMarkdown>
              </div>
              {msg.isStreaming && (
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    mt: 2,
                    gap: 1,
                    p: 1,
                    backgroundColor: 'primary.50',
                    borderRadius: 1,
                    border: '1px solid',
                    borderColor: 'primary.200',
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      gap: 0.5,
                      '& .dot': {
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        backgroundColor: 'primary.main',
                        animation: 'pulse 1.4s ease-in-out infinite both',
                      },
                      '& .dot:nth-of-type(1)': { animationDelay: '-0.32s' },
                      '& .dot:nth-of-type(2)': { animationDelay: '-0.16s' },
                      '@keyframes pulse': {
                        '0%, 80%, 100%': {
                          transform: 'scale(0)',
                        },
                        '40%': {
                          transform: 'scale(1)',
                        },
                      },
                    }}
                  >
                    <div className="dot" />
                    <div className="dot" />
                    <div className="dot" />
                  </Box>
                  <Typography
                    variant="caption"
                    color="primary.main"
                    fontWeight={500}
                  >
                    AI is thinking...
                  </Typography>
                </Box>
              )}
            </Paper>
          ) : (
            <Paper
              elevation={0}
              sx={{
                p: 2,
                backgroundColor: 'primary.50',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'primary.200',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  boxShadow: 1,
                  borderColor: 'primary.300',
                },
              }}
            >
              <Typography
                variant="body1"
                sx={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  lineHeight: 1.6,
                }}
              >
                {msg.content || '[No content]'}
              </Typography>
            </Paper>
          )}
        </Box>
      </Box>
    );
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Purple Themed Sidebar */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={drawerOpen}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            background: 'linear-gradient(180deg, #130738 0%, #000000 100%)',
            color: 'white',
            borderRight: 'none',
            boxShadow: '4px 0 20px rgba(19, 7, 56, 0.5)',
          },
        }}
      >
        {/* Header with Logo/Title */}
        <Box sx={{ p: 3, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              background: 'linear-gradient(45deg, #ffffff 30%, #e0e7ff 90%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2,
            }}
          >
            ResourceWise AI
          </Typography>
          <Box
            component="button"
            onClick={handleNewConversation}
            sx={{
              width: '100%',
              display: 'flex',
              justifyContent: 'flex-start',
              alignItems: 'center',
              gap: 1.5,
              p: 2,
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              backdropFilter: 'blur(10px)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                transform: 'translateY(-1px)',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              },
            }}
          >
            <AddIcon sx={{ fontSize: 20 }} />
            <Typography variant="body2" fontWeight={500}>
              New Conversation
            </Typography>
          </Box>
        </Box>

        {/* Conversations List */}
        <List sx={{ flex: 1, overflow: 'auto', p: 1 }}>
          {conversations.map((conv: any) => (
            <ListItem key={conv.id} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={conv.id === activeConversation?.id}
                onClick={() => handleSelectConversation(conv.id)}
                sx={{
                  borderRadius: 2,
                  mx: 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    transform: 'translateX(4px)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    backdropFilter: 'blur(10px)',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.25)',
                    },
                  },
                }}
              >
                <ListItemText
                  primary={conv.title}
                  secondary={formatTimestamp(conv.updated_at)}
                  primaryTypographyProps={{
                    noWrap: true,
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    color: 'white',
                  }}
                  secondaryTypographyProps={{
                    fontSize: '0.75rem',
                    color: 'rgba(255, 255, 255, 0.7)',
                  }}
                />
                <IconButton
                  size="small"
                  onClick={e => {
                    e.stopPropagation();
                    handleMenuClick(e, conv.id);
                  }}
                  sx={{
                    color: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'white',
                    },
                  }}
                >
                  <MoreVertIcon fontSize="small" />
                </IconButton>
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        {/* Footer with subtle branding */}
        <Box
          sx={{
            p: 2,
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            textAlign: 'center',
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255, 255, 255, 0.6)',
              fontSize: '0.7rem',
            }}
          >
            Powered by AI • v1.0
          </Typography>
        </Box>
      </Drawer>

      {/* Main Chat Area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          ml: drawerOpen ? 0 : `-${DRAWER_WIDTH}px`,
          transition: 'margin-left 0.3s',
        }}
      >
        {/* Header */}
        <AppBar
          position="static"
          elevation={1}
          sx={{
            background: 'linear-gradient(90deg, #130738 0%, #000000 100%)',
            color: 'white',
          }}
        >
          <Toolbar>
            <IconButton
              edge="start"
              onClick={() => setDrawerOpen(!drawerOpen)}
              sx={{ mr: 2, color: 'white' }}
            >
              <MenuIcon />
            </IconButton>
            <IconButton
              onClick={() => navigate('/')}
              sx={{
                mr: 2,
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h6" sx={{ flex: 1, color: 'white' }}>
              {activeConversation?.title || 'ResourceWise AI'}
            </Typography>
            {isStreaming && (
              <Chip
                label="Thinking..."
                size="small"
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                }}
                icon={<CircularProgress size={16} sx={{ color: 'white' }} />}
              />
            )}
          </Toolbar>
        </AppBar>

        {/* Messages Area */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            py: 2,
            backgroundColor: 'background.default',
          }}
        >
          {error && (
            <Alert severity="error" sx={{ mx: 2, mb: 2 }}>
              {error}
            </Alert>
          )}

          {activeConversation?.messages.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                textAlign: 'center',
                px: 4,
              }}
            >
              <BotIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Welcome to ResourceWise AI
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Ask me anything about resource allocation, project management,
                or team optimization.
              </Typography>
            </Box>
          ) : (
            <>
              {activeConversation?.messages.map(renderMessage)}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>

        {/* Enhanced Input Area */}
        <Paper
          elevation={4}
          sx={{
            p: 3,
            borderRadius: 0,
            borderTop: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'background.paper',
          }}
        >
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
            <TextField
              fullWidth
              multiline
              maxRows={6}
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                isStreaming
                  ? 'AI is responding...'
                  : 'Ask me anything about resource allocation, project management, or team optimization...'
              }
              disabled={isStreaming}
              variant="outlined"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: 'background.default',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    backgroundColor: 'grey.50',
                  },
                  '&.Mui-focused': {
                    backgroundColor: 'background.paper',
                    boxShadow: '0 0 0 2px rgba(25, 118, 210, 0.2)',
                  },
                },
                '& .MuiOutlinedInput-input': {
                  fontSize: '1rem',
                  lineHeight: 1.5,
                },
              }}
            />
            <IconButton
              onClick={handleSendMessage}
              disabled={!message.trim() || isStreaming}
              color="primary"
              sx={{
                width: 48,
                height: 48,
                backgroundColor:
                  message.trim() && !isStreaming ? 'primary.main' : 'grey.300',
                color: 'white',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  backgroundColor:
                    message.trim() && !isStreaming
                      ? 'primary.dark'
                      : 'grey.400',
                  transform: 'scale(1.05)',
                },
                '&:disabled': {
                  backgroundColor: 'grey.300',
                  color: 'grey.500',
                },
              }}
            >
              {isStreaming ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <SendIcon />
              )}
            </IconButton>
          </Box>

          {/* Helpful hints */}
          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              label="💡 Try: 'How to allocate resources efficiently?'"
              size="small"
              variant="outlined"
              onClick={() =>
                setMessage('How to allocate resources efficiently?')
              }
              sx={{
                cursor: 'pointer',
                '&:hover': { backgroundColor: 'primary.50' },
              }}
            />
            <Chip
              label="📊 Try: 'Show me project management best practices'"
              size="small"
              variant="outlined"
              onClick={() =>
                setMessage('Show me project management best practices')
              }
              sx={{
                cursor: 'pointer',
                '&:hover': { backgroundColor: 'primary.50' },
              }}
            />
            <Chip
              label="🚀 Try: 'Help me optimize team productivity'"
              size="small"
              variant="outlined"
              onClick={() => setMessage('Help me optimize team productivity')}
              sx={{
                cursor: 'pointer',
                '&:hover': { backgroundColor: 'primary.50' },
              }}
            />
          </Box>
        </Paper>
      </Box>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem
          onClick={() =>
            selectedConversationId &&
            handleDeleteConversation(selectedConversationId)
          }
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ChatInterface;
