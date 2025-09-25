/**
 * VideoGenerationDashboard - Main dashboard for video generation management
 * T6-001: GREEN phase - Minimum implementation to pass tests
 */

import React, { useState, useEffect, useMemo } from 'react';
import { apiClient, isGenerationComplete, isGenerationFailed, isGenerationInProgress } from '../../services/api';
import { useVideoPolling } from '../../hooks/useVideoPolling';
import VideoGenerationForm from './VideoGenerationForm';
import VideoProgressDisplay from './VideoProgressDisplay';
import GenerationHistoryTable from './GenerationHistoryTable';
import CostManagementPanel from './CostManagementPanel';

// T6-001: Video Generation type definitions
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

interface VideoGenerationRequest {
  prompt: string;
  duration_seconds: number;
  resolution: string;
  fps: number;
  quality: string;
}


// T6-001: Mock API service (minimal implementation)
const videoApiService = {
  async getGenerationHistory(): Promise<VideoGeneration[]> {
    try {
      return await apiClient.getGenerationHistory();
    } catch (error) {
      console.error('Failed to get generation history:', error);
      return [];
    }
  },

  async generateVideo(data: VideoGenerationRequest): Promise<{ task_id: string; status: string; message: string }> {
    try {
      // Use existing API client with video parameters
      return await (apiClient as any).generateVideo(data);
    } catch (error) {
      console.error('Failed to generate video:', error);
      throw error;
    }
  },
};

const VideoGenerationDashboard: React.FC = () => {
  const [generations, setGenerations] = useState<VideoGeneration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [retryData, setRetryData] = useState<VideoGenerationRequest | undefined>(undefined);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  // T6-009 REFACTOR: Centralized generation list management
  const generationListManager = {
    // Update or add a generation to the state
    updateGeneration: (updatedGeneration: VideoGeneration) => {
      setGenerations(prevGenerations => {
        const existingIndex = prevGenerations.findIndex(g => g.task_id === updatedGeneration.task_id);
        
        if (existingIndex !== -1) {
          // Replace existing generation
          const newGenerations = [...prevGenerations];
          newGenerations[existingIndex] = updatedGeneration;
          return newGenerations;
        } else {
          // Add new generation at the beginning
          return [updatedGeneration, ...prevGenerations];
        }
      });
    },

    // Get display list combining state and polling data
    getCombinedList: (generations: VideoGeneration[], pollingGeneration: VideoGeneration | null) => {
      if (!pollingGeneration) {
        return generations;
      }

      const existingIndex = generations.findIndex(g => g.task_id === pollingGeneration.task_id);
      
      if (existingIndex !== -1) {
        // Update existing item with latest polling data
        const updatedGenerations = [...generations];
        updatedGenerations[existingIndex] = pollingGeneration;
        return updatedGenerations;
      } else {
        // Add new polling generation at the beginning
        return [pollingGeneration, ...generations];
      }
    }
  };

  // T6-009: UseVideoPolling integration for real-time updates
  const { generation: pollingGeneration, isPolling, error: pollingError, stopPolling, startPolling } = useVideoPolling(currentTaskId, {
    onComplete: (completedGeneration) => {
      console.log('Video generation completed:', completedGeneration);
      // T6-009 REFACTOR: Centralized state management
      generationListManager.updateGeneration(completedGeneration);
      setCurrentTaskId(null); // Clear current task to stop polling display
    },
    onError: (error) => {
      console.error('Polling error:', error);
    }
  });

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const videoGenerations = await videoApiService.getGenerationHistory();
      setGenerations(videoGenerations);
    } catch (err) {
      setError('Failed to load generations. Please try again.');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateVideo = async (data: VideoGenerationRequest) => {
    try {
      setError(null);
      const result = await videoApiService.generateVideo(data);
      
      // T6-009: Start polling for the new video generation
      if (result.task_id) {
        setCurrentTaskId(result.task_id);
        // T6-009 REFACTOR: No need for loadData() - polling will handle updates
        // Real-time updates will be handled by useVideoPolling hook
      }
    } catch (err) {
      setError(`Error: ${(err as Error).message}`);
      throw err; // Re-throw to let form handle the error display
    }
  };

  const handleRetry = (generation: VideoGeneration) => {
    setRetryData({
      prompt: generation.prompt,
      duration_seconds: generation.duration_seconds,
      resolution: generation.resolution,
      fps: generation.fps,
      quality: generation.quality,
    });
    setShowCreateForm(true);
  };

  const handleCancelPolling = () => {
    stopPolling();
    setCurrentTaskId(null);
  };

  // T6-009 REFACTOR: Simplified combined generations using manager
  const combinedGenerations = useMemo(() => 
    generationListManager.getCombinedList(generations, pollingGeneration),
    [pollingGeneration, generations]
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Video Generation Dashboard
        </h1>
        <p className="text-gray-600">
          Manage your video generations and monitor performance
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-red-800">{error}</span>
            <button 
              onClick={loadData}
              className="px-3 py-1 bg-red-100 text-red-800 rounded hover:bg-red-200"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* T6-009: Polling Status Display */}
      {isPolling && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              <span className="text-blue-800">Currently polling for updates...</span>
            </div>
            <button 
              onClick={handleCancelPolling}
              className="px-3 py-1 bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* T6-009: Polling Error Display */}
      {pollingError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-red-800">Polling error: {pollingError.message}</span>
            <button 
              onClick={handleCancelPolling}
              className="px-3 py-1 bg-red-100 text-red-800 rounded hover:bg-red-200"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Cost Management Panel */}
      <CostManagementPanel />

      {/* Controls */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold">Generation History</h2>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Generate Video
        </button>
      </div>

      {/* Generation History */}
      <GenerationHistoryTable
        generations={combinedGenerations}
        onRetry={handleRetry}
      />

      {/* Video Generation Form Modal */}
      <VideoGenerationForm
        isOpen={showCreateForm}
        onClose={() => {
          setShowCreateForm(false);
          setRetryData(undefined);
        }}
        onSubmit={handleGenerateVideo}
        initialData={retryData}
      />
    </main>
  );
};

export default VideoGenerationDashboard;