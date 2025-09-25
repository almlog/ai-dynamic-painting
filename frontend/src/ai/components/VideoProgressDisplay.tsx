/**
 * VideoProgressDisplay - Dedicated component for video generation progress display
 * T6-003: REFACTOR - Extracted from VideoGenerationDashboard for better separation of concerns
 */

import React from 'react';

// Video generation status type
type VideoStatus = 'pending' | 'processing' | 'completed' | 'failed';

// Component props interface
interface VideoProgressDisplayProps {
  status: VideoStatus;
  progressPercent: number;
  errorMessage?: string;
  className?: string;
}

const VideoProgressDisplay: React.FC<VideoProgressDisplayProps> = ({
  status,
  progressPercent,
  errorMessage,
  className = ''
}) => {
  const getStatusBadgeClass = (status: string) => {
    const baseClass = 'px-2 py-1 rounded text-sm font-medium ';
    switch (status) {
      case 'completed': return baseClass + 'bg-green-100 text-green-800';
      case 'processing': return baseClass + 'bg-blue-100 text-blue-800';
      case 'failed': return baseClass + 'bg-red-100 text-red-800';
      default: return baseClass + 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className={className}>
      {/* Status Badge */}
      <span className={getStatusBadgeClass(status)}>
        {status}
      </span>
      
      {/* Progress Bar for Processing Status */}
      {status === 'processing' && (
        <div className="mt-2">
          <div className="bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${progressPercent}%` }}
              role="progressbar"
              aria-valuenow={progressPercent}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>
          <div className="text-sm text-gray-600 mt-1">{progressPercent}%</div>
        </div>
      )}
      
      {/* Error Message for Failed Status */}
      {status === 'failed' && errorMessage && (
        <div className="text-sm text-red-600 mt-1">{errorMessage}</div>
      )}
    </div>
  );
};

export default VideoProgressDisplay;