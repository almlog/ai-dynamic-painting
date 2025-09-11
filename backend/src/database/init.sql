-- AI Dynamic Painting System - Phase 1 Database Schema
-- Created: 2025-09-11

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    file_path TEXT UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    duration REAL NOT NULL,
    format TEXT NOT NULL DEFAULT 'mp4',
    resolution TEXT,
    thumbnail_path TEXT,
    upload_timestamp DATETIME NOT NULL,
    last_played DATETIME,
    play_count INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'processing',
    CHECK (file_size <= 524288000),
    CHECK (status IN ('active', 'archived', 'processing', 'error'))
);

-- Display Sessions table  
CREATE TABLE IF NOT EXISTS display_sessions (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    session_type TEXT NOT NULL DEFAULT 'manual',
    current_position REAL DEFAULT 0.0,
    playback_status TEXT NOT NULL DEFAULT 'stopped',
    display_mode TEXT NOT NULL DEFAULT 'fullscreen',
    loop_enabled BOOLEAN DEFAULT FALSE,
    created_by TEXT NOT NULL,
    FOREIGN KEY (video_id) REFERENCES videos(id),
    CHECK (session_type IN ('manual', 'scheduled', 'loop')),
    CHECK (playback_status IN ('playing', 'paused', 'stopped', 'loading')),
    CHECK (display_mode IN ('fullscreen', 'windowed'))
);

-- User Devices table
CREATE TABLE IF NOT EXISTS user_devices (
    id TEXT PRIMARY KEY,
    device_type TEXT NOT NULL,
    device_name TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    last_seen DATETIME NOT NULL,
    session_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    CHECK (device_type IN ('web_browser', 'm5stack'))
);

-- System Status table (for monitoring)
CREATE TABLE IF NOT EXISTS system_status (
    id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    cpu_usage REAL,
    memory_usage REAL, 
    disk_usage REAL,
    uptime INTEGER,
    active_sessions INTEGER DEFAULT 0,
    total_videos INTEGER DEFAULT 0,
    m5stack_status TEXT DEFAULT 'offline',
    display_status TEXT DEFAULT 'idle',
    api_status TEXT DEFAULT 'healthy',
    CHECK (cpu_usage >= 0 AND cpu_usage <= 100),
    CHECK (memory_usage >= 0 AND memory_usage <= 100),
    CHECK (disk_usage >= 0 AND disk_usage <= 100)
);

-- Control Events table (for logging)
CREATE TABLE IF NOT EXISTS control_events (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    device_id TEXT,
    event_type TEXT NOT NULL,
    event_data JSON,
    timestamp DATETIME NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    FOREIGN KEY (session_id) REFERENCES display_sessions(id),
    FOREIGN KEY (device_id) REFERENCES user_devices(id),
    CHECK (event_type IN ('play', 'pause', 'stop', 'next', 'previous', 'volume', 'upload'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_upload_time ON videos(upload_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_video_id ON display_sessions(video_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON display_sessions(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON control_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_session_id ON control_events(session_id);

-- Insert initial system status record
INSERT OR IGNORE INTO system_status (
    id, 
    timestamp, 
    uptime, 
    active_sessions, 
    total_videos,
    api_status
) VALUES (
    'initial_status',
    datetime('now'),
    0,
    0,
    0,
    'healthy'
);