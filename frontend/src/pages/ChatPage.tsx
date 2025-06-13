import React from 'react';
import Layout from '../components/layout/Layout';
import ChatInterface from '../components/chat/ChatInterface';

const ChatPage: React.FC = () => {
  return (
    <Layout fullHeight>
      <ChatInterface />
    </Layout>
  );
};

export default ChatPage;
