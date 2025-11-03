import React from 'react';
import { FileText, ExternalLink, BookOpen } from 'lucide-react';

const CitationPanel = ({ citations = [] }) => {
  // Remove duplicates based on source_id
  const uniqueCitations = citations.reduce((acc, citation) => {
    if (!acc.find(c => c.source_id === citation.source_id)) {
      acc.push(citation);
    }
    return acc;
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Sources & Citations</h3>
        <BookOpen className="h-5 w-5 text-gray-400" />
      </div>

      {uniqueCitations.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="h-10 w-10 mx-auto text-gray-300 mb-3" />
          <p className="text-sm text-gray-500">
            Citations will appear here when the AI references policy documents
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {uniqueCitations.map((citation, index) => (
            <div
              key={`${citation.source_id}-${index}`}
              className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900 mb-1">
                    {citation.document_name}
                  </h4>
                  {citation.section && (
                    <p className="text-xs text-gray-600 mb-1">{citation.section}</p>
                  )}
                  {citation.page_number && (
                    <p className="text-xs text-gray-500">Page {citation.page_number}</p>
                  )}
                </div>
                <div className="flex items-center space-x-1">
                  <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {(citation.relevance_score * 100).toFixed(0)}% match
                  </div>
                </div>
              </div>
              
              {citation.excerpt && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-700 italic">
                  "{citation.excerpt}"
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {uniqueCitations.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-gray-500">
            {uniqueCitations.length} source{uniqueCitations.length !== 1 ? 's' : ''} referenced
          </p>
        </div>
      )}
    </div>
  );
};

export default CitationPanel;
