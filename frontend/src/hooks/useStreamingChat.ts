/* eslint-disable @typescript-eslint/no-explicit-any */
import { useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { v4 as uuidv4 } from 'uuid';
import {
  addMessage,
  startStreaming,
  updateStreamingMessage,
  stopStreaming,
  setError,
  setLoading,
} from '../store/slices/chatSlice';

interface StreamingChatOptions {
  baseUrl?: string;
}

interface StreamEvent {
  type: string;
  data: any;
  session_id?: string;
}

export const useStreamingChat = (options: StreamingChatOptions = {}) => {
  const dispatch = useDispatch();
  const baseUrl = options.baseUrl || '/api/v1';

  const sendMessage = useCallback(
    async (conversationId: string, message: string, sessionId: string) => {
      try {
        dispatch(setError(null));
        dispatch(setLoading(true));

        // Add user message to conversation
        dispatch(
          addMessage({
            conversationId,
            message: {
              content: message,
              role: 'user',
            },
          })
        );

        // Create assistant message placeholder
        const assistantMessageId = uuidv4();
        dispatch(
          addMessage({
            conversationId,
            message: {
              id: assistantMessageId,
              content: '',
              role: 'assistant',
              isStreaming: true,
            },
          })
        );

        // Start streaming
        dispatch(
          startStreaming({
            conversationId,
            messageId: assistantMessageId,
          })
        );

        // Make streaming request
        const response = await fetch(`${baseUrl}/ai/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: message,
            session_id: sessionId,
            user_id: null, // TODO: Add user authentication
            metadata: {
              conversation_id: conversationId,
            },
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!response.body) {
          throw new Error('No response body');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedContent = '';
        let buffer = '';

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;

            // Process complete lines
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
              if (line.trim() === '') continue;

              // console.log('Processing line:', line); // Debug log

              try {
                // Handle Server-Sent Events format
                if (line.startsWith('data: ')) {
                  const jsonStr = line.slice(6); // Remove 'data: ' prefix
                  if (jsonStr === '[DONE]') {
                    console.log('Stream completed');
                    break;
                  }

                  const event: StreamEvent = JSON.parse(jsonStr);
                  // console.log('Parsed event:', event); // Debug log

                  // Handle different event types
                  switch (event.type) {
                    case 'start': {
                      // Stream started - no action needed
                      // console.log('Stream started for session:', event.data.session_id);
                      break;
                    }

                    case 'token': {
                      const token = event.data.token || '';
                      accumulatedContent += token;
                      // console.log('Token received:', token, 'Accumulated:', accumulatedContent.length, 'chars');
                      dispatch(
                        updateStreamingMessage({
                          conversationId,
                          messageId: assistantMessageId,
                          content: accumulatedContent,
                        })
                      );
                      break;
                    }

                    case 'content': {
                      accumulatedContent = event.data.content || '';
                      console.log(
                        'Content update:',
                        accumulatedContent.length,
                        'chars'
                      );
                      dispatch(
                        updateStreamingMessage({
                          conversationId,
                          messageId: assistantMessageId,
                          content: accumulatedContent,
                        })
                      );
                      break;
                    }

                    case 'error': {
                      console.error('Stream error:', event.data.message);
                      throw new Error(event.data.message || 'Streaming error');
                    }

                    case 'done': {
                      // Final content update
                      if (event.data.content) {
                        accumulatedContent = event.data.content;
                        console.log(
                          'Final content:',
                          accumulatedContent.length,
                          'chars'
                        );
                        dispatch(
                          updateStreamingMessage({
                            conversationId,
                            messageId: assistantMessageId,
                            content: accumulatedContent,
                          })
                        );
                      }
                      break;
                    }

                    default: {
                      console.log('Unknown event type:', event.type);
                    }
                  }
                } else {
                  // Handle plain JSON streaming
                  const event = JSON.parse(line);
                  if (event.content) {
                    accumulatedContent += event.content;
                    dispatch(
                      updateStreamingMessage({
                        conversationId,
                        messageId: assistantMessageId,
                        content: accumulatedContent,
                      })
                    );
                  }
                }
              } catch (parseError) {
                console.warn(
                  'Failed to parse streaming chunk:',
                  line,
                  parseError
                );
                // Continue processing other lines
              }
            }
          }

          // Process any remaining buffer content
          if (buffer.trim()) {
            console.log('Processing remaining buffer:', buffer);
          }
        } finally {
          reader.releaseLock();
        }

        // Stop streaming
        dispatch(
          stopStreaming({
            conversationId,
            messageId: assistantMessageId,
          })
        );
      } catch (error) {
        console.error('Streaming chat error:', error);
        dispatch(
          setError(error instanceof Error ? error.message : 'An error occurred')
        );

        // Stop streaming on error
        dispatch(
          stopStreaming({
            conversationId,
            messageId: '', // We might not have the message ID in case of early error
          })
        );
      } finally {
        dispatch(setLoading(false));
      }
    },
    [dispatch, baseUrl]
  );

  const cancelStream = useCallback(
    (conversationId: string, messageId: string) => {
      dispatch(
        stopStreaming({
          conversationId,
          messageId,
        })
      );
    },
    [dispatch]
  );

  return {
    sendMessage,
    cancelStream,
  };
};

export default useStreamingChat;
