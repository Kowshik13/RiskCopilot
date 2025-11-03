import React from 'react';
import { Activity, CheckCircle, XCircle, Clock, Zap } from 'lucide-react';

const TraceViewer = ({ traces = [] }) => {
  const getIconForAgent = (agentName) => {
    const icons = {
      sanitizer: '🛡️',
      retriever: '🔍',
      risk_evaluator: '⚠️',
      generator: '✍️',
      validator: '✅',
      audit: '📝',
    };
    return icons[agentName] || '🤖';
  };

  const getColorForStatus = (status) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-50';
      case 'failure':
        return 'text-red-600 bg-red-50';
      case 'skipped':
        return 'text-gray-400 bg-gray-50';
      default:
        return 'text-blue-600 bg-blue-50';
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900 flex items-center">
          <Activity className="h-4 w-4 mr-2" />
          Agent Execution Trace
        </h3>
        <span className="text-xs text-gray-500">
          {traces.length} agents
        </span>
      </div>

      <div className="space-y-2">
        {traces.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No traces available
          </p>
        ) : (
          traces.map((trace, index) => (
            <div
              key={index}
              className={`p-2 rounded-lg border ${
                trace.status === 'success' 
                  ? 'border-green-200 bg-green-50/50' 
                  : trace.status === 'failure'
                  ? 'border-red-200 bg-red-50/50'
                  : 'border-gray-200 bg-gray-50/50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{getIconForAgent(trace.agent_name)}</span>
                  <span className="font-medium text-sm capitalize">
                    {trace.agent_name.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {trace.status === 'success' ? (
                    <CheckCircle className="h-3 w-3 text-green-600" />
                  ) : trace.status === 'failure' ? (
                    <XCircle className="h-3 w-3 text-red-600" />
                  ) : (
                    <Clock className="h-3 w-3 text-gray-400" />
                  )}
                  <span className="text-xs text-gray-500 flex items-center">
                    <Zap className="h-3 w-3 mr-0.5" />
                    {trace.duration_ms}ms
                  </span>
                </div>
              </div>
              
              {/* Show key outputs */}
              {trace.output_data && Object.keys(trace.output_data).length > 0 && (
                <div className="text-xs text-gray-600 mt-1">
                  {Object.entries(trace.output_data).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-500">{key}:</span>
                      <span className="font-mono">
                        {typeof value === 'boolean' ? (value ? '✓' : '✗') : value}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {traces.length > 0 && (
        <div className="mt-3 pt-3 border-t text-xs text-gray-500">
          Total time: {traces.reduce((sum, t) => sum + t.duration_ms, 0)}ms
        </div>
      )}
    </div>
  );
};

export default TraceViewer;