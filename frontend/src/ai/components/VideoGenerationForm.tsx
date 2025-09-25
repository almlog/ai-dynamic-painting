/**
 * VideoGenerationForm - Dedicated form component for video generation
 * T6-002: REFACTOR - Extracted from VideoGenerationDashboard for better separation of concerns
 */

import React, { useState, useEffect } from 'react';

// Form data interface
interface VideoGenerationForm {
  prompt: string;
  duration_seconds: number;
  resolution: string;
  fps: number;
  quality: string;
}

// Request interface for API
interface VideoGenerationRequest {
  prompt: string;
  duration_seconds: number;
  resolution: string;
  fps: number;
  quality: string;
}

// Component props interface
interface VideoGenerationFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: VideoGenerationRequest) => Promise<void>;
  initialData?: VideoGenerationForm;
}

const VideoGenerationForm: React.FC<VideoGenerationFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData
}) => {
  // Form state
  const [formData, setFormData] = useState<VideoGenerationForm>({
    prompt: '',
    duration_seconds: 30,
    resolution: '1080p',
    fps: 30,
    quality: 'standard',
  });

  // Update form data when initial data changes (for retry functionality)
  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        prompt: '',
        duration_seconds: 30,
        resolution: '1080p',
        fps: 30,
        quality: 'standard',
      });
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      // Error handling is managed by parent component
      console.error('Form submission failed:', error);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Generate Video</h3>

        <div className="space-y-4">
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
              Prompt
            </label>
            <textarea
              id="prompt"
              value={formData.prompt}
              onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              rows={3}
              required
            />
          </div>

          <div>
            <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-1">
              Duration (seconds)
            </label>
            <input
              id="duration"
              type="number"
              min="5"
              max="60"
              value={formData.duration_seconds}
              onChange={(e) => setFormData(prev => ({ ...prev, duration_seconds: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label htmlFor="resolution" className="block text-sm font-medium text-gray-700 mb-1">
              Resolution
            </label>
            <select
              id="resolution"
              value={formData.resolution}
              onChange={(e) => setFormData(prev => ({ ...prev, resolution: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="720p">720p</option>
              <option value="1080p">1080p</option>
              <option value="4K">4K</option>
            </select>
          </div>

          <div>
            <label htmlFor="fps" className="block text-sm font-medium text-gray-700 mb-1">
              FPS
            </label>
            <select
              id="fps"
              value={formData.fps}
              onChange={(e) => setFormData(prev => ({ ...prev, fps: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value={24}>24 FPS</option>
              <option value={30}>30 FPS</option>
              <option value={60}>60 FPS</option>
            </select>
          </div>

          <div>
            <label htmlFor="quality" className="block text-sm font-medium text-gray-700 mb-1">
              Quality
            </label>
            <select
              id="quality"
              value={formData.quality}
              onChange={(e) => setFormData(prev => ({ ...prev, quality: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="draft">Draft</option>
              <option value="standard">Standard</option>
              <option value="premium">Premium</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!formData.prompt.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            Generate Video
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoGenerationForm;