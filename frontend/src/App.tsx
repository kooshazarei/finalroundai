import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  const [threadId, setThreadId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const threadInitializedRef = useRef(false);

  // API base URL - use environment variable or fallback to relative path for proxy
  const API_BASE_URL = process.env.REACT_APP_API_URL || '';

  // Initialize a new thread when component mounts
  useEffect(() => {
    // Prevent double initialization in React Strict Mode
    if (threadInitializedRef.current) return;
    threadInitializedRef.current = true;

    const initializeThread = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/chat/thread/new`, {
          method: 'POST'
        });
        if (response.ok) {
          const data = await response.json();
          setThreadId(data.thread_id);
          console.log('Initialized new thread:', data.thread_id);
        }
      } catch (error) {
        console.error('Failed to initialize thread:', error);
        // Fallback to generating a client-side thread ID
        setThreadId('thread-' + Math.random().toString(36).substr(2, 9));
      }
    };

    initializeThread();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array since we use ref to prevent double execution

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamingContent]);

  // Initial welcome message from backend
  const fetchWelcomeMessage = useCallback(async () => {
    if (!threadId) return;

    setIsLoading(true);
    setCurrentStreamingContent('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: "__INIT__", // Special init message to trigger welcome
          prompt_type: 'default',
          thread_id: threadId
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch welcome message');

      const reader = response.body?.getReader();
      if (!reader) return;

      let welcomeContent = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.content) {
                welcomeContent += data.content;
                setCurrentStreamingContent(welcomeContent);
              }
              if (data.done) {
                setMessages([{ role: 'assistant', content: welcomeContent }]);
                setCurrentStreamingContent('');
                setIsLoading(false);
                return;
              }
            } catch (e) {
              // Ignore parsing errors
            }
          }
        }
      }
    } catch (error) {
      console.error('Error fetching welcome message:', error);
      // Fallback to a simple message
      setMessages([{
        role: 'assistant',
        content: "Welcome! I'm ready to start your technical interview. How can I help you today?"
      }]);
      setCurrentStreamingContent('');
      setIsLoading(false);
    }
  }, [threadId, API_BASE_URL]);

  useEffect(() => {
    // Only fetch welcome message if we have a thread ID and no messages yet
    if (threadId && messages.length === 0) {
      fetchWelcomeMessage();
    }
  }, [threadId, messages.length, fetchWelcomeMessage]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !threadId) return;

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
          prompt_type: 'default',
          thread_id: threadId
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      const decoder = new TextDecoder();
      let content = '';

      const processDataLine = (line: string) => {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.error) throw new Error(data.error);

            if (data.done) {
              setMessages(prev => [...prev, { role: 'assistant', content }]);
              setCurrentStreamingContent('');
              setIsLoading(false);
              return true; // Signal completion
            }

            const newContent = data.content;
            if (newContent) {
              content = content + newContent;
              setCurrentStreamingContent(content);
            }
          } catch (e) {
            console.warn('Failed to parse chunk:', e);
          }
        }
        return false; // Continue processing
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          const isComplete = processDataLine(line);
          if (isComplete) return;
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
    return content.split('\n').map((line, i) => {
      // Handle empty lines
      if (!line.trim()) {
        return <br key={i} />;
      }

      // Handle bullet points
      if (line.trim().startsWith('- ')) {
        const bulletContent = line.replace(/^[\s]*-\s*/, '');
        return (
          <div key={i} className="bullet-point">
            <span className="bullet">•</span>
            <span>{formatInlineMarkdown(bulletContent)}</span>
          </div>
        );
      }

      // Handle numbered lists
      if (/^\d+\.\s/.test(line.trim())) {
        const match = line.trim().match(/^(\d+)\.\s(.*)$/);
        if (match) {
          return (
            <div key={i} className="numbered-point">
              <span className="number">{match[1]}.</span>
              <span>{formatInlineMarkdown(match[2])}</span>
            </div>
          );
        }
      }

      // Regular line with inline formatting
      return <div key={i}>{formatInlineMarkdown(line)}</div>;
    });
  };

  const formatInlineMarkdown = (text: string) => {
    // Split text by ** for bold formatting
    const parts = text.split(/(\*\*[^*]+\*\*)/);

    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.slice(2, -2);
        return <strong key={index}>{boldText}</strong>;
      }
      return part;
    });
  };

  const startNewConversation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/thread/new`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setThreadId(data.thread_id);
        setMessages([]);
        setCurrentStreamingContent('');
        setIsLoading(false);
        console.log('Started new conversation:', data.thread_id);

        // Fetch welcome message for new conversation
        fetchWelcomeMessage();
      }
    } catch (error) {
      console.error('Failed to start new conversation:', error);
      // Fallback to generating a client-side thread ID
      setThreadId('thread-' + Math.random().toString(36).substr(2, 9));
      setMessages([]);
      setCurrentStreamingContent('');
      setIsLoading(false);
      fetchWelcomeMessage();
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <h1>AI Interview Assistant</h1>
          <div className="chat-controls">
            <button className="new-conversation-btn" onClick={startNewConversation}>
              New Interview
            </button>
            <div className="chat-info">
              <span className="info-item">Session: {threadId.slice(-8)}</span>
            </div>
          </div>
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
            placeholder="Type your response... (or say 'next' to skip)"
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
