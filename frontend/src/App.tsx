import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingContent, setCurrentStreamingContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // API base URL - use environment variable or fallback to relative path for proxy
  const API_BASE_URL = process.env.REACT_APP_API_URL || '';

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamingContent]);

  // Initial welcome message
  useEffect(() => {
    const loadWelcome = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/welcome`);
        if (!response.ok) throw new Error('Failed to load welcome');

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No reader available');

        const decoder = new TextDecoder();
        let content = '';

        // Start streaming
        setIsLoading(true);
        setCurrentStreamingContent('');

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.done) {
                  setMessages([{ role: 'assistant', content }]);
                  setCurrentStreamingContent('');
                  setIsLoading(false);
                  return;
                }
                const newContent = data.content;
                content += newContent;
                setCurrentStreamingContent(prev => prev + newContent);
              } catch (e) {
                console.warn('Failed to parse chunk:', e);
              }
            }
          }
        }
      } catch (error) {
        console.error('Welcome message error:', error);
        setMessages([{
          role: 'assistant',
          content: "Hello! I'm your AI Chat Assistant. How can I help you today?"
        }]);
        setCurrentStreamingContent('');
        setIsLoading(false);
      }
    };

    loadWelcome();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setCurrentStreamingContent('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          prompt_type: 'default'
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      const decoder = new TextDecoder();
      let content = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.error) throw new Error(data.error);

              if (data.done) {
                setMessages(prev => [...prev, { role: 'assistant', content }]);
                setCurrentStreamingContent('');
                setIsLoading(false);
                return;
              }

              const newContent = data.content;
              content += newContent;
              setCurrentStreamingContent(prev => prev + newContent);
            } catch (e) {
              console.warn('Failed to parse chunk:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Send message error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your message.'
      }]);
      setCurrentStreamingContent('');
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content: string) => {
    return content.split('\n').map((line, i) => (
      <div key={i}>{line || <br />}</div>
    ));
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <h1>AI Chat Assistant</h1>
        </div>

        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                {formatMessage(message.content)}
              </div>
            </div>
          ))}

          {/* Show streaming content */}
          {currentStreamingContent && (
            <div className="message assistant">
              <div className="message-content">
                {formatMessage(currentStreamingContent)}
                <span className="cursor">|</span>
              </div>
            </div>
          )}

          {/* Show loading indicator */}
          {isLoading && !currentStreamingContent && (
            <div className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            rows={1}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
