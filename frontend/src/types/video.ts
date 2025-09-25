/**
 * Video Generation Types - Phase 6 VEO API Integration
 * T6-006-R01: REFACTOR phase - Enhanced type definitions with improved type safety
 * 
 * This module provides comprehensive TypeScript types for VEO API video generation,
 * ensuring type safety across the frontend application.
 */

// ============================================================================
// ENUMS & UNION TYPES
// ============================================================================

/**
 * Video generation status enum
 * Represents all possible states in the video generation lifecycle
 */
export enum VideoStatus {
  /** Initial state when generation is queued but not started */
  PENDING = 'pending',
  /** Generation is actively being processed by VEO API */
  PROCESSING = 'processing', 
  /** Generation completed successfully with video available */
  COMPLETED = 'completed',
  /** Generation failed due to error or timeout */
  FAILED = 'failed'
}

/**
 * Video quality levels available for generation
 * Each level affects both cost and processing time
 */
export type VideoQuality = 'draft' | 'standard' | 'premium';

/**
 * Supported video resolutions for VEO API
 */
export type VideoResolution = '720p' | '1080p' | '4K';

/**
 * Supported frame rates for video generation
 */
export type VideoFPS = 24 | 30 | 60;

/**
 * Status type union that matches VideoStatus enum values
 * Used where enum cannot be directly imported
 */
export type VideoStatusType = 'pending' | 'processing' | 'completed' | 'failed';

// ============================================================================
// CORE INTERFACES
// ============================================================================

/**
 * Main video generation entity
 * Represents a complete video generation record from database
 */
export interface VideoGeneration {
  /** Unique identifier for the video generation */
  id: string;
  
  /** VEO API task identifier for tracking generation progress */
  task_id: string;
  
  /** Text prompt used to generate the video */
  prompt: string;
  
  /** Current status of the generation process */
  status: VideoStatusType;
  
  /** Video duration in seconds (5-60 range) */
  duration_seconds: number;
  
  /** Video resolution (720p, 1080p, 4K) */
  resolution: VideoResolution;
  
  /** Frames per second (24, 30, 60) */
  fps: VideoFPS;
  
  /** Quality level affecting cost and processing time */
  quality: VideoQuality;
  
  /** URL to generated video file (available only when status is 'completed') */
  video_url?: string;
  
  /** Cost of generation in USD */
  cost: number;
  
  /** ISO timestamp when generation was requested */
  created_at: string;
  
  /** ISO timestamp when record was last updated */
  updated_at: string;
  
  /** Generation progress percentage (0-100) */
  progress_percent: number;
  
  /** Error message if generation failed, null otherwise */
  error_message: string | null;
}

// ============================================================================
// API INTERFACES
// ============================================================================

/**
 * Request payload for creating a new video generation
 * Sent to backend API to initiate VEO generation
 */
export interface VideoGenerationRequest {
  /** Text prompt describing the desired video content */
  prompt: string;
  
  /** Desired video duration in seconds */
  duration_seconds: number;
  
  /** Target video resolution */
  resolution: VideoResolution;
  
  /** Target frame rate */
  fps: VideoFPS;
  
  /** Quality level for generation */
  quality: VideoQuality;
}

/**
 * Response from backend when creating video generation
 * Contains initial status and tracking information
 */
export interface VideoGenerationResponse {
  /** VEO API task ID for tracking progress */
  task_id: string;
  
  /** Initial status of the generation request */
  status: VideoStatusType;
  
  /** Human-readable message about the request */
  message: string;
  
  /** Estimated completion time (ISO timestamp) */
  estimated_completion_time?: string;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Type guard to check if a status is processing-related
 */
export const isProcessingStatus = (status: VideoStatusType): status is 'pending' | 'processing' => {
  return status === 'pending' || status === 'processing';
};

/**
 * Type guard to check if a status is final (completed or failed)
 */
export const isFinalStatus = (status: VideoStatusType): status is 'completed' | 'failed' => {
  return status === 'completed' || status === 'failed';
};

/**
 * Partial video generation for updates
 * Used when updating existing generation records
 */
export type VideoGenerationUpdate = Partial<Pick<VideoGeneration, 
  'status' | 'progress_percent' | 'video_url' | 'error_message' | 'updated_at'
>>;

// ============================================================================
// EXPORTS
// ============================================================================

// Re-export everything for convenient importing
export type {
  VideoGeneration as VG,
  VideoGenerationRequest as VGRequest,
  VideoGenerationResponse as VGResponse,
};