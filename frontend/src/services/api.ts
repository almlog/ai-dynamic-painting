/**
 * API Client Service - Phase 1 Frontend-Backend Integration
 * バックエンドAPIとの通信を管理
 */

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

class ApiClient {
  private baseUrl: string;

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
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request Failed:', error);
      throw error;
    }
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
}

// APIクライアントインスタンスをエクスポート
export const apiClient = new ApiClient();

// TypeScript型変換ヘルパー関数
export const convertApiVideoToVideo = (apiVideo: ApiVideo) => {
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
    playback_status: apiVideo.status === 'active' ? 'available' : 'processing'
  };
};