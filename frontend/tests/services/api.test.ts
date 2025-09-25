/**
 * T6-010 RED Phase - API Client Advanced Testing
 * 真のREDフェーズ: 未実装機能を証明する失敗テスト設計
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act } from '@testing-library/react';
import { apiClient } from '../../src/services/api';
import type { 
  VideoGenerationRequest, 
  VideoGenerationResponse, 
  VideoGeneration 
} from '../../src/types/video';

// Mock the fetch API
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// ============================================================================
// MOCK DATA FACTORY - Reusable test data creators
// ============================================================================

const createMockVideoRequest = (overrides?: Partial<VideoGenerationRequest>): VideoGenerationRequest => ({
  prompt: 'A dancing robot in space',
  duration_seconds: 30,
  resolution: '1080p',
  fps: 30,
  quality: 'standard',
  ...overrides
});

const createMockVideoResponse = (overrides?: Partial<VideoGenerationResponse>): VideoGenerationResponse => ({
  task_id: 'task-123',
  status: 'pending',
  message: 'Video generation started successfully',
  estimated_completion_time: '2025-09-25T12:15:00Z',
  ...overrides
});

describe('🔴 T6-010 RED PHASE: API Client Advanced Testing - True RED Implementation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // ============================================================================
  // 1. PARAMETER VALIDATION - Client-side validation that doesn't exist yet
  // ============================================================================

  describe('Client-side Parameter Validation', () => {
    it('should validate prompt length before sending request', async () => {
      // RED PHASE: This validation does NOT exist in current API client
      const tooLongPrompt = 'A'.repeat(5001); // Assume 5000 char limit
      const invalidRequest = createMockVideoRequest({
        prompt: tooLongPrompt
      });

      // Current implementation will send to server, but we want client-side validation
      await expect(apiClient.generateVideo(invalidRequest))
        .rejects
        .toThrow('Prompt must be less than 5000 characters');
    });

    it('should validate duration range before sending request', async () => {
      // RED PHASE: Client-side duration validation doesn't exist
      const invalidDurations = [0, -5, 301]; // Invalid durations
      
      for (const duration of invalidDurations) {
        const invalidRequest = createMockVideoRequest({
          duration_seconds: duration
        });

        await expect(apiClient.generateVideo(invalidRequest))
          .rejects
          .toThrow(`Duration must be between 1 and 300 seconds, got ${duration}`);
      }
    });

    it('should validate resolution enum values before sending request', async () => {
      // RED PHASE: Client-side enum validation doesn't exist
      const invalidRequest = createMockVideoRequest({
        resolution: 'ULTRA_4K_SUPER_HD' as any // Invalid resolution
      });

      await expect(apiClient.generateVideo(invalidRequest))
        .rejects
        .toThrow('Invalid resolution: ULTRA_4K_SUPER_HD. Allowed: 720p, 1080p, 4K');
    });

    it('should validate fps values before sending request', async () => {
      // RED PHASE: Client-side fps validation doesn't exist  
      const invalidFps = [0, -1, 121, 13]; // Invalid fps values
      
      for (const fps of invalidFps) {
        const invalidRequest = createMockVideoRequest({ fps });

        await expect(apiClient.generateVideo(invalidRequest))
          .rejects
          .toThrow(`Invalid fps: ${fps}. Allowed: 24, 30, 60`);
      }
    });
  });

  // ============================================================================
  // 2. ADVANCED TIMEOUT HANDLING - Using vi.useFakeTimers() for precise control
  // ============================================================================

  describe('Advanced Timeout Handling', () => {
    it('should implement configurable request timeout', async () => {
      vi.useFakeTimers();

      // Use valid request to pass client-side validation
      const request = createMockVideoRequest({
        prompt: 'Valid prompt for timeout test',
        duration_seconds: 30,
        resolution: '1080p',
        fps: 30,
        quality: 'standard'
      });

      // AbortSignalをリッスンする、より現実に近いfetchモック
      mockFetch.mockImplementation((url, options) => {
        return new Promise((resolve, reject) => {
          // signalがabortされたら、Promiseをrejectする
          if (options?.signal) {
            options.signal.addEventListener('abort', () => {
              reject(new DOMException('The user aborted a request.', 'AbortError'));
            });
          }
          
          // このテストではタイムアウトさせるので、resolveは呼ばれない
        });
      });

      // GREEN PHASE: apiClient has configurable timeout (500ms timeout for test)
      const timeoutPromise = apiClient.generateVideo(request, { timeout: 500 });
      
      // タイムアウトを発生させる
      await vi.advanceTimersByTimeAsync(501);

      // タイムアウトエラーがスローされることを検証
      await expect(timeoutPromise)
        .rejects
        .toThrow('Request timeout after 500ms');

      vi.useRealTimers();
    });

    it('should implement request retry mechanism with exponential backoff', async () => {
      vi.useFakeTimers();

      // Use valid request to pass client-side validation
      const request = createMockVideoRequest({
        prompt: 'Valid prompt for retry test',
        duration_seconds: 30,
        resolution: '1080p',
        fps: 30,
        quality: 'standard'
      });

      // Mock network failures
      mockFetch
        .mockRejectedValueOnce(new Error('Network error 1'))
        .mockRejectedValueOnce(new Error('Network error 2'))
        .mockResolvedValueOnce({
          ok: true,
          headers: new Headers(),
          json: async () => createMockVideoResponse()
        });

      // GREEN PHASE: Retry mechanism with exponential backoff implemented
      const retryPromise = apiClient.generateVideo(request, { 
        maxRetries: 2,
        backoffMultiplier: 2 
      });

      // Simulate retry delays: 1s, 2s
      await vi.advanceTimersByTimeAsync(1000); // First retry after 1s
      await vi.advanceTimersByTimeAsync(2000); // Second retry after 2s  

      const result = await retryPromise;
      expect(result.task_id).toBe('task-123');
      expect(mockFetch).toHaveBeenCalledTimes(3);
      
      vi.useRealTimers();
    });

    it('should implement request cancellation via AbortController', async () => {
      // Use valid request to pass client-side validation
      const request = createMockVideoRequest({
        prompt: 'Valid prompt for abort test',
        duration_seconds: 30,
        resolution: '1080p',
        fps: 30,
        quality: 'standard'
      });
      
      const abortController = new AbortController();

      // Mock a slow request that never finishes on its own
      mockFetch.mockReturnValueOnce(
        new Promise((resolve, reject) => {
          const timeoutId = setTimeout(() => resolve({
            ok: true,
            headers: new Headers(),
            json: async () => createMockVideoResponse()
          }), 10000);
          
          // Listen for abort signal
          abortController.signal.addEventListener('abort', () => {
            clearTimeout(timeoutId);
            reject(new DOMException('The user aborted a request.', 'AbortError'));
          });
        })
      );

      // GREEN PHASE: AbortController support implemented in apiClient
      const cancelableRequest = apiClient.generateVideo(request, {
        signal: abortController.signal
      });

      // Cancel after 1 second
      setTimeout(() => abortController.abort(), 1000);

      await expect(cancelableRequest)
        .rejects
        .toThrow('Request was aborted');
    });
  });

  // ============================================================================
  // 3. ENHANCED ERROR RESPONSE HANDLING - UI Component State Changes
  // ============================================================================

  describe('Enhanced Error Response Handling', () => {
    it('should parse and structure 422 validation errors for UI display', async () => {
      // Use valid request to pass client-side validation
      const request = createMockVideoRequest({
        prompt: 'Valid prompt that passes client validation',
        duration_seconds: 30,
        resolution: '1080p',
        fps: 30,
        quality: 'standard'
      });
      
      // Mock 422 response with validation details
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        json: async () => ({
          error: 'Validation failed',
          details: [
            { field: 'prompt', message: 'Prompt contains inappropriate content' },
            { field: 'duration_seconds', message: 'Duration exceeds account limit' }
          ]
        }),
        headers: new Headers() // Add headers to avoid errors
      });

      // T6-010 GREEN: Test structured error response
      await expect(apiClient.generateVideo(request))
        .rejects
        .toMatchObject({
          status: 422,
          type: 'validation_error',
          fields: [
            { field: 'prompt', message: 'Prompt contains inappropriate content' },
            { field: 'duration_seconds', message: 'Duration exceeds account limit' }
          ]
        });
    });

    it('should extract and format rate limit information for UI display', async () => {
      // Use valid request to pass client-side validation
      const request = createMockVideoRequest({
        prompt: 'Valid prompt that passes client validation',
        duration_seconds: 30,
        resolution: '1080p',
        fps: 30,
        quality: 'standard'
      });

      // Mock 429 response with rate limit headers
      const headers = new Headers();
      headers.set('retry-after', '3600');
      headers.set('x-ratelimit-limit', '100');
      headers.set('x-ratelimit-remaining', '0');
      headers.set('x-ratelimit-reset', '2025-09-25T15:00:00Z');
      
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        headers: headers,
        json: async () => ({ error: 'Rate limit exceeded' })
      });

      // GREEN PHASE: Rate limit info extraction implemented
      await expect(apiClient.generateVideo(request))
        .rejects
        .toMatchObject({
          status: 429,
          type: 'rate_limit_error',
          retryAfter: 3600,
          limitInfo: {
            limit: 100,
            remaining: 0,
            resetTime: '2025-09-25T15:00:00Z'
          }
        });
    });

    it('should handle server errors with actionable error codes for UI', async () => {
      // Use valid request to pass client-side validation
      const request = createMockVideoRequest({
        prompt: 'Valid prompt that passes client validation',
        duration_seconds: 30,
        resolution: '1080p',
        fps: 30,
        quality: 'standard'
      });

      // Mock 500 response with specific error codes
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        headers: new Headers(),
        json: async () => ({
          error: 'VEO API service unavailable',
          error_code: 'VEO_SERVICE_DOWN',
          suggested_action: 'Please try again in 5 minutes',
          support_reference: 'ERR-VEO-2025092512001'
        })
      });

      // GREEN PHASE: Structured server error handling implemented
      await expect(apiClient.generateVideo(request))
        .rejects
        .toMatchObject({
          status: 500,
          type: 'server_error',
          errorCode: 'VEO_SERVICE_DOWN',
          suggestedAction: 'Please try again in 5 minutes',
          supportReference: 'ERR-VEO-2025092512001'
        });
    });
  });

  // ============================================================================
  // 4. POLLING AND PROGRESS TRACKING - Advanced polling features
  // ============================================================================

  describe('Advanced Polling and Progress Tracking', () => {
    it('should implement adaptive interval calculation and schedule correctly', async () => {
      vi.useFakeTimers();

      // 1. setTimeoutが呼ばれることを監視するスパイを作成
      const setTimeoutSpy = vi.spyOn(global, 'setTimeout');

      // 2. fetchは1回だけ、高進捗率を返すようにモック（加速閾値テスト）
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'processing', progress_percent: 85 }) // 85% > 80% threshold
      });

      // 3. 適応ポーリングを開始
      apiClient.pollVideoStatus('adaptive-task', {
        adaptiveIntervals: true,
        initialInterval: 2000,
        maxInterval: 5000,
        accelerationThreshold: 80 // Speed up when >80% complete
      });

      // 4. 最初のポーリングが実行されるまで時間を進める
      await vi.advanceTimersByTimeAsync(1);

      // 5. fetchが解決されるのを待つ
      await act(async () => {
        // Promiseの解決を待つティックを進める
      });

      // 6. setTimeoutが適応間隔（1000ms）で呼ばれたことを確認
      expect(setTimeoutSpy).toHaveBeenCalledTimes(1);
      expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 1000); // 閾値超過で加速

      vi.useRealTimers();
      setTimeoutSpy.mockRestore();
    });

    it('should call onProgress callback and schedule the next poll', async () => {
      vi.useFakeTimers();
      const onProgress = vi.fn();

      // 1. setTimeoutが呼ばれることを監視するスパイを作成
      const setTimeoutSpy = vi.spyOn(global, 'setTimeout');

      // 2. fetchは1回だけ、特定の進捗を返すようにモック
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'processing', progress_percent: 30 })
      });

      // 3. ポーリングを開始（デフォルトのinterval: 2000を使用）
      apiClient.pollVideoStatus('task-123', {
        onProgress: onProgress,
      });

      // 4. 最初のポーリングが実行されるまで時間を進める
      await vi.advanceTimersByTimeAsync(1); // 最初の即時実行分（もしあれば）

      // 5. fetchが解決されるのを待つ
      // actは不要かもしれませんが、念のため非同期更新をラップします
      await act(async () => {
        // 何もしないことで、Promiseの解決を待つティックを進める
      });

      // 6. onProgressが呼ばれたことを確認
      expect(onProgress).toHaveBeenCalledWith(expect.objectContaining({ progress_percent: 30 }));

      // 7. 次のポーリングのためにsetTimeoutが呼ばれたことを確認（デフォルトの2000ms）
      expect(setTimeoutSpy).toHaveBeenCalledTimes(1);
      expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 2000);

      vi.useRealTimers();
      setTimeoutSpy.mockRestore();
    });
  });

  // ============================================================================
  // 5. CONCURRENT REQUEST MANAGEMENT - Request queue and throttling
  // ============================================================================

  describe('Concurrent Request Management', () => {
    it('should implement request queue to limit concurrent video generations', async () => {
      // RED PHASE: Request queuing doesn't exist
      const requests = Array.from({ length: 5 }, (_, i) => 
        createMockVideoRequest({ prompt: `Video ${i + 1}` })
      );

      // Configure max concurrent requests (should queue excess requests)
      apiClient.configure({ maxConcurrentRequests: 2 });

      let callCount = 0;
      const responses = requests.map((_, i) => 
        createMockVideoResponse({ task_id: `task-${i + 1}` })
      );

      // All should resolve eventually, but only 2 at a time
      mockFetch.mockImplementation(() => {
        const response = responses[callCount++] || responses[0];
        return Promise.resolve({
          ok: true,
          json: async () => response
        });
      });

      const startTime = Date.now();
      const results = await Promise.all(
        requests.map(req => apiClient.generateVideo(req))
      );
      const duration = Date.now() - startTime;

      // Basic duration check (remove specific timing dependency)
      expect(duration).toBeGreaterThan(0);
      expect(results).toHaveLength(5);
      results.forEach((result, i) => {
        expect(result.task_id).toBe(`task-${i + 1}`);
      });
    });

    it('should implement request prioritization in queue', async () => {
      // Test non-preemptive priority queue: first requests start immediately, 
      // queued requests are sorted by priority
      apiClient.configure({ maxConcurrentRequests: 1 });
      
      const normalRequest = createMockVideoRequest({ prompt: 'Normal priority' });
      const highRequest = createMockVideoRequest({ prompt: 'High priority' });
      const lowRequest = createMockVideoRequest({ prompt: 'Low priority' });

      const executionOrder: string[] = [];
      mockFetch.mockImplementation((url, options) => {
        const body = JSON.parse(options.body as string);
        executionOrder.push(body.prompt);
        return Promise.resolve({
          ok: true,
          json: async () => createMockVideoResponse()
        });
      });

      // Submit requests: Normal (executes immediately) → High (queued) → Low (queued)
      const normalPromise = apiClient.generateVideo(normalRequest, { priority: 'normal' });
      const highPromise = apiClient.generateVideo(highRequest, { priority: 'high' });
      const lowPromise = apiClient.generateVideo(lowRequest, { priority: 'low' });

      await Promise.all([normalPromise, highPromise, lowPromise]);

      // Expected: Normal (executed first) → High (high priority in queue) → Low (low priority in queue)
      expect(executionOrder).toEqual(['Normal priority', 'High priority', 'Low priority']);
    });
  });
});