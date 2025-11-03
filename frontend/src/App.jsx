import React, { useState } from 'react';
import { Shield, Send, AlertCircle, CheckCircle, XCircle, Activity } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import RiskBadge from './components/RiskBadge';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Kowshik's Risk Copilot</h1>
                <p className="text-sm text-gray-500">Multi-Agent LLM Risk Management System</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-green-500 animate-pulse" />
                <span className="text-sm text-gray-600">System Operational</span>
              </div>
              <RiskBadge level="low" />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chat'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Chat Interface
            </button>
            <button
              onClick={() => setActiveTab('traces')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'traces'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Audit Traces
            </button>
            <button
              onClick={() => setActiveTab('docs')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'docs'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Policy Documents
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'traces' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Audit Traces</h2>
            <p className="text-gray-600">Trace viewer will be implemented in Phase 5</p>
          </div>
        )}
        {activeTab === 'docs' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Policy Documents</h2>
            <p className="text-gray-600">Document management will be implemented in Phase 2</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              © 2024 Risk Copilot - Demo for Société Générale
            </p>
            <div className="flex space-x-4 text-sm text-gray-500">
              <span>v1.0.0</span>
              <span>•</span>
              <a href="https://github.com/Kowshik13/RiskCopilot" className="hover:text-gray-700">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
