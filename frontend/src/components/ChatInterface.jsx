import React, { useState, useRef, useEffect } from 'react';
import { Send, AlertCircle, FileText, Shield, Loader2 } from 'lucide-react';
import RiskBadge from './RiskBadge';
import CitationPanel from './CitationPanel';
import api from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.sendMessage(input, sessionId);
      
      // Set session ID if not already set
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const aiMessage = {
        type: 'assistant',
        content: response.answer,
        riskLevel: response.risk_level,
        confidence: response.confidence,
        citations: response.citations || [],
        violations: response.guardrail_violations || [],
        timestamp: response.timestamp,
        messageId: response.message_id,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'error',
        content: 'Failed to process your request. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-3 gap-6 h-[calc(100vh-280px)]">
      {/* Chat Area */}
      <div className="col-span-2 bg-white rounded-lg shadow-lg flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Shield className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to Risk Copilot
              </h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Ask questions about risk policies, compliance requirements, or model validation.
                I'll provide answers with citations and risk assessment.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-3xl ${
                    message.type === 'user'
                      ? 'bg-primary-600 text-white'
                      : message.type === 'error'
                      ? 'bg-red-50 border border-red-200'
                      : 'bg-gray-100'
                  } rounded-lg p-4`}
                >
                  {message.type === 'assistant' && (
                    <div className="flex items-center justify-between mb-2">
                      <RiskBadge level={message.riskLevel} />
                      <span className="text-xs text-gray-500">
                        Confidence: {(message.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  
                  <p className={message.type === 'user' ? 'text-white' : 'text-gray-800'}>
                    {message.content}
                  </p>

                  {message.violations && message.violations.length > 0 && (
                    <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                      <div className="flex items-center text-yellow-800">
                        <AlertCircle className="h-4 w-4 mr-2" />
                        <span className="text-sm font-medium">Guardrail Alerts:</span>
                      </div>
                      <ul className="mt-1 text-sm text-yellow-700">
                        {message.violations.map((violation, idx) => (
                          <li key={idx}>• {violation.description}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-3 flex items-center text-sm text-gray-500">
                      <FileText className="h-4 w-4 mr-1" />
                      <span>{message.citations.length} sources cited</span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg p-4">
                <Loader2 className="h-5 w-5 animate-spin text-gray-600" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="border-t p-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about risk policies, compliance, or model validation..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <Send className="h-5 w-5" />
                  <span>Send</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Citations Panel */}
      <div className="col-span-1">
        <CitationPanel 
          citations={messages
            .filter(m => m.type === 'assistant' && m.citations)
            .flatMap(m => m.citations)} 
        />
      </div>
    </div>
  );
};

export default ChatInterface;
