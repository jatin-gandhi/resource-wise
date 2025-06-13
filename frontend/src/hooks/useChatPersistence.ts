import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  loadConversations,
  selectConversations,
} from '../store/slices/chatSlice';
import type { Conversation } from '../store/slices/chatSlice';

const STORAGE_KEY = 'resourcewise_chat_conversations';

export const useChatPersistence = () => {
  const dispatch = useDispatch();
  const conversations = useSelector(selectConversations);

  // Load conversations from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsedConversations: Conversation[] = JSON.parse(stored);
        dispatch(loadConversations(parsedConversations));
      }
    } catch (error) {
      console.error('Failed to load conversations from localStorage:', error);
    }
  }, [dispatch]);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    } catch (error) {
      console.error('Failed to save conversations to localStorage:', error);
    }
  }, [conversations]);

  const clearStoredConversations = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear stored conversations:', error);
    }
  };

  return {
    clearStoredConversations,
  };
};

export default useChatPersistence;
