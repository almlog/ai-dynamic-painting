/**
 * useVideoPolling Hook Simple Tests - T6-008 GREEN Phase
 * 
 * 基本機能確認用のシンプルなテスト
 * 
 * @version v2.6.0
 * @author Claude (博士)
 * @created 2025-09-24
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useVideoPolling } from '../../src/hooks/useVideoPolling';
import { apiClient } from '../../src/services/api';
import type { VideoGeneration } from '../../src/types/video';

// Mock apiClient
vi.mock('../../src/services/api', () => ({
  apiClient: {
    getVideoStatus: vi.fn()
  }
}));

beforeEach(() => {
  vi.clearAllMocks();
});

// Mock Data Factory
const createMockVideoGeneration = (overrides?: Partial<VideoGeneration>): VideoGeneration => ({
  id: 'video-test-123',
  task_id: 'task-test-456',
  prompt: 'A test video generation',
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

describe('useVideoPolling Hook - Simple Tests', () => {
  
  it('should start polling when taskId is provided', async () => {
    const taskId = 'task-test-456';
    const mockGeneration = createMockVideoGeneration();
    vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

    const { result } = renderHook(() => useVideoPolling(taskId));

    // 初期状態
    expect(result.current.isPolling).toBe(true);

    // ポーリング開始確認
    await waitFor(() => {
      expect(apiClient.getVideoStatus).toHaveBeenCalledWith(taskId);
      expect(result.current.generation).toEqual(mockGeneration);
    });
  });

  it('should not start polling when taskId is null', () => {
    const { result } = renderHook(() => useVideoPolling(null));
    expect(result.current.isPolling).toBe(false);
    expect(apiClient.getVideoStatus).not.toHaveBeenCalled();
  });

  it('should not start polling when taskId is empty', () => {
    const { result } = renderHook(() => useVideoPolling(''));
    expect(result.current.isPolling).toBe(false);
    expect(apiClient.getVideoStatus).not.toHaveBeenCalled();
  });

  it('should handle network errors', async () => {
    const taskId = 'task-test-456';
    const networkError = new Error('Network error');
    vi.mocked(apiClient.getVideoStatus).mockRejectedValue(networkError);

    const { result } = renderHook(() => useVideoPolling(taskId));

    await waitFor(() => {
      expect(result.current.error).toEqual(networkError);
      expect(result.current.generation).toBeNull();
    });
  });

  it('should support autoStart option', () => {
    const taskId = 'task-test-456';
    const { result } = renderHook(() => useVideoPolling(taskId, { autoStart: false }));
    expect(result.current.isPolling).toBe(false);
  });

  it('should provide stopPolling function', async () => {
    const taskId = 'task-test-456';
    const mockGeneration = createMockVideoGeneration();
    vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

    const { result } = renderHook(() => useVideoPolling(taskId));

    // ポーリング開始確認
    expect(result.current.isPolling).toBe(true);

    // 手動停止
    const { act } = await import('@testing-library/react');
    act(() => {
      result.current.stopPolling();
    });
    expect(result.current.isPolling).toBe(false);
  });

  it('should provide startPolling function', async () => {
    const taskId = 'task-test-456';
    
    // autoStart: false で開始
    const { result } = renderHook(() => useVideoPolling(taskId, { autoStart: false }));
    expect(result.current.isPolling).toBe(false);

    // 手動開始
    const { act } = await import('@testing-library/react');
    act(() => {
      result.current.startPolling();
    });
    expect(result.current.isPolling).toBe(true);
  });

  it('should stop polling on completed status', async () => {
    const taskId = 'task-test-456';
    const mockCompleted = createMockVideoGeneration({ 
      status: 'completed',
      video_url: 'https://example.com/video.mp4'
    });
    vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockCompleted);

    const { result } = renderHook(() => useVideoPolling(taskId));

    await waitFor(() => {
      expect(result.current.generation?.status).toBe('completed');
      expect(result.current.isPolling).toBe(false);
    });
  });

  it('should stop polling on failed status', async () => {
    const taskId = 'task-test-456';
    const mockFailed = createMockVideoGeneration({ 
      status: 'failed',
      error_message: 'API error'
    });
    vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockFailed);

    const { result } = renderHook(() => useVideoPolling(taskId));

    await waitFor(() => {
      expect(result.current.generation?.status).toBe('failed');
      expect(result.current.isPolling).toBe(false);
    });
  });

  it('should call onComplete callback', async () => {
    const taskId = 'task-test-456';
    const onComplete = vi.fn();
    const mockCompleted = createMockVideoGeneration({ 
      status: 'completed',
      video_url: 'https://example.com/video.mp4'
    });

    vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockCompleted);

    renderHook(() => useVideoPolling(taskId, { onComplete }));

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalledWith(mockCompleted);
    });
  });

  it('should call onError callback', async () => {
    const taskId = 'task-test-456';
    const onError = vi.fn();
    const error = new Error('Test error');

    vi.mocked(apiClient.getVideoStatus).mockRejectedValue(error);

    renderHook(() => useVideoPolling(taskId, { onError }));

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(error);
    });
  });
});