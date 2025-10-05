/**
 * API Client Service - Phase 6: VEO API Integration
 * バックエンドAPIとの通信を管理（動画管理 + AI画像生成 + VEO動画生成）
 * 
 * @version v2.6.0
 * @author Claude (博士)
 * @created Phase 1 (動画管理)
 * @updated Phase 6 (VEO動画生成統合)
 */

import type {
  VideoGeneration,
  VideoGenerationRequest,
  VideoGenerationResponse,
  VideoStatusType
} from '../types/video';

import type { Video } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export interface ApiVideo {
  id: string;
  title: string;
  file_path: string;
  file_size: number;
  duration: number;
  format: string;
  resolution: string;
  upload_timestamp: string;
  status: string;
  play_count: number;
}

export interface ApiVideoListResponse {
  videos: ApiVideo[];
  total: number;
  page: number;
}

export interface ApiSystemStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime_seconds: number;
}

// ============================================================================
// TYPE DEFINITIONS - Organized by domain
// ============================================================================

// T6-010: Advanced Request Options
export interface RequestOptions {
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Maximum number of retry attempts */
  maxRetries?: number;
  /** Multiplier for exponential backoff (default: 2) */
  backoffMultiplier?: number;
  /** AbortController signal for request cancellation */
  signal?: AbortSignal;
  /** Priority level for request queue management */
  priority?: 'low' | 'normal' | 'high';
}

// Image Generation API Types (Legacy - T4B-001)
export type GenerationStatus = VideoStatusType; // Use unified status type
export type ImageQuality = 'standard' | 'hd';
export type AspectRatio = '1:1' | '16:9' | '9:16';
export type StylePreset = 'anime' | 'photographic' | 'digital-art';

export interface GenerationRequest {
  prompt_template_id: string;
  model: string;
  quality: ImageQuality;
  aspect_ratio: AspectRatio;
  negative_prompt?: string;
  style_preset?: StylePreset;
  seed?: number;
  temperature: number;
  top_k: number;
  top_p: number;
  max_tokens: number;
  variables: Record<string, string>;
}

export interface GenerationResponse {
  generation_id: string;
  status: GenerationStatus;
  message: string;
}

export interface GenerationResult {
  id: string;
  generation_id?: string;
  request: GenerationRequest;
  status: GenerationStatus;
  ai_instructions?: string;
  image_path?: string;
  metadata?: {
    model_version?: string;
    generation_time?: number;
    tokens_used?: number;
    [key: string]: unknown;
  };
  quality_score?: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

class ApiClient {
  private baseUrl: string;
  private maxConcurrentRequests: number = 5;
  private requestQueue: Array<{ request: () => Promise<any>, priority: 'low' | 'normal' | 'high', resolve: (value: any) => void, reject: (error: any) => void }> = [];
  private activeRequests: number = 0;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        // T6-010: Enhanced Error Response Handling
        const errorData = await this.parseErrorResponse(response);
        throw errorData;
      }

      return await response.json();
    } catch (error) {
      console.error('API Request Failed:', error);
      throw error;
    }
  }

  // ============================================================================
  // T6-010: Advanced Request Options with Timeout, Retry, and AbortController
  // ============================================================================

  /**
   * 高度なオプション付きリクエスト実行（タイムアウト・リトライ・キャンセル対応）
   * 
   * @private
   * @param endpoint - API エンドポイント
   * @param requestInit - fetch リクエスト設定
   * @param options - 高度なリクエストオプション
   * @returns レスポンスデータ
   */
  private async requestWithAdvancedOptions<T>(
    endpoint: string,
    requestInit: RequestInit = {},
    options?: RequestOptions
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // デフォルト設定
    const timeout = options?.timeout || 30000; // 30秒デフォルト
    const maxRetries = options?.maxRetries || 0;
    const backoffMultiplier = options?.backoffMultiplier || 2;
    const userSignal = options?.signal;

    // リトライ付きリクエスト実行
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // Create controller for this attempt
        const controller = new AbortController();
        
        // Handle user-provided AbortSignal
        if (userSignal && userSignal.aborted) {
          throw new Error('Request was aborted');
        }
        
        const abortHandler = () => controller.abort();
        userSignal?.addEventListener('abort', abortHandler);
        
        try {
          const result = await this.executeRequest<T>(url, requestInit, controller, timeout);
          userSignal?.removeEventListener('abort', abortHandler);
          return result;
        } catch (error: any) {
          userSignal?.removeEventListener('abort', abortHandler);
          
          // Check if error was due to user abort
          if (userSignal?.aborted) {
            throw new Error('Request was aborted');
          }
          
          throw error;
        }

      } catch (error: any) {
        // 最後の試行または中止された場合は即座にエラーを投げる
        if (attempt === maxRetries || userSignal?.aborted) {
          throw error;
        }

        // ネットワークエラーの場合のみリトライ
        if (this.shouldRetry(error)) {
          const delay = this.calculateBackoffDelay(attempt, backoffMultiplier);
          await this.sleep(delay);
          continue;
        } else {
          throw error;
        }
      }
    }

    // Should never reach here
    throw new Error('Unexpected error in retry logic');
  }

  /**
   * 実際のHTTPリクエストを実行
   * 
   * @private
   */
  private async executeRequest<T>(
    url: string,
    requestInit: RequestInit,
    controller: AbortController,
    timeout: number
  ): Promise<T> {
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...requestInit.headers,
      },
      ...requestInit,
      signal: controller.signal,
    };

    // タイムアウト設定
    const timeoutId = setTimeout(() => {
      if (!controller.signal.aborted) {
        controller.abort();
      }
    }, timeout);

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorData = await this.parseErrorResponse(response);
        throw errorData;
      }

      return await response.json();
    } catch (error: any) {
      clearTimeout(timeoutId);
      
      // AbortError handling
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeout}ms`);
      }
      
      console.error('API Request Failed:', error);
      throw error;
    }
  }

  /**
   * エラーがリトライ可能かどうかを判定
   * 
   * @private
   */
  private shouldRetry(error: any): boolean {
    // ネットワークエラーやタイムアウトはリトライ対象
    return error.name === 'TypeError' || 
           error.message?.includes('Network error') ||
           error.message?.includes('timeout') ||
           error.status >= 500;
  }

  /**
   * 指数バックオフ遅延時間を計算
   * 
   * @private
   */
  private calculateBackoffDelay(attempt: number, multiplier: number): number {
    const baseDelay = 1000; // 1秒ベース
    return baseDelay * Math.pow(multiplier, attempt);
  }

  /**
   * 指定した時間だけ待機
   * 
   * @private
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 動画関連API
  async getVideos(): Promise<ApiVideoListResponse> {
    return this.request<ApiVideoListResponse>('/api/videos');
  }

  async uploadVideo(file: File, title?: string): Promise<ApiVideo> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) {
      formData.append('title', title);
    }

    const response = await fetch(`${this.baseUrl}/api/videos`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  async deleteVideo(videoId: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(`/api/videos/${videoId}`, {
      method: 'DELETE',
    });
  }

  // システム状態API
  async getSystemStatus(): Promise<ApiSystemStatus> {
    return this.request<ApiSystemStatus>('/api/system/health');
  }

  // ディスプレイ制御API
  async playVideo(videoId: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>('/api/display/play', {
      method: 'POST',
      body: JSON.stringify({ video_id: videoId }),
    });
  }

  async stopVideo(): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>('/api/display/stop', {
      method: 'POST',
    });
  }

  // M5STACK制御API
  async getM5StackStatus(): Promise<any> {
    return this.request('/api/m5stack/status');
  }

  async sendM5StackControl(action: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>('/api/m5stack/control', {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
  }

  // ヘルスチェック
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/videos`);
      return response.ok;
    } catch {
      return false;
    }
  }

  // ============================================================================
  // LEGACY API - AI画像生成 (T4B-001 Legacy Support)
  // ============================================================================
  
  /**
   * AI画像生成リクエストを送信し、バックグラウンドで生成を開始します。
   * 
   * @param request - 画像生成リクエストパラメータ
   * @returns 生成IDと初期ステータスを含むレスポンス
   * @throws {Error} APIエラー、パラメータ不正、ネットワークエラー
   * 
   * @example
   * ```typescript
   * const response = await apiClient.generateImage({
   *   prompt_template_id: 'template-001',
   *   quality: 'hd',
   *   aspect_ratio: '16:9',
   *   style_preset: 'anime',
   *   seed: 12345
   * });
   * console.log('Generation ID:', response.generation_id);
   * ```
   */
  async generateImage(request: GenerationRequest): Promise<GenerationResponse> {
    const requestWithDefaults = this.buildGenerationRequest(request);
    return this.request<GenerationResponse>('/api/admin/generate', {
      method: 'POST',
      body: JSON.stringify(requestWithDefaults),
    });
  }

  // ============================================================================
  // VEO API - 動画生成 (T6-007 Complete Implementation)
  // ============================================================================
  
  /**
   * VEO API動画生成リクエストを送信し、バックグラウンドで生成を開始します。
   * 
   * @param request - 動画生成リクエストパラメータ
   * @param options - リクエストオプション (timeout, retry, signal等)
   * @returns タスクIDと初期ステータスを含むレスポンス
   * @throws {Error} APIエラー、パラメータ不正、ネットワークエラー
   * 
   * @example
   * ```typescript
   * const response = await apiClient.generateVideo({
   *   prompt: 'A dancing robot in space',
   *   duration_seconds: 30,
   *   resolution: '1080p',
   *   fps: 30,
   *   quality: 'standard'
   * }, { timeout: 10000, maxRetries: 3 });
   * console.log('Task ID:', response.task_id);
   * ```
   */
  async generateVideo(request: VideoGenerationRequest, options?: RequestOptions): Promise<VideoGenerationResponse> {
    // T6-010: Client-side parameter validation
    this.validateVideoGenerationRequest(request);
    
    const requestWithDefaults = this.buildVideoGenerationRequest(request);
    const priority = options?.priority || 'normal';
    
    // T6-010: Request queue management
    return new Promise((resolve, reject) => {
      const queuedRequest = {
        request: () => this.requestWithAdvancedOptions<VideoGenerationResponse>('/api/ai/generate', {
          method: 'POST',
          body: JSON.stringify(requestWithDefaults),
        }, options),
        priority,
        resolve,
        reject
      };
      
      this.addToQueue(queuedRequest);
      this.processQueue();
    });
  }

  /**
   * T6-010: Add request to queue with priority handling
   */
  private addToQueue(queuedRequest: { request: () => Promise<any>, priority: 'low' | 'normal' | 'high', resolve: (value: any) => void, reject: (error: any) => void }): void {
    // Insert based on priority: high -> normal -> low
    const priorityOrder: Record<'high' | 'normal' | 'low', number> = { 'high': 0, 'normal': 1, 'low': 2 };
    let insertIndex = this.requestQueue.length;
    
    for (let i = 0; i < this.requestQueue.length; i++) {
      const currentPriority = this.requestQueue[i]?.priority;
      if (currentPriority && priorityOrder[queuedRequest.priority] < priorityOrder[currentPriority]) {
        insertIndex = i;
        break;
      }
    }
    
    this.requestQueue.splice(insertIndex, 0, queuedRequest);
  }

  /**
   * T6-010: Process queued requests respecting concurrency limits
   */
  private async processQueue(): Promise<void> {
    if (this.activeRequests >= this.maxConcurrentRequests || this.requestQueue.length === 0) {
      return;
    }
    
    const queuedRequest = this.requestQueue.shift();
    if (!queuedRequest) return;
    
    this.activeRequests++;
    
    try {
      const result = await queuedRequest.request();
      queuedRequest.resolve(result);
    } catch (error) {
      queuedRequest.reject(error);
    } finally {
      this.activeRequests--;
      // Process next request in queue
      this.processQueue();
    }
  }

  /**
   * 指定したタスクIDの動画生成ステータスと結果を取得します。
   * 
   * @param taskId - タスクID（generateVideoから返されたID）
   * @returns 動画生成結果の詳細情報
   * @throws {Error} タスクIDが見つからない場合、その他APIエラー
   * 
   * @example
   * ```typescript
   * const result = await apiClient.getVideoStatus('task-123');
   * if (result.status === 'completed') {
   *   console.log('Video URL:', result.video_url);
   * }
   * ```
   */
  async getVideoStatus(taskId: string): Promise<VideoGeneration> {
    this.validateTaskId(taskId, 'getVideoStatus');
    return this.request<VideoGeneration>(`/api/ai/generation/${taskId}`);
  }

  /**
   * 過去の動画生成履歴を新しい順に取得します。
   * 
   * @param limit - 取得する最大件数（デフォルト: 50件）
   * @returns 動画生成結果の配列（新しい順）
   * @throws {Error} APIエラー、ネットワークエラー
   * 
   * @example
   * ```typescript
   * const history = await apiClient.getVideoGenerationHistory(20);
   * const completedVideos = history.filter(v => v.status === 'completed');
   * ```
   */
  async getVideoGenerationHistory(limit: number = 50): Promise<VideoGeneration[]> {
    this.validateLimit(limit, 'getVideoGenerationHistory');
    return this.request<VideoGeneration[]>(`/api/ai/generations?limit=${limit}`);
  }

  /**
   * 指定したタスクIDの動画生成をキャンセルします。
   * 
   * @param taskId - キャンセルするタスクID
   * @returns キャンセル結果
   * @throws {Error} タスクIDが見つからない場合、その他APIエラー
   * 
   * @example
   * ```typescript
   * const result = await apiClient.cancelVideoGeneration('task-123');
   * if (result.success) {
   *   console.log('Cancellation successful:', result.message);
   * }
   * ```
   */
  async cancelVideoGeneration(taskId: string): Promise<{ success: boolean; message: string }> {
    this.validateTaskId(taskId, 'cancelVideoGeneration');
    return this.request<{ success: boolean; message: string }>(`/api/ai/generation/${taskId}`, {
      method: 'DELETE',
    });
  }

  /**
   * T6-010: Poll video generation status with optional callbacks
   * @param taskId Task ID to poll
   * @param options Polling options including intervals and callbacks
   * @returns Final video generation result
   */
  async pollVideoStatus(
    taskId: string,
    options?: {
      interval?: number;
      maxInterval?: number;
      initialInterval?: number;
      accelerationThreshold?: number;
      adaptiveIntervals?: boolean;
      onProgress?: (status: any) => void;
      onStatusChange?: (status: any) => void;
    }
  ): Promise<any> {
    const {
      maxInterval = 5000,
      initialInterval = 2000,
      accelerationThreshold = 80,
      adaptiveIntervals = false,
      onProgress,
      onStatusChange,
    } = options || {};

    let currentInterval = initialInterval;
    let lastStatus: string | null = null;

    const poll = async (): Promise<any> => {
      const response = await fetch(`${this.baseUrl}/api/videos/status/${taskId}`);
      const data = await response.json();

      // Call progress callback if provided
      if (onProgress) {
        onProgress(data);
      }

      // Call status change callback if status changed
      if (onStatusChange && data.status !== lastStatus) {
        onStatusChange(data);
        lastStatus = data.status;
      }

      // Check if polling should continue
      if (data.status === 'completed' || data.status === 'failed') {
        return data;
      }

      // Adaptive interval calculation
      if (adaptiveIntervals && data.progress_percent !== undefined) {
        if (data.progress_percent > accelerationThreshold) {
          currentInterval = 1000; // Speed up near completion
        } else if (data.progress_percent > 50) {
          currentInterval = Math.min(maxInterval, currentInterval * 1.5);
        }
      }

      // Wait and poll again
      await new Promise(resolve => setTimeout(resolve, currentInterval));
      return poll();
    };

    return poll();
  }

  /**
   * T6-010: Configure API client settings
   * @param config Configuration options
   */
  configure(config: { maxConcurrentRequests?: number }): void {
    // Store configuration for request queue management
    if (config.maxConcurrentRequests !== undefined) {
      this.maxConcurrentRequests = config.maxConcurrentRequests;
    }
  }

  /**
   * 指定した生成IDの現在のステータスと結果を取得します。
   * 
   * @param generationId - 生成ID（generateImageから返されたID）
   * @returns 生成結果の詳細情報
   * @throws {Error} 生成IDが見つからない場合、その他APIエラー
   * 
   * @example
   * ```typescript
   * const result = await apiClient.getGenerationStatus('gen-123');
   * if (result.status === 'completed') {
   *   console.log('Image path:', result.image_path);
   * }
   * ```
   */
  async getGenerationStatus(generationId: string): Promise<GenerationResult> {
    this.validateGenerationId(generationId, 'getGenerationStatus');
    return this.request<GenerationResult>(`/api/admin/generate/status/${generationId}`);
  }

  /**
   * 過去の画像生成履歴を新しい順に取得します。
   * 
   * @param limit - 取得する最大件数（デフォルト: 50件）
   * @returns 生成結果の配列（新しい順）
   * @throws {Error} APIエラー、ネットワークエラー
   * 
   * @example
   * ```typescript
   * const history = await apiClient.getGenerationHistory(20);
   * const completedImages = history.filter(r => r.status === 'completed');
   * ```
   */
  async getGenerationHistory(limit: number = 50): Promise<GenerationResult[]> {
    this.validateLimit(limit, 'getGenerationHistory');
    return this.request<GenerationResult[]>(`/api/admin/generate/history?limit=${limit}`);
  }
  
  /**
   * GenerationRequestにデフォルト値を適用して結果を返します。
   * 
   * @private
   * @param request - 部分的なリクエストパラメータ
   * @returns デフォルト値が適用された完全なリクエスト
   */
  private buildGenerationRequest(request: GenerationRequest): GenerationRequest {
    const result: GenerationRequest = {
      model: request.model || 'gemini-1.5-flash',
      quality: request.quality || 'standard',
      aspect_ratio: request.aspect_ratio || '1:1',
      temperature: request.temperature || 0.7,
      top_k: request.top_k || 40,
      top_p: request.top_p || 0.95,
      max_tokens: request.max_tokens || 2048,
      variables: request.variables || {},
      prompt_template_id: request.prompt_template_id
    };
    
    // オプショナルプロパティは値が存在する場合のみ追加
    if (request.negative_prompt !== undefined) {
      result.negative_prompt = request.negative_prompt;
    }
    if (request.seed !== undefined) {
      result.seed = request.seed;
    }
    if (request.style_preset !== undefined) {
      result.style_preset = request.style_preset;
    }
    
    return result;
  }

  /**
   * VideoGenerationRequestにデフォルト値を適用して結果を返します。
   * 
   * @private
   * @param request - 部分的なリクエストパラメータ
   * @returns デフォルト値が適用された完全なリクエスト
   */
  private buildVideoGenerationRequest(request: VideoGenerationRequest): VideoGenerationRequest {
    return {
      prompt: request.prompt, // promptは必須のためデフォルト値なし
      duration_seconds: request.duration_seconds || 30,
      resolution: request.resolution || '1080p',
      fps: request.fps || 30,
      quality: request.quality || 'standard'
    };
  }

  // ============================================================================
  // VALIDATION HELPERS - T6-007-R01: Unified validation methods
  // ============================================================================

  /**
   * タスクIDのバリデーションを行います。
   * 
   * @private
   * @param taskId - 検証するタスクID
   * @param methodName - 呼び出し元メソッド名（エラーメッセージ用）
   * @throws {Error} タスクIDが無効な場合
   */
  private validateTaskId(taskId: string, methodName: string): void {
    if (!taskId?.trim()) {
      throw new Error(`${methodName}: Task ID is required and cannot be empty`);
    }
  }

  /**
   * 生成IDのバリデーションを行います。
   * 
   * @private
   * @param generationId - 検証する生成ID
   * @param methodName - 呼び出し元メソッド名（エラーメッセージ用）
   * @throws {Error} 生成IDが無効な場合
   */
  private validateGenerationId(generationId: string, methodName: string): void {
    if (!generationId?.trim()) {
      throw new Error(`${methodName}: Generation ID is required and cannot be empty`);
    }
  }

  /**
   * limit値のバリデーションを行います。
   * 
   * @private
   * @param limit - 検証するlimit値
   * @param methodName - 呼び出し元メソッド名（エラーメッセージ用）
   * @throws {Error} limit値が無効な場合
   */
  private validateLimit(limit: number, methodName: string): void {
    if (limit < 1 || limit > 200) {
      throw new Error(`${methodName}: Limit must be between 1 and 200, got ${limit}`);
    }
  }

  // ============================================================================
  // T6-010: Enhanced Error Response Handling
  // ============================================================================

  /**
   * レスポンスエラーを構造化されたエラーオブジェクトに解析
   * 
   * @private
   * @param response - エラーレスポンス
   * @returns 構造化されたエラーオブジェクト
   */
  private async parseErrorResponse(response: Response): Promise<any> {
    const status = response.status;
    const statusText = response.statusText;
    
    try {
      const errorData = await response.json();
      
      // 422 Validation Error
      if (status === 422) {
        const error = new Error(`API Error: ${status} ${statusText}`) as any;
        error.status = status;
        error.type = 'validation_error';
        error.fields = errorData.details || [];
        return error;
      }
      
      // 429 Rate Limit Error
      if (status === 429) {
        const retryAfter = response.headers.get('retry-after');
        const rateLimit = response.headers.get('x-ratelimit-limit');
        const rateLimitRemaining = response.headers.get('x-ratelimit-remaining');
        const rateLimitReset = response.headers.get('x-ratelimit-reset');
        
        const error = new Error(`API Error: ${status} ${statusText}`) as any;
        error.status = status;
        error.type = 'rate_limit_error';
        error.retryAfter = retryAfter ? parseInt(retryAfter, 10) : null;
        error.limitInfo = {
          limit: rateLimit ? parseInt(rateLimit, 10) : null,
          remaining: rateLimitRemaining ? parseInt(rateLimitRemaining, 10) : null,
          resetTime: rateLimitReset || null
        };
        return error;
      }
      
      // 500 Server Error
      if (status >= 500) {
        const error = new Error(`API Error: ${status} ${statusText}`) as any;
        error.status = status;
        error.type = 'server_error';
        error.errorCode = errorData.error_code || 'UNKNOWN_SERVER_ERROR';
        error.suggestedAction = errorData.suggested_action || 'Please try again later';
        error.supportReference = errorData.support_reference || null;
        return error;
      }
      
      // Default error format
      return new Error(`API Error: ${status} ${statusText}`);
    } catch (parseError) {
      // If JSON parsing fails, return basic error
      return new Error(`API Error: ${status} ${statusText}`);
    }
  }

  // ============================================================================
  // T6-010: Client-side Parameter Validation
  // ============================================================================

  /**
   * VideoGenerationRequestのクライアントサイドバリデーション
   * 
   * @private
   * @param request - 検証するリクエスト
   * @throws {Error} パラメータが無効な場合
   */
  private validateVideoGenerationRequest(request: VideoGenerationRequest): void {
    // Prompt length validation
    if (!request.prompt || request.prompt.trim().length === 0) {
      throw new Error('Prompt is required and cannot be empty');
    }
    if (request.prompt.length > 5000) {
      throw new Error('Prompt must be less than 5000 characters');
    }

    // Duration range validation
    if (request.duration_seconds < 1 || request.duration_seconds > 300) {
      throw new Error(`Duration must be between 1 and 300 seconds, got ${request.duration_seconds}`);
    }

    // Resolution enum validation
    const validResolutions = ['720p', '1080p', '4K'];
    if (!validResolutions.includes(request.resolution)) {
      throw new Error(`Invalid resolution: ${request.resolution}. Allowed: ${validResolutions.join(', ')}`);
    }

    // FPS validation
    const validFps = [24, 30, 60];
    if (!validFps.includes(request.fps)) {
      throw new Error(`Invalid fps: ${request.fps}. Allowed: ${validFps.join(', ')}`);
    }

    // Quality validation
    const validQualities = ['draft', 'standard', 'premium'];
    if (!validQualities.includes(request.quality)) {
      throw new Error(`Invalid quality: ${request.quality}. Allowed: ${validQualities.join(', ')}`);
    }
  }
}

// APIクライアントインスタンスをエクスポート
export const apiClient = new ApiClient();

// ======= TypeScript型変換ヘルパー関数 =======

// ============================================================================
// TYPE CONVERSION HELPERS - Legacy video management
// ============================================================================

/**
 * 動画管理用：バックエンドAPIVideo型をフロントエンドVideo型に変換
 */
export const convertApiVideoToVideo = (apiVideo: ApiVideo): Video => {
  return {
    id: apiVideo.id,
    filename: apiVideo.file_path.split('/').pop() || apiVideo.title,
    title: apiVideo.title,
    description: `Uploaded: ${new Date(apiVideo.upload_timestamp).toLocaleDateString('ja-JP')}`,
    duration: apiVideo.duration,
    file_size: apiVideo.file_size / 1024 / 1024, // Convert to MB
    uploaded_at: apiVideo.upload_timestamp,
    view_count: apiVideo.play_count,
    user_rating: 0, // TODO: Add rating system in Phase 2
    tags: [], // TODO: Add tagging system in Phase 2
    thumbnail_url: '/thumbnails/default.jpg', // TODO: Generate thumbnails in Phase 2
    is_manual_upload: true,
    prompt: null,
    playback_status: apiVideo.status === 'active' ? 'available' as const : 'error' as const
  };
};

/**
 * AI画像生成用：GenerationRequestのデフォルト値を持つビルダー関数
 */
export const createGenerationRequest = (
  promptTemplateId: string, 
  overrides: Partial<GenerationRequest> = {}
): GenerationRequest => {
  return {
    prompt_template_id: promptTemplateId,
    model: 'gemini-1.5-flash',
    quality: 'standard',
    aspect_ratio: '1:1', 
    temperature: 0.7,
    top_k: 40,
    top_p: 0.95,
    max_tokens: 2048,
    variables: {},
    ...overrides
  };
};

/**
 * AI画像生成用：GenerationStatus判定ヘルパー
 */
export const isGenerationComplete = (status: GenerationStatus): boolean => {
  return status === 'completed';
};

export const isGenerationFailed = (status: GenerationStatus): boolean => {
  return status === 'failed';
};

export const isGenerationInProgress = (status: GenerationStatus): boolean => {
  return status === 'pending' || status === 'processing';
};

// ============================================================================
// HELPER FUNCTIONS - Organized by API domain
// ============================================================================

/**
 * VEO動画生成用：VideoGenerationRequestビルダー関数
 */
export const createVideoGenerationRequest = (
  prompt: string,
  overrides: Partial<VideoGenerationRequest> = {}
): VideoGenerationRequest => {
  return {
    prompt,
    duration_seconds: 30,
    resolution: '1080p',
    fps: 30,
    quality: 'standard',
    ...overrides
  };
};

/**
 * VEO動画生成用：VideoGeneration型判定ヘルパー関数群
 */
export const isVideoGenerationComplete = (generation: VideoGeneration): boolean => {
  return generation.status === 'completed' && !!generation.video_url;
};

export const isVideoGenerationFailed = (generation: VideoGeneration): boolean => {
  return generation.status === 'failed';
};

export const isVideoGenerationInProgress = (generation: VideoGeneration): boolean => {
  return generation.status === 'pending' || generation.status === 'processing';
};

export const getVideoGenerationProgress = (generation: VideoGeneration): number => {
  return Math.max(0, Math.min(100, generation.progress_percent || 0));
};