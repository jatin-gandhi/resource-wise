import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { v4 as uuidv4 } from 'uuid';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string; // ISO string instead of Date
  isStreaming?: boolean;
  metadata?: {
    session_id?: string;
    error?: string;
    type?: string;
  };
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  created_at: string; // ISO string instead of Date
  updated_at: string; // ISO string instead of Date
  session_id: string;
}

export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isStreaming: boolean;
  streamingMessageId: string | null;
  error: string | null;
  isLoading: boolean;
}

const initialState: ChatState = {
  conversations: [],
  activeConversationId: null,
  isStreaming: false,
  streamingMessageId: null,
  error: null,
  isLoading: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    // Conversation management
    createConversation: (state, action: PayloadAction<{ title?: string }>) => {
      const now = new Date().toISOString();
      const newConversation: Conversation = {
        id: uuidv4(),
        title: action.payload.title || 'New Conversation',
        messages: [],
        created_at: now,
        updated_at: now,
        session_id: uuidv4(),
      };
      state.conversations.unshift(newConversation);
      state.activeConversationId = newConversation.id;
    },

    setActiveConversation: (state, action: PayloadAction<string>) => {
      state.activeConversationId = action.payload;
    },

    deleteConversation: (state, action: PayloadAction<string>) => {
      state.conversations = state.conversations.filter(
        conv => conv.id !== action.payload
      );
      if (state.activeConversationId === action.payload) {
        state.activeConversationId = state.conversations[0]?.id || null;
      }
    },

    updateConversationTitle: (
      state,
      action: PayloadAction<{ id: string; title: string }>
    ) => {
      const conversation = state.conversations.find(
        conv => conv.id === action.payload.id
      );
      if (conversation) {
        conversation.title = action.payload.title;
        conversation.updated_at = new Date().toISOString();
      }
    },

    // Message management
    addMessage: (
      state,
      action: PayloadAction<{
        conversationId: string;
        message: Omit<Message, 'timestamp'>;
      }>
    ) => {
      const conversation = state.conversations.find(
        conv => conv.id === action.payload.conversationId
      );
      if (conversation) {
        const now = new Date().toISOString();
        const newMessage: Message = {
          ...action.payload.message,
          id: action.payload.message.id || uuidv4(), // Use provided ID or generate new one
          timestamp: now,
        };
        conversation.messages.push(newMessage);
        conversation.updated_at = now;

        // Auto-generate title from first user message
        if (conversation.messages.length === 1 && newMessage.role === 'user') {
          conversation.title =
            newMessage.content.slice(0, 50) +
            (newMessage.content.length > 50 ? '...' : '');
        }
      }
    },

    // Streaming management
    startStreaming: (
      state,
      action: PayloadAction<{ conversationId: string; messageId: string }>
    ) => {
      state.isStreaming = true;
      state.streamingMessageId = action.payload.messageId;

      const conversation = state.conversations.find(
        conv => conv.id === action.payload.conversationId
      );
      if (conversation) {
        const message = conversation.messages.find(
          msg => msg.id === action.payload.messageId
        );
        if (message) {
          message.isStreaming = true;
        }
      }
    },

    updateStreamingMessage: (
      state,
      action: PayloadAction<{
        conversationId: string;
        messageId: string;
        content: string;
      }>
    ) => {
      const conversation = state.conversations.find(
        conv => conv.id === action.payload.conversationId
      );
      if (conversation) {
        const message = conversation.messages.find(
          msg => msg.id === action.payload.messageId
        );
        if (message) {
          message.content = action.payload.content;
          conversation.updated_at = new Date().toISOString();
        }
      }
    },

    stopStreaming: (
      state,
      action: PayloadAction<{ conversationId: string; messageId: string }>
    ) => {
      state.isStreaming = false;
      state.streamingMessageId = null;

      const conversation = state.conversations.find(
        conv => conv.id === action.payload.conversationId
      );
      if (conversation) {
        const message = conversation.messages.find(
          msg => msg.id === action.payload.messageId
        );
        if (message) {
          message.isStreaming = false;
        }
      }
    },

    // Error handling
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },

    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    // Clear all conversations
    clearAllConversations: state => {
      state.conversations = [];
      state.activeConversationId = null;
      state.isStreaming = false;
      state.streamingMessageId = null;
      state.error = null;
    },

    // Load conversations from localStorage
    loadConversations: (state, action: PayloadAction<Conversation[]>) => {
      state.conversations = action.payload.map(conv => ({
        ...conv,
        // Ensure dates are strings (they should already be from localStorage)
        created_at:
          typeof conv.created_at === 'string'
            ? conv.created_at
            : new Date(conv.created_at).toISOString(),
        updated_at:
          typeof conv.updated_at === 'string'
            ? conv.updated_at
            : new Date(conv.updated_at).toISOString(),
        messages: conv.messages.map(msg => ({
          ...msg,
          timestamp:
            typeof msg.timestamp === 'string'
              ? msg.timestamp
              : new Date(msg.timestamp).toISOString(),
        })),
      }));
    },
  },
});

export const {
  createConversation,
  setActiveConversation,
  deleteConversation,
  updateConversationTitle,
  addMessage,
  startStreaming,
  updateStreamingMessage,
  stopStreaming,
  setError,
  setLoading,
  clearAllConversations,
  loadConversations,
} = chatSlice.actions;

export default chatSlice.reducer;

// Selectors
export const selectActiveConversation = (state: { chat: ChatState }) => {
  if (!state.chat.activeConversationId) return null;
  return (
    state.chat.conversations.find(
      conv => conv.id === state.chat.activeConversationId
    ) || null
  );
};

export const selectConversations = (state: { chat: ChatState }) =>
  state.chat.conversations;
export const selectIsStreaming = (state: { chat: ChatState }) =>
  state.chat.isStreaming;
export const selectChatError = (state: { chat: ChatState }) => state.chat.error;
export const selectIsLoading = (state: { chat: ChatState }) =>
  state.chat.isLoading;
