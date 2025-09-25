/**
 * VideoGenerationDashboard - TDD RED Phase Tests
 * T6-001: 期待する動作を定義した失敗テスト
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Mock API client - must be defined before mock
vi.mock('../../src/services/api', () => ({
  apiClient: {
    generateVideo: vi.fn(),
    getVideoStatus: vi.fn(),
    getGenerationHistory: vi.fn(),
    cancelGeneration: vi.fn(),
  },
  isGenerationComplete: (status: string) => status === 'completed',
  isGenerationFailed: (status: string) => status === 'failed',
  isGenerationInProgress: (status: string) => status === 'processing',
}));

// Mock useVideoPolling hook for T6-009
vi.mock('../../src/hooks/useVideoPolling', () => ({
  useVideoPolling: vi.fn(),
}));

import VideoGenerationDashboard from '../../src/ai/components/VideoGenerationDashboard';
import { apiClient } from '../../src/services/api';
import { useVideoPolling } from '../../src/hooks/useVideoPolling';

// Console error mock for clean test output
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

// T6-009 REFACTOR R02: Test utilities for DRY principle
const mockVideoGeneration = (overrides?: Partial<VideoGeneration>): VideoGeneration => ({
  id: 'test-video-id',
  task_id: 'test-task-id',
  prompt: 'Test video prompt',
  status: 'processing',
  progress_percent: 50,
  video_url: null,
  thumbnail_url: null,
  duration_seconds: 30,
  resolution: '1080p',
  fps: 30,
  quality: 'standard',
  cost: 0,
  error_message: null,
  created_at: '2025-09-24T10:00:00Z',
  updated_at: '2025-09-24T10:01:00Z',
  completed_at: null,
  ...overrides
});

const setupMockPolling = (config: {
  generation?: VideoGeneration | null;
  isPolling?: boolean;
  error?: Error | null;
  startPolling?: any;
  stopPolling?: any;
} = {}) => {
  const mockStartPolling = vi.fn();
  const mockStopPolling = vi.fn();
  
  vi.mocked(useVideoPolling).mockReturnValue({
    generation: config.generation ?? null,
    isPolling: config.isPolling ?? false,
    error: config.error ?? null,
    startPolling: config.startPolling ?? mockStartPolling,
    stopPolling: config.stopPolling ?? mockStopPolling,
  });

  return { mockStartPolling, mockStopPolling };
};

describe('VideoGenerationDashboard - TDD RED Phase', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.getGenerationHistory as any).mockResolvedValue([]);
    
    // Default useVideoPolling mock using utility
    setupMockPolling();
  });

  afterEach(() => {
    consoleSpy.mockClear();
  });

  // Test 1: Component should render with title
  it('should render video generation dashboard with correct title', async () => {
    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    expect(screen.getByText('Video Generation Dashboard')).toBeInTheDocument();
    expect(screen.getByText(/Manage your video generations/i)).toBeInTheDocument();
  });

  // Test 2: Should display video generation form
  it('should display video generation form with all required fields', async () => {
    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    // Click to open the form modal
    const generateButton = screen.getByRole('button', { name: /generate video/i });
    await act(async () => {
      fireEvent.click(generateButton);
    });

    // Video-specific form fields
    expect(screen.getByLabelText(/prompt/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/duration/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/resolution/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/fps/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/quality/i)).toBeInTheDocument();
  });

  // Test 3: Should display generation history table with video columns
  it('should display generation history table with video-specific columns', async () => {
    const mockVideoGeneration = {
      id: 'video-1',
      task_id: 'task-123',
      prompt: 'A beautiful sunset',
      status: 'completed',
      duration_seconds: 30,
      resolution: '1080p',
      fps: 30,
      quality: 'standard',
      video_url: 'https://example.com/video.mp4',
      cost: 0.90,
      created_at: '2025-09-23T10:00:00Z',
      progress_percent: 100,
    };

    (apiClient.getGenerationHistory as any).mockResolvedValue([mockVideoGeneration]);

    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Generation History')).toBeInTheDocument();
      expect(screen.getByText('Prompt')).toBeInTheDocument();
      expect(screen.getByText('Duration')).toBeInTheDocument();
      expect(screen.getByText('Resolution')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Cost')).toBeInTheDocument();
    });
  });

  // Test 4: Should handle video generation form submission
  it('should handle video generation form submission with correct parameters', async () => {
    (apiClient as any).generateVideo.mockResolvedValue({
      task_id: 'task-456',
      status: 'processing',
      message: 'Video generation started',
    });

    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    // Open the form modal first
    const generateButton = screen.getByRole('button', { name: /generate video/i });
    await act(async () => {
      fireEvent.click(generateButton);
    });

    // Fill form with video parameters
    const promptInput = screen.getByLabelText(/prompt/i);
    const durationInput = screen.getByLabelText(/duration/i);
    // Get the submit button inside the modal (the second one)
    const submitButtons = screen.getAllByRole('button', { name: /generate video/i });
    const submitButton = submitButtons[1]; // The modal submit button

    await act(async () => {
      fireEvent.change(promptInput, { target: { value: 'A dancing robot' } });
      fireEvent.change(durationInput, { target: { value: '30' } });
      fireEvent.click(submitButton);
    });

    expect((apiClient as any).generateVideo).toHaveBeenCalledWith({
      prompt: 'A dancing robot',
      duration_seconds: 30,
      resolution: '1080p',
      fps: 30,
      quality: 'standard',
    });
  });

  // Test 5: Should display progress for processing videos
  it('should display progress bar for processing video generation', async () => {
    const processingVideo = {
      id: 'video-2',
      task_id: 'task-789',
      prompt: 'Processing video',
      status: 'processing',
      progress_percent: 45,
      duration_seconds: 30,
      resolution: '1080p',
      fps: 30,
      quality: 'standard',
      created_at: '2025-09-23T10:30:00Z',
    };

    (apiClient.getGenerationHistory as any).mockResolvedValue([processingVideo]);

    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    await waitFor(() => {
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toBeInTheDocument();
      expect(progressBar).toHaveAttribute('aria-valuenow', '45');
      expect(screen.getByText('45%')).toBeInTheDocument();
    });
  });

  // Test 6: Should display cost management panel
  it('should display cost management panel with budget tracking', async () => {
    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    expect(screen.getByRole('heading', { name: /daily budget/i })).toBeInTheDocument();
    expect(screen.getByText(/total cost/i)).toBeInTheDocument();
    expect(screen.getByText(/remaining budget/i)).toBeInTheDocument();
  });

  // Test 7: Should display video preview for completed generations
  it('should display video preview for completed generations', async () => {
    const completedVideo = {
      id: 'video-3',
      task_id: 'task-999',
      prompt: 'Completed video',
      status: 'completed',
      video_url: 'https://example.com/completed.mp4',
      duration_seconds: 30,
      resolution: '1080p',
      fps: 30,
      quality: 'standard',
      cost: 0.90,
      created_at: '2025-09-23T11:00:00Z',
      progress_percent: 100,
    };

    (apiClient.getGenerationHistory as any).mockResolvedValue([completedVideo]);

    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    await waitFor(() => {
      const videoElement = screen.getByRole('button', { name: /play video/i });
      expect(videoElement).toBeInTheDocument();
      expect(screen.getByText(/download/i)).toBeInTheDocument();
    });
  });

  // Test 8: Should handle error states appropriately
  it('should handle error states with proper error messages', async () => {
    const failedVideo = {
      id: 'video-4',
      task_id: 'task-error',
      prompt: 'Failed video',
      status: 'failed',
      error_message: 'VEO API quota exceeded',
      duration_seconds: 30,
      resolution: '1080p',
      fps: 30,
      quality: 'standard',
      created_at: '2025-09-23T11:30:00Z',
      progress_percent: 0,
    };

    (apiClient.getGenerationHistory as any).mockResolvedValue([failedVideo]);

    await act(async () => {
      render(<VideoGenerationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('VEO API quota exceeded')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });
  });

  // ============================================================================
  // T6-009 RED Phase: useVideoPolling統合テスト (失敗するテストを先に作成)
  // ============================================================================

  describe('useVideoPolling統合テスト - T6-009 RED Phase', () => {
    it('should integrate useVideoPolling hook and display polling status', async () => {
      // Arrange - ポーリング中の状態をモック
      setupMockPolling({
        generation: mockVideoGeneration({
          id: 'video-polling-test',
          task_id: 'task-polling-123',
          prompt: 'A test video being polled',
          progress_percent: 75,
          updated_at: '2025-09-24T10:03:00Z',
        }),
        isPolling: true
      });

      // Act
      await act(async () => {
        render(<VideoGenerationDashboard />);
      });

      // Assert - ポーリングステータスが表示されているか
      await waitFor(() => {
        expect(screen.getByText('Currently polling for updates...')).toBeInTheDocument();
        expect(screen.getByText('75%')).toBeInTheDocument();
        expect(screen.getByText('A test video being polled')).toBeInTheDocument();
      });
    });

    it('should call startPolling when new video generation is submitted', async () => {
      // Arrange
      const { mockStartPolling } = setupMockPolling();

      (apiClient as any).generateVideo.mockResolvedValue({
        task_id: 'new-task-456',
        status: 'processing',
        message: 'Video generation started',
      });

      // Act
      await act(async () => {
        render(<VideoGenerationDashboard />);
      });

      // 生成フォーム送信
      const generateButton = screen.getByRole('button', { name: /generate video/i });
      await act(async () => {
        fireEvent.click(generateButton);
      });

      const promptInput = screen.getByLabelText(/prompt/i);
      const submitButtons = screen.getAllByRole('button', { name: /generate video/i });
      const submitButton = submitButtons[1];

      await act(async () => {
        fireEvent.change(promptInput, { target: { value: 'New video' } });
        fireEvent.click(submitButton);
      });

      // Assert - useVideoPollingが新しいtask_idで呼ばれているか
      await waitFor(() => {
        expect(useVideoPolling).toHaveBeenCalledWith('new-task-456', expect.any(Object));
      });
    });

    it('should display completed video from polling hook', async () => {
      // Arrange - 完了した動画をモック
      setupMockPolling({
        generation: mockVideoGeneration({
          id: 'video-completed',
          task_id: 'task-completed-789',
          prompt: 'Completed video from polling',
          status: 'completed',
          progress_percent: 100,
          video_url: 'https://example.com/completed-polling.mp4',
          cost: 1.20,
          updated_at: '2025-09-24T10:05:00Z',
          completed_at: '2025-09-24T10:05:00Z',
        }),
        isPolling: false
      });

      // Act
      await act(async () => {
        render(<VideoGenerationDashboard />);
      });

      // Assert - 完了した動画が表示されているか
      await waitFor(() => {
        expect(screen.getByText('Completed video from polling')).toBeInTheDocument();
        expect(screen.getByText('completed')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /play video/i })).toBeInTheDocument();
        expect(screen.getByText('$1.20')).toBeInTheDocument();
      });
    });

    it('should display error from polling hook', async () => {
      // Arrange - エラー状態をモック
      setupMockPolling({
        error: new Error('Network error during polling')
      });

      // Act
      await act(async () => {
        render(<VideoGenerationDashboard />);
      });

      // Assert - エラーメッセージが表示されているか
      await waitFor(() => {
        expect(screen.getByText('Polling error: Network error during polling')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /dismiss/i })).toBeInTheDocument();
      });
    });

    it('should stop polling when user manually cancels', async () => {
      // Arrange
      const { mockStopPolling } = setupMockPolling({
        generation: mockVideoGeneration({
          id: 'video-processing',
          task_id: 'task-processing-999',
          prompt: 'Processing video to be cancelled',
          updated_at: '2025-09-24T10:02:30Z',
        }),
        isPolling: true
      });

      // Act
      await act(async () => {
        render(<VideoGenerationDashboard />);
      });

      // キャンセルボタンをクリック
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await act(async () => {
        fireEvent.click(cancelButton);
      });

      // Assert - stopPollingが呼ばれているか
      expect(mockStopPolling).toHaveBeenCalled();
    });

    it('should update GenerationHistoryTable with polling data', async () => {
      // Arrange - ポーリングで取得したデータをモック
      setupMockPolling({
        generation: mockVideoGeneration({
          id: 'video-history-update',
          task_id: 'task-history-111',
          prompt: 'History update test',
          progress_percent: 85,
          duration_seconds: 45,
          resolution: '4k',
          fps: 60,
          quality: 'premium',
          updated_at: '2025-09-24T10:04:15Z',
        }),
        isPolling: true
      });

      // 既存履歴もモック（ポーリングデータとマージされるべき）
      (apiClient.getGenerationHistory as any).mockResolvedValue([
        {
          id: 'video-existing',
          task_id: 'task-existing-222',
          prompt: 'Existing video',
          status: 'completed',
          progress_percent: 100,
          video_url: 'https://example.com/existing.mp4',
          duration_seconds: 30,
          resolution: '1080p',
          fps: 30,
          quality: 'standard',
          cost: 0.90,
          created_at: '2025-09-24T09:00:00Z',
        }
      ]);

      // Act
      await act(async () => {
        render(<VideoGenerationDashboard />);
      });

      // Assert - 両方のデータが表示されているか（ポーリングデータが上位）
      await waitFor(() => {
        expect(screen.getByText('History update test')).toBeInTheDocument();
        expect(screen.getByText('Existing video')).toBeInTheDocument();
        expect(screen.getByText('85%')).toBeInTheDocument();
        expect(screen.getByText('4k')).toBeInTheDocument();
        expect(screen.getByText('45s')).toBeInTheDocument(); // duration表示
      });
    });
  });
});