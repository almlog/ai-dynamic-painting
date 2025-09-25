/**
 * GenerationHistoryTable - Dedicated component for video generation history display
 * T6-004: REFACTOR - Extracted from VideoGenerationDashboard for better separation of concerns
 */

import React from 'react';
import VideoProgressDisplay from './VideoProgressDisplay';

// Video generation interface
interface VideoGeneration {
  id: string;
  task_id: string;
  prompt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  duration_seconds: number;
  resolution: string;
  fps: number;
  quality: 'draft' | 'standard' | 'premium';
  video_url?: string;
  cost: number;
  created_at: string;
  progress_percent: number;
  error_message?: string;
}

// Component props interface
interface GenerationHistoryTableProps {
  generations: VideoGeneration[];
  onRetry: (generation: VideoGeneration) => void;
  className?: string;
}

const GenerationHistoryTable: React.FC<GenerationHistoryTableProps> = ({
  generations,
  onRetry,
  className = ''
}) => {
  const formatCost = (cost: number | undefined | null) => {
    if (cost === undefined || cost === null || isNaN(cost)) {
      return '$0.00';
    }
    return `$${cost.toFixed(2)}`;
  };

  if (generations.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow overflow-hidden ${className}`}>
        <div className="p-8 text-center">
          <div className="text-gray-500 mb-4">No generations found</div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Create your first video generation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow overflow-hidden ${className}`}>
      <div className="overflow-x-auto">
        <table role="table" className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Prompt
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Duration
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Resolution
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {generations.map((generation) => (
              <tr key={generation.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {generation.prompt}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {generation.duration_seconds}s
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {generation.resolution}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <VideoProgressDisplay
                    status={generation.status}
                    progressPercent={generation.progress_percent}
                    errorMessage={generation.error_message}
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatCost(generation.cost)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    {generation.status === 'completed' && generation.video_url && (
                      <>
                        <button
                          className="text-blue-600 hover:text-blue-900"
                          aria-label="Play Video"
                        >
                          Play Video
                        </button>
                        <a
                          href={generation.video_url}
                          download
                          className="text-green-600 hover:text-green-900"
                        >
                          Download
                        </a>
                      </>
                    )}
                    {generation.status === 'failed' && (
                      <button
                        onClick={() => onRetry(generation)}
                        className="text-yellow-600 hover:text-yellow-900"
                      >
                        Retry
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default GenerationHistoryTable;