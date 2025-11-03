import React, { useState, useRef, useEffect } from 'react';
import { Send, AlertCircle, FileText, Shield, Loader2, Sparkles, Bot, User } from 'lucide-react';
import RiskBadge from './RiskBadge';
import CitationPanel from './CitationPanel';
import TraceViewer from './TraceViewer';
import api from '../services/api';

const EXAMPLE_QUERIES = [
  "What is model risk?",
  "How often should models be validated?",
  "Explain AI ethics principles",
  "What are LLM governance requirements?",
  "Compliance requirements for AI systems"
];

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showTraces, setShowTraces] = useState(false);
  const [currentTraces, setCurrentTraces] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Focus input on load
    inputRef.current?.focus();
  }, []);

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
      const response = await api.sendMessage(
        input, 
        sessionId, 
        true,  // enable_guardrails
        showTraces  // return_traces
      );
      
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
        processingTime: response.processing_time_ms,
      };

      if (response.traces) {
        setCurrentTraces(response.traces);
      }

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
      inputRef.current?.focus();
    }
  };

  const handleExampleClick = (query) => {
    setInput(query);
    inputRef.current?.focus();
  };

  return (
    <div className="grid grid-cols-12 gap-4 h-[calc(100vh-280px)]">
      {/* Chat Area */}
      <div className="col-span-8 bg-white rounded-lg shadow-lg flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="h-16 w-16 mx-auto text-primary-500 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Welcome to Risk Copilot
              </h3>
              <p className="text-gray-600 max-w-md mx-auto mb-6">
                I'm your AI assistant for risk management and compliance. Ask me about policies, 
                regulations, or best practices.
              </p>
              
              {/* Example Queries */}
              <div className="mt-8">
                <p className="text-sm text-gray-500 mb-3">Try asking:</p>
                <div className="flex flex-wrap justify-center gap-2">
                  {EXAMPLE_QUERIES.map((query, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExampleClick(query)}
                      className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors flex items-center gap-1"
                    >
                      <Sparkles className="h-3 w-3" />
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' ? 'bg-primary-600' : 'bg-gray-200'
                  }`}>
                    {message.type === 'user' ? 
                      <User className="h-5 w-5 text-white" /> : 
                      <Bot className="h-5 w-5 text-gray-700" />
                    }
                  </div>
                  
                  {/* Message Content */}
                  <div className="flex-1">
                    {message.type === 'assistant' && (
                      <div className="flex items-center gap-2 mb-1">
                        <RiskBadge level={message.riskLevel} size="sm" />
                        {message.confidence && (
                          <span className="text-xs text-gray-500">
                            {(message.confidence * 100).toFixed(0)}% confident
                          </span>
                        )}
                        {message.processingTime && (
                          <span className="text-xs text-gray-400">
                            {message.processingTime}ms
                          </span>
                        )}
                      </div>
                    )}
                    
                    <div className={`rounded-lg px-4 py-3 ${
                      message.type === 'user' 
                        ? 'bg-primary-600 text-white' 
                        : message.type === 'error'
                        ? 'bg-red-50 border border-red-200 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>

                    {/* Violations */}
                    {message.violations && message.violations.length > 0 && (
                      <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
                        <div className="flex items-center text-yellow-800 mb-1">
                          <AlertCircle className="h-4 w-4 mr-1" />
                          <span className="font-medium">Safety Notice:</span>
                        </div>
                        {message.violations.map((v, idx) => (
                          <div key={idx} className="text-yellow-700 text-xs">
                            • {v.description}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Citations */}
                    {message.citations && message.citations.length > 0 && (
                      <div className="mt-2 flex items-center text-xs text-gray-500">
                        <FileText className="h-3 w-3 mr-1" />
                        <span>{message.citations.length} sources</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-gray-700" />
                </div>
                <div className="bg-gray-100 rounded-lg px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                    <span className="text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="border-t p-4">
          <div className="flex gap-2 items-center">
            <div className="flex items-center gap-2 mr-2">
              <button
                type="button"
                onClick={() => setShowTraces(!showTraces)}
                className={`p-2 rounded-lg transition-colors ${
                  showTraces ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'
                }`}
                title="Toggle trace viewer"
              >
                <Shield className="h-5 w-5" />
              </button>
            </div>
            
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about risk policies, compliance, or governance..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={isLoading}
            />
            
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
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
          
          {showTraces && (
            <div className="mt-2 text-xs text-gray-500">
              <Shield className="h-3 w-3 inline mr-1" />
              Trace mode enabled - showing agent execution details
            </div>
          )}
        </form>
      </div>

      {/* Side Panel */}
      <div className="col-span-4 space-y-4">
        {/* Citations Panel */}
        <div className="bg-white rounded-lg shadow-lg p-4 h-[60%] overflow-y-auto">
          <CitationPanel 
            citations={messages
              .filter(m => m.type === 'assistant' && m.citations)
              .flatMap(m => m.citations)} 
          />
        </div>
        
        {/* Traces Panel (if enabled) */}
        {showTraces && currentTraces.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-4 h-[38%] overflow-y-auto">
            <TraceViewer traces={currentTraces} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;