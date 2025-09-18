/**
 * TypeScript型定義 - Phase 1 手動動画管理システム
 */

// 動画データ型
export interface Video {
  id: string;
  filename: string;
  title: string;
  description: string;
  duration: number;
  file_size: number;
  uploaded_at: string;
  view_count: number;
  user_rating: number;
  tags: string[];
  thumbnail_url: string;
  is_manual_upload: boolean;
  prompt: string | null;
  playback_status: 'available' | 'playing' | 'paused' | 'error';
}

// システム状態型
export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime_seconds: number;
  database: {
    connected: boolean;
    tables_count: number;
  };
  storage: {
    videos_directory_exists: boolean;
    free_space_mb: number;
  };
}

// 再生状態型
export interface PlaybackStatus {
  video_id: string | null;
  playback_status: 'idle' | 'playing' | 'paused' | 'stopped';
  current_position?: number;
  start_time?: string;
  loop_enabled?: boolean;
  volume?: number;
  session_id?: string;
}

// ユーザー設定型
export interface UserSettings {
  display: {
    overlay_enabled: boolean;
    auto_brightness: boolean;
    brightness_level: number;
    fullscreen_mode: boolean;
  };
  generation: {
    auto_generation_enabled: boolean;
    daily_limit: number;
    quality_level: 'high' | 'medium' | 'fast';
    weekend_special: boolean;
  };
  schedule: {
    morning_start: string;
    morning_end: string;
    evening_start: string;
    evening_end: string;
  };
  api: {
    veo_api_key_set: boolean;
    weather_api_key_set: boolean;
    last_connection_test: string;
  };
}

// 使用統計型
export interface UsageStats {
  monthly_limit: number;
  monthly_used: number;
  daily_limit: number;
  daily_used: number;
  total_videos: number;
  total_uploaded: number;
  total_generated: number;
  storage_used_gb: number;
  storage_total_gb: number;
}

// システムログ型
export interface SystemLog {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  component: string;
  message: string;
  session_id?: string;
  device_id?: string;
  file_size?: string;
  current_usage?: string;
  uptime?: string;
}

// デバイス情報型
export interface DeviceInfo {
  m5stack: {
    status: 'online' | 'offline' | 'error';
    ip_address: string;
    signal_strength: number;
    battery_level: number | null;
    temperature: number;
    light_level: number;
    last_seen: string;
  };
  raspberry_pi: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    cpu_usage: number;
    memory_usage: number;
    temperature: number;
    disk_usage: number;
    last_reboot: string;
  };
}

// フィルターオプション型
export interface FilterOptions {
  categories: string[];
  timeOfDay: string[];
  weather: string[];
  tags: string[];
}

// API Response型
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// コンポーネントProps型
export interface DashboardProps {
  systemStatus: SystemStatus;
  currentVideo: Video | null;
  usageStats: UsageStats;
  recentVideos: Video[];
}

export interface VideoListProps {
  videos: Video[];
  filterOptions: FilterOptions;
  onVideoSelect: (video: Video) => void;
  onVideoUpload: () => void;
  onVideoDelete: (videoId: string) => void;
}

export interface VideoUploadProps {
  onUploadComplete: (video: Video) => void;
  onUploadError: (error: string) => void;
  maxFileSize: number;
  acceptedFormats: string[];
}

export interface SettingsProps {
  settings: UserSettings;
  onSettingsChange: (settings: UserSettings) => void;
  onApiTest: (service: 'veo' | 'weather') => Promise<boolean>;
}