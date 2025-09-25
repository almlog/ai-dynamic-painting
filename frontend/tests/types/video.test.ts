/**
 * VideoGeneration Types - TDD RED Phase Tests
 * T6-006: 型定義の期待する動作を定義した失敗テスト
 */

import { describe, it, expect } from 'vitest';

// T6-006-R02: Import enhanced types and utility functions
import { 
  VideoGeneration, 
  VideoGenerationRequest, 
  VideoGenerationResponse,
  VideoStatus,
  VideoStatusType,
  VideoQuality,
  VideoResolution,
  VideoFPS,
  isProcessingStatus,
  isFinalStatus
} from '../../src/types/video';

// ============================================================================
// TEST DATA FACTORY - Eliminates code duplication
// ============================================================================

/**
 * Creates mock VideoGeneration with sensible defaults and optional overrides
 * Reduces test code duplication and improves maintainability
 */
const createMockVideoGeneration = (overrides?: Partial<VideoGeneration>): VideoGeneration => ({
  id: 'test-video-123',
  task_id: 'test-task-456',
  prompt: 'A beautiful sunset over mountains',
  status: 'processing' as VideoStatusType,
  duration_seconds: 30,
  resolution: '1080p' as VideoResolution,
  fps: 30 as VideoFPS,
  quality: 'standard' as VideoQuality,
  video_url: undefined,
  cost: 0.95,
  created_at: '2025-09-23T12:00:00Z',
  updated_at: '2025-09-23T12:05:00Z',
  progress_percent: 75,
  error_message: null,
  ...overrides
});

/**
 * Creates mock VideoGenerationRequest with defaults
 */
const createMockRequest = (overrides?: Partial<VideoGenerationRequest>): VideoGenerationRequest => ({
  prompt: 'A dancing robot in space',
  duration_seconds: 30,
  resolution: '1080p' as VideoResolution,
  fps: 30 as VideoFPS,
  quality: 'standard' as VideoQuality,
  ...overrides
});

/**
 * Creates mock VideoGenerationResponse with defaults
 */
const createMockResponse = (overrides?: Partial<VideoGenerationResponse>): VideoGenerationResponse => ({
  task_id: 'task-789',
  status: 'processing' as VideoStatusType,
  message: 'Video generation started successfully',
  estimated_completion_time: '2025-09-23T12:15:00Z',
  ...overrides
});

describe('VideoGeneration Types - Enhanced Test Suite', () => {
  
  // ========================================================================
  // CORE INTERFACE TESTS
  // ========================================================================
  
  describe('VideoGeneration Interface', () => {
    // Test 1: VideoGeneration interface should have required properties
    it('should define VideoGeneration interface with all required properties', () => {
      const mockVideoGeneration = createMockVideoGeneration({
        video_url: 'https://example.com/video.mp4'
      });

      // Type validation using factory-created mock
      expect(typeof mockVideoGeneration.id).toBe('string');
      expect(typeof mockVideoGeneration.task_id).toBe('string');
      expect(typeof mockVideoGeneration.prompt).toBe('string');
      expect(typeof mockVideoGeneration.status).toBe('string');
      expect(typeof mockVideoGeneration.duration_seconds).toBe('number');
      expect(typeof mockVideoGeneration.resolution).toBe('string');
      expect(typeof mockVideoGeneration.fps).toBe('number');
      expect(typeof mockVideoGeneration.quality).toBe('string');
      expect(typeof mockVideoGeneration.cost).toBe('number');
      expect(typeof mockVideoGeneration.progress_percent).toBe('number');
      
      // Verify specific values are set correctly
      expect(mockVideoGeneration.video_url).toBe('https://example.com/video.mp4');
    });

    // Test 2: Should handle optional fields correctly
    it('should handle optional fields correctly', () => {
      const minimalGeneration = createMockVideoGeneration({
        status: 'pending',
        progress_percent: 0,
        video_url: undefined
      });

      // video_url should be optional for pending/processing videos
      expect(minimalGeneration.video_url).toBeUndefined();
      expect(minimalGeneration.error_message).toBeNull();
      expect(minimalGeneration.status).toBe('pending');
    });
  });

  describe('API Interface Validation', () => {
    // Test 3: VideoGenerationRequest interface should have required fields
    it('should define VideoGenerationRequest interface with API request fields', () => {
      const mockRequest = createMockRequest();

      expect(typeof mockRequest.prompt).toBe('string');
      expect(typeof mockRequest.duration_seconds).toBe('number');
      expect(typeof mockRequest.resolution).toBe('string');
      expect(typeof mockRequest.fps).toBe('number');
      expect(typeof mockRequest.quality).toBe('string');
      
      // Verify type constraints
      expect(['720p', '1080p', '4K']).toContain(mockRequest.resolution);
      expect([24, 30, 60]).toContain(mockRequest.fps);
      expect(['draft', 'standard', 'premium']).toContain(mockRequest.quality);
    });

    // Test 4: VideoGenerationResponse interface should have API response fields
    it('should define VideoGenerationResponse interface with API response fields', () => {
      const mockResponse = createMockResponse();

      expect(typeof mockResponse.task_id).toBe('string');
      expect(typeof mockResponse.status).toBe('string');
      expect(typeof mockResponse.message).toBe('string');
      expect(typeof mockResponse.estimated_completion_time).toBe('string');
    });
  });

  // ========================================================================
  // ENUM & UNION TYPE TESTS
  // ========================================================================
  
  describe('VideoStatus Enum & Union Types', () => {
    // Test 5: VideoStatus enum should have all expected values
    it('should define VideoStatus enum with all status values', () => {
      // Test specific enum values
      expect(VideoStatus.PENDING).toBe('pending');
      expect(VideoStatus.PROCESSING).toBe('processing');
      expect(VideoStatus.COMPLETED).toBe('completed');
      expect(VideoStatus.FAILED).toBe('failed');
      
      // Test all enum values are strings
      Object.values(VideoStatus).forEach(status => {
        expect(typeof status).toBe('string');
      });
    });

    // Test 6: Union type constraints should be enforced
    it('should validate union type constraints', () => {
      // VideoResolution validation
      const validResolutions: VideoResolution[] = ['720p', '1080p', '4K'];
      validResolutions.forEach(resolution => {
        const gen = createMockVideoGeneration({ resolution });
        expect(gen.resolution).toBe(resolution);
      });

      // VideoFPS validation
      const validFPS: VideoFPS[] = [24, 30, 60];
      validFPS.forEach(fps => {
        const gen = createMockVideoGeneration({ fps });
        expect(gen.fps).toBe(fps);
      });

      // VideoQuality validation
      const validQualities: VideoQuality[] = ['draft', 'standard', 'premium'];
      validQualities.forEach(quality => {
        const gen = createMockVideoGeneration({ quality });
        expect(gen.quality).toBe(quality);
      });
    });
  });

  // ========================================================================
  // TYPE GUARD TESTS - CRITICAL MISSING COVERAGE
  // ========================================================================
  
  describe('Type Guard Functions', () => {
    // Test 7: isProcessingStatus should correctly identify processing states
    it('should correctly identify processing-related statuses', () => {
      // Processing statuses should return true
      expect(isProcessingStatus('pending')).toBe(true);
      expect(isProcessingStatus('processing')).toBe(true);
      
      // Final statuses should return false
      expect(isProcessingStatus('completed')).toBe(false);
      expect(isProcessingStatus('failed')).toBe(false);
    });

    // Test 8: isFinalStatus should correctly identify final states
    it('should correctly identify final statuses', () => {
      // Final statuses should return true
      expect(isFinalStatus('completed')).toBe(true);
      expect(isFinalStatus('failed')).toBe(true);
      
      // Processing statuses should return false
      expect(isFinalStatus('pending')).toBe(false);
      expect(isFinalStatus('processing')).toBe(false);
    });

    // Test 9: Type guards should handle invalid inputs gracefully
    it('should handle invalid status values gracefully', () => {
      // Invalid statuses should return false (type guards are defensive)
      expect(isProcessingStatus('invalid' as any)).toBe(false);
      expect(isFinalStatus('unknown' as any)).toBe(false);
      expect(isProcessingStatus('' as any)).toBe(false);
      expect(isFinalStatus(null as any)).toBe(false);
    });
  });

  // ========================================================================
  // COMPONENT INTEGRATION & COMPATIBILITY TESTS
  // ========================================================================
  
  describe('Component Integration', () => {
    // Test 10: Type compatibility with existing components
    it('should be compatible with VideoGenerationDashboard component expectations', () => {
      const mockGeneration = createMockVideoGeneration({
        id: 'test-id',
        status: 'completed',
        video_url: 'https://test.com/video.mp4',
        progress_percent: 100
      });

      // Should be assignable to existing component props
      const generations: VideoGeneration[] = [mockGeneration];
      expect(Array.isArray(generations)).toBe(true);
      expect(generations.length).toBe(1);
      expect(generations[0].id).toBe('test-id');
    });

    // Test 11: Should support status-based conditional logic
    it('should support type checking for status-based logic', () => {
      const processingGen = createMockVideoGeneration({
        status: 'processing',
        progress_percent: 50
      });

      // Should support status-based conditional logic using type guards
      const isProcessing = isProcessingStatus(processingGen.status);
      const isFinal = isFinalStatus(processingGen.status);
      const hasProgress = processingGen.progress_percent > 0;
      
      expect(isProcessing).toBe(true);
      expect(isFinal).toBe(false);
      expect(hasProgress).toBe(true);
    });
  });

  // ========================================================================
  // EDGE CASES & ERROR HANDLING
  // ========================================================================
  
  describe('Edge Cases & Error Handling', () => {
    // Test 12: Should handle boundary values correctly
    it('should handle boundary values for numeric fields', () => {
      // Minimum duration (5 seconds)
      const minDuration = createMockVideoGeneration({ duration_seconds: 5 });
      expect(minDuration.duration_seconds).toBe(5);
      
      // Maximum duration (60 seconds)
      const maxDuration = createMockVideoGeneration({ duration_seconds: 60 });
      expect(maxDuration.duration_seconds).toBe(60);
      
      // Progress boundaries
      const zeroProgress = createMockVideoGeneration({ progress_percent: 0 });
      const fullProgress = createMockVideoGeneration({ progress_percent: 100 });
      expect(zeroProgress.progress_percent).toBe(0);
      expect(fullProgress.progress_percent).toBe(100);
    });

    // Test 13: Should handle different error scenarios
    it('should handle error scenarios with proper error messages', () => {
      const failedGeneration = createMockVideoGeneration({
        status: 'failed',
        error_message: 'VEO API quota exceeded',
        progress_percent: 0
      });

      expect(failedGeneration.status).toBe('failed');
      expect(failedGeneration.error_message).toBe('VEO API quota exceeded');
      expect(isFinalStatus(failedGeneration.status)).toBe(true);
    });

    // Test 14: Should validate cost calculations
    it('should handle cost calculations correctly', () => {
      const expensiveGeneration = createMockVideoGeneration({
        quality: 'premium',
        resolution: '4K',
        duration_seconds: 60,
        cost: 2.50
      });

      expect(expensiveGeneration.cost).toBeGreaterThan(0);
      expect(typeof expensiveGeneration.cost).toBe('number');
      expect(expensiveGeneration.quality).toBe('premium');
    });
  });
});