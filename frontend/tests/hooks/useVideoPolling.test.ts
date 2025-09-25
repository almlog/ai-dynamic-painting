/**
 * useVideoPolling Hook Tests - T6-008 RED Phase
 * 
 * VEO動画生成のポーリング機構テスト
 * 5秒間隔でステータスを取得し、完了/失敗で自動停止
 * 
 * @version v2.6.0
 * @author Claude (博士)
 * @created 2025-09-24 (T6-008 RED Phase)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useVideoPolling } from '../../src/hooks/useVideoPolling';
import { apiClient } from '../../src/services/api';
import type { VideoGeneration } from '../../src/types/video';

// Mock apiClient
vi.mock('../../src/services/api', () => ({
  apiClient: {
    getVideoStatus: vi.fn()
  }
}));

// Global setup
beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  vi.clearAllMocks();
});

// ============================================================================
// MOCK DATA FACTORY - T6-008 品質重視テスト基盤
// ============================================================================

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

describe('useVideoPolling Hook - T6-008 RED Phase', () => {
  
  describe('基本的なポーリング機能', () => {
    it('should start polling when taskId is provided', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const mockGeneration = createMockVideoGeneration();
      vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

      // Act
      const { result } = renderHook(() => useVideoPolling(taskId));

      // Assert - 初期状態
      expect(result.current.isPolling).toBe(true);
      expect(result.current.generation).toBeNull();
      expect(result.current.error).toBeNull();

      // ポーリング開始確認
      await waitFor(() => {
        expect(apiClient.getVideoStatus).toHaveBeenCalledWith(taskId);
      });

      await waitFor(() => {
        expect(result.current.generation).toEqual(mockGeneration);
      });
    });

    it('should poll at 5 second intervals', async () => {
      // Use fake timers for this test
      vi.useFakeTimers();
      
      // Arrange
      const taskId = 'task-test-456';
      const mockGeneration = createMockVideoGeneration({ progress_percent: 25 });
      vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

      // Act
      renderHook(() => useVideoPolling(taskId));

      // 初回呼び出し
      await act(async () => {
        await vi.advanceTimersByTimeAsync(100);
      });
      expect(apiClient.getVideoStatus).toHaveBeenCalledTimes(1);

      // 5秒後に2回目の呼び出し
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
      });
      expect(apiClient.getVideoStatus).toHaveBeenCalledTimes(2);

      // さらに5秒後に3回目の呼び出し
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
      });
      expect(apiClient.getVideoStatus).toHaveBeenCalledTimes(3);
      
      vi.useRealTimers();
    });

    it('should not start polling when taskId is null or empty', () => {
      // Test with null
      const { result: resultNull } = renderHook(() => useVideoPolling(null));
      expect(resultNull.current.isPolling).toBe(false);
      expect(apiClient.getVideoStatus).not.toHaveBeenCalled();

      // Test with empty string
      const { result: resultEmpty } = renderHook(() => useVideoPolling(''));
      expect(resultEmpty.current.isPolling).toBe(false);
      expect(apiClient.getVideoStatus).not.toHaveBeenCalled();

      // Test with undefined
      const { result: resultUndefined } = renderHook(() => useVideoPolling(undefined));
      expect(resultUndefined.current.isPolling).toBe(false);
      expect(apiClient.getVideoStatus).not.toHaveBeenCalled();
    });
  });

  describe('自動停止条件', () => {
    it('should stop polling when status is completed', async () => {
      vi.useFakeTimers();
      
      // Arrange
      const taskId = 'task-test-456';
      const mockProcessing = createMockVideoGeneration({ 
        status: 'processing',
        progress_percent: 90 
      });
      const mockCompleted = createMockVideoGeneration({ 
        status: 'completed',
        progress_percent: 100,
        video_url: 'https://example.com/video.mp4',
        completed_at: '2025-09-24T10:05:00Z'
      });

      vi.mocked(apiClient.getVideoStatus)
        .mockResolvedValueOnce(mockProcessing)
        .mockResolvedValueOnce(mockCompleted);

      // Act
      const { result } = renderHook(() => useVideoPolling(taskId));

      // 初回呼び出し - processing
      await act(async () => {
        await vi.advanceTimersByTimeAsync(100);
      });
      
      await waitFor(() => {
        expect(result.current.generation?.status).toBe('processing');
        expect(result.current.isPolling).toBe(true);
      });

      // 5秒後 - completed
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
      });

      await waitFor(() => {
        expect(result.current.generation?.status).toBe('completed');
        expect(result.current.isPolling).toBe(false);
      });

      // さらに5秒後も呼び出されない（自動停止確認）
      vi.clearAllMocks();
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
      });
      expect(apiClient.getVideoStatus).not.toHaveBeenCalled();
      
      vi.useRealTimers();
    });

    it('should stop polling when status is failed', async () => {
      vi.useFakeTimers();
      
      // Arrange
      const taskId = 'task-test-456';
      const mockProcessing = createMockVideoGeneration({ 
        status: 'processing',
        progress_percent: 50 
      });
      const mockFailed = createMockVideoGeneration({ 
        status: 'failed',
        progress_percent: 0,
        error_message: 'VEO API quota exceeded',
        completed_at: '2025-09-24T10:03:00Z'
      });

      vi.mocked(apiClient.getVideoStatus)
        .mockResolvedValueOnce(mockProcessing)
        .mockResolvedValueOnce(mockFailed);

      // Act
      const { result } = renderHook(() => useVideoPolling(taskId));

      // 初回呼び出し - processing
      await act(async () => {
        await vi.advanceTimersByTimeAsync(100);
      });
      
      await waitFor(() => {
        expect(result.current.generation?.status).toBe('processing');
      });

      // 5秒後 - failed
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
      });

      await waitFor(() => {
        expect(result.current.generation?.status).toBe('failed');
        expect(result.current.generation?.error_message).toBe('VEO API quota exceeded');
        expect(result.current.isPolling).toBe(false);
      });
      
      vi.useRealTimers();
    });
  });

  describe('エラーハンドリング', () => {
    it('should handle network errors gracefully', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const networkError = new Error('Network error');
      vi.mocked(apiClient.getVideoStatus).mockRejectedValueOnce(networkError);

      // Act
      const { result } = renderHook(() => useVideoPolling(taskId));

      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      // Assert
      await waitFor(() => {
        expect(result.current.error).toEqual(networkError);
        expect(result.current.generation).toBeNull();
        expect(result.current.isPolling).toBe(true); // エラーでも継続
      });

      // エラー後も次のポーリングが実行される
      const mockGeneration = createMockVideoGeneration();
      vi.mocked(apiClient.getVideoStatus).mockResolvedValueOnce(mockGeneration);

      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(result.current.error).toBeNull(); // エラーがクリアされる
        expect(result.current.generation).toEqual(mockGeneration);
      });
    });

    it('should handle API errors (404, 401, etc)', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const apiError = new Error('API Error: 404 Not Found');
      vi.mocked(apiClient.getVideoStatus).mockRejectedValueOnce(apiError);

      // Act
      const { result } = renderHook(() => useVideoPolling(taskId));

      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      // Assert
      await waitFor(() => {
        expect(result.current.error).toEqual(apiError);
        expect(result.current.generation).toBeNull();
      });
    });

    it('should clear error when next poll succeeds', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const error = new Error('Temporary error');
      const mockGeneration = createMockVideoGeneration();

      vi.mocked(apiClient.getVideoStatus)
        .mockRejectedValueOnce(error)
        .mockResolvedValueOnce(mockGeneration);

      // Act
      const { result } = renderHook(() => useVideoPolling(taskId));

      // 初回 - エラー
      await act(async () => {
        vi.advanceTimersByTime(100);
      });
      await waitFor(() => {
        expect(result.current.error).toEqual(error);
      });

      // 5秒後 - 成功
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });
      await waitFor(() => {
        expect(result.current.error).toBeNull();
        expect(result.current.generation).toEqual(mockGeneration);
      });
    });
  });

  describe('手動制御機能', () => {
    it('should provide stopPolling function', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const mockGeneration = createMockVideoGeneration();
      vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

      // Act
      const { result } = renderHook(() => useVideoPolling(taskId));

      // ポーリング開始確認
      await act(async () => {
        vi.advanceTimersByTime(100);
      });
      expect(result.current.isPolling).toBe(true);

      // 手動停止
      act(() => {
        result.current.stopPolling();
      });
      expect(result.current.isPolling).toBe(false);

      // 停止後は呼び出されない
      vi.clearAllMocks();
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });
      expect(apiClient.getVideoStatus).not.toHaveBeenCalled();
    });

    it('should provide startPolling function', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const mockGeneration = createMockVideoGeneration();
      vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

      // Act - 初期状態で停止
      const { result } = renderHook(() => useVideoPolling(taskId, { autoStart: false }));
      expect(result.current.isPolling).toBe(false);

      // 手動開始
      act(() => {
        result.current.startPolling();
      });
      expect(result.current.isPolling).toBe(true);

      // ポーリング実行確認
      await act(async () => {
        vi.advanceTimersByTime(100);
      });
      await waitFor(() => {
        expect(apiClient.getVideoStatus).toHaveBeenCalledWith(taskId);
      });
    });
  });

  describe('クリーンアップ処理', () => {
    it('should cleanup interval on unmount', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const mockGeneration = createMockVideoGeneration();
      vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

      // Act
      const { unmount } = renderHook(() => useVideoPolling(taskId));

      // 初回呼び出し
      await act(async () => {
        vi.advanceTimersByTime(100);
      });
      expect(apiClient.getVideoStatus).toHaveBeenCalledTimes(1);

      // アンマウント
      unmount();

      // アンマウント後は呼び出されない
      vi.clearAllMocks();
      await act(async () => {
        vi.advanceTimersByTime(10000); // 2回分の時間
      });
      expect(apiClient.getVideoStatus).not.toHaveBeenCalled();
    });

    it('should prevent memory leaks when taskId changes', async () => {
      // Arrange
      const taskId1 = 'task-001';
      const taskId2 = 'task-002';
      const mockGeneration1 = createMockVideoGeneration({ task_id: taskId1 });
      const mockGeneration2 = createMockVideoGeneration({ task_id: taskId2 });

      vi.mocked(apiClient.getVideoStatus)
        .mockImplementation((id) => {
          if (id === taskId1) return Promise.resolve(mockGeneration1);
          if (id === taskId2) return Promise.resolve(mockGeneration2);
          return Promise.reject(new Error('Unknown task'));
        });

      // Act
      const { result, rerender } = renderHook(
        ({ taskId }) => useVideoPolling(taskId),
        { initialProps: { taskId: taskId1 } }
      );

      // taskId1のポーリング確認
      await act(async () => {
        vi.advanceTimersByTime(100);
      });
      await waitFor(() => {
        expect(result.current.generation?.task_id).toBe(taskId1);
      });

      // taskIdを変更
      rerender({ taskId: taskId2 });

      // 古いポーリングが停止し、新しいポーリングが開始
      vi.clearAllMocks();
      await act(async () => {
        vi.advanceTimersByTime(100);
      });
      await waitFor(() => {
        expect(apiClient.getVideoStatus).toHaveBeenCalledWith(taskId2);
        expect(apiClient.getVideoStatus).not.toHaveBeenCalledWith(taskId1);
        expect(result.current.generation?.task_id).toBe(taskId2);
      });
    });
  });

  describe('オプション設定', () => {
    it('should accept custom polling interval', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const mockGeneration = createMockVideoGeneration();
      vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockGeneration);

      // Act - 3秒間隔でポーリング
      renderHook(() => useVideoPolling(taskId, { interval: 3000 }));

      // 初回
      await act(async () => {
        vi.advanceTimersByTime(100);
      });
      expect(apiClient.getVideoStatus).toHaveBeenCalledTimes(1);

      // 3秒後
      await act(async () => {
        vi.advanceTimersByTime(3000);
      });
      expect(apiClient.getVideoStatus).toHaveBeenCalledTimes(2);

      // さらに3秒後
      await act(async () => {
        vi.advanceTimersByTime(3000);
      });
      expect(apiClient.getVideoStatus).toHaveBeenCalledTimes(3);
    });

    it('should support autoStart option', () => {
      // Arrange
      const taskId = 'task-test-456';

      // Act - autoStart: false
      const { result } = renderHook(() => useVideoPolling(taskId, { autoStart: false }));

      // Assert
      expect(result.current.isPolling).toBe(false);
      expect(apiClient.getVideoStatus).not.toHaveBeenCalled();
    });

    it('should support onComplete callback', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const onComplete = vi.fn();
      const mockCompleted = createMockVideoGeneration({ 
        status: 'completed',
        video_url: 'https://example.com/video.mp4'
      });

      vi.mocked(apiClient.getVideoStatus).mockResolvedValue(mockCompleted);

      // Act
      renderHook(() => useVideoPolling(taskId, { onComplete }));

      // Assert
      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      await waitFor(() => {
        expect(onComplete).toHaveBeenCalledWith(mockCompleted);
      });
    });

    it('should support onError callback', async () => {
      // Arrange
      const taskId = 'task-test-456';
      const onError = vi.fn();
      const error = new Error('Test error');

      vi.mocked(apiClient.getVideoStatus).mockRejectedValue(error);

      // Act
      renderHook(() => useVideoPolling(taskId, { onError }));

      // Assert
      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(error);
      });
    });
  });
});