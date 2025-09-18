/**
 * MOCKデータ - Phase 1 手動動画管理システム
 * フロントエンド開発・デザイン確認用のサンプルデータ
 */
import type { Video, SystemStatus, FilterOptions } from '../types';

// システム状態MOCK
export const mockSystemStatus: SystemStatus = {
  status: "healthy",
  timestamp: "2025-09-12T15:30:00Z",
  version: "1.0.0-phase1",
  uptime_seconds: 86400,
  database: {
    connected: true,
    tables_count: 5
  },
  storage: {
    videos_directory_exists: true,
    free_space_mb: 15680.5
  }
};

// 動画データMOCK
export const mockVideos: Video[] = [
  {
    id: "video-001",
    filename: "Morning_Forest_Sunrise.mp4",
    title: "Morning Forest",
    description: "Peaceful forest morning with golden sunlight",
    duration: 8.5,
    file_size: 95.2,
    uploaded_at: "2025-09-10T06:15:00Z",
    view_count: 12,
    user_rating: 4.8,
    tags: ["morning", "forest", "sunny", "peaceful"],
    thumbnail_url: "/thumbnails/morning_forest.jpg",
    is_manual_upload: true,
    prompt: null,
    playback_status: "available"
  },
  {
    id: "video-002", 
    filename: "Evening_Rain_City.mp4",
    title: "Evening Rain",
    description: "City evening with gentle rain and reflections",
    duration: 7.8,
    file_size: 102.3,
    uploaded_at: "2025-09-09T18:30:00Z",
    view_count: 8,
    user_rating: 4.2,
    tags: ["evening", "rain", "city", "moody"],
    thumbnail_url: "/thumbnails/evening_rain.jpg",
    is_manual_upload: false,
    prompt: "A peaceful evening city scene with gentle rain falling, creating beautiful reflections on wet streets",
    playback_status: "playing"
  },
  {
    id: "video-003",
    filename: "Night_Stars_Mountain.mp4", 
    title: "Night Stars",
    description: "Clear mountain night with brilliant stars",
    duration: 9.2,
    file_size: 87.6,
    uploaded_at: "2025-09-08T22:45:00Z",
    view_count: 15,
    user_rating: 5.0,
    tags: ["night", "stars", "mountain", "clear"],
    thumbnail_url: "/thumbnails/night_stars.jpg",
    is_manual_upload: false,
    prompt: "Spectacular night sky full of stars above a mountain silhouette",
    playback_status: "paused"
  },
  {
    id: "video-004",
    filename: "Rainy_Day_Garden.mp4",
    title: "Rainy Garden", 
    description: "Lush garden during a refreshing daytime rain",
    duration: 6.9,
    file_size: 73.4,
    uploaded_at: "2025-09-07T14:20:00Z",
    view_count: 3,
    user_rating: 3.7,
    tags: ["daytime", "rain", "garden", "fresh"],
    thumbnail_url: "/thumbnails/rainy_garden.jpg",
    is_manual_upload: true,
    prompt: null,
    playback_status: "available"
  },
  {
    id: "video-005",
    filename: "Winter_Snow_Forest.mp4",
    title: "Winter Snow",
    description: "Quiet snow-covered forest in winter",
    duration: 8.1,
    file_size: 91.8,
    uploaded_at: "2025-09-06T10:15:00Z", 
    view_count: 7,
    user_rating: 4.5,
    tags: ["morning", "snow", "forest", "winter"],
    thumbnail_url: "/thumbnails/winter_snow.jpg",
    is_manual_upload: false,
    prompt: "A serene winter forest scene with fresh snow covering the trees",
    playback_status: "available"
  },
  {
    id: "video-006",
    filename: "Sunset_Ocean_Waves.mp4",
    title: "Sunset Ocean",
    description: "Beautiful ocean sunset with gentle waves",
    duration: 7.5,
    file_size: 89.2,
    uploaded_at: "2025-09-05T19:30:00Z",
    view_count: 22,
    user_rating: 4.9,
    tags: ["evening", "sunset", "ocean", "waves"],
    thumbnail_url: "/thumbnails/sunset_ocean.jpg",
    is_manual_upload: true,
    prompt: null,
    playback_status: "available"
  }
];

// 現在再生中の動画情報
export const mockCurrentPlayback = {
  video_id: "video-002",
  playback_status: "playing",
  current_position: 3.2,
  start_time: "2025-09-12T15:25:00Z",
  loop_enabled: false,
  volume: 0.8,
  session_id: "session-12345"
};

// ユーザー設定MOCK
export const mockUserSettings = {
  display: {
    overlay_enabled: true,
    auto_brightness: true,
    brightness_level: 70,
    fullscreen_mode: true
  },
  generation: {
    auto_generation_enabled: true,
    daily_limit: 3,
    quality_level: "high", // high, medium, fast
    weekend_special: true
  },
  schedule: {
    morning_start: "06:00",
    morning_end: "10:00", 
    evening_start: "18:00",
    evening_end: "22:00"
  },
  api: {
    veo_api_key_set: true,
    weather_api_key_set: true,
    last_connection_test: "2025-09-12T12:00:00Z"
  }
};

// 使用統計MOCK
export const mockUsageStats = {
  monthly_limit: 90,
  monthly_used: 45,
  daily_limit: 3,
  daily_used: 1,
  total_videos: 156,
  total_uploaded: 89,
  total_generated: 67,
  storage_used_gb: 12.4,
  storage_total_gb: 64.0
};

// システムログMOCK
export const mockSystemLogs = [
  {
    timestamp: "2025-09-12T15:30:15Z",
    level: "INFO",
    component: "display",
    message: "Video playback started: Evening_Rain_City.mp4",
    session_id: "session-12345"
  },
  {
    timestamp: "2025-09-12T15:25:32Z", 
    level: "INFO",
    component: "m5stack",
    message: "Button pressed: NEXT_VIDEO",
    device_id: "m5stack-001"
  },
  {
    timestamp: "2025-09-12T15:20:45Z",
    level: "INFO",
    component: "api",
    message: "Video uploaded successfully: Winter_Snow_Forest.mp4",
    file_size: "91.8MB"
  },
  {
    timestamp: "2025-09-12T14:15:22Z",
    level: "WARN", 
    component: "storage",
    message: "Storage usage above 80%",
    current_usage: "51.2GB"
  },
  {
    timestamp: "2025-09-12T12:00:10Z",
    level: "INFO",
    component: "system",
    message: "Daily health check completed successfully",
    uptime: "24h 15m"
  }
];

// デバイス情報MOCK  
export const mockDeviceInfo = {
  m5stack: {
    status: "online",
    ip_address: "192.168.1.100",
    signal_strength: 85,
    battery_level: null, // USB powered
    temperature: 23.5,
    light_level: 65,
    last_seen: "2025-09-12T15:30:00Z"
  },
  raspberry_pi: {
    status: "healthy",
    cpu_usage: 15.2,
    memory_usage: 42.8,
    temperature: 45.2,
    disk_usage: 78.5,
    last_reboot: "2025-09-10T06:00:00Z"
  }
};

// フィルターオプション
export const mockFilterOptions: FilterOptions = {
  categories: ["All", "Generated", "Uploaded", "Favorites"],
  timeOfDay: ["morning", "daytime", "evening", "night"],
  weather: ["sunny", "cloudy", "rainy", "snowy"],
  tags: ["forest", "city", "ocean", "mountain", "garden", "peaceful", "moody", "fresh"]
};

// エラー状態MOCK（テスト用）
export const mockErrorStates = {
  api_error: {
    status: "unhealthy",
    message: "API server connection failed",
    timestamp: "2025-09-12T15:30:00Z"
  },
  upload_error: {
    status: "error",
    message: "File upload failed: unsupported format",
    file: "test_video.avi"
  },
  playback_error: {
    status: "error", 
    message: "Video playback interrupted",
    video_id: "video-002"
  }
};