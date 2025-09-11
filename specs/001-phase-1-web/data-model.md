# Data Model: Phase 1 手動動画管理システム

**Date**: 2025-09-11  
**Phase**: 1 - Entity Design & Data Model

## Core Entities

### Video
動画ファイルのメタデータと状態管理

**Fields**:
- `id`: string (UUID) - Primary key
- `title`: string - 表示用タイトル  
- `file_path`: string - ファイルシステム上のパス
- `file_size`: integer - ファイルサイズ（バイト）
- `duration`: float - 再生時間（秒）
- `format`: string - ファイル形式（mp4）
- `resolution`: string - 解像度（"1920x1080"）
- `thumbnail_path`: string - サムネイル画像パス
- `upload_timestamp`: datetime - アップロード日時
- `last_played`: datetime - 最終再生日時
- `play_count`: integer - 再生回数
- `status`: enum - active, archived, processing, error

**Relationships**:
- One-to-Many with DisplaySession (動画は複数セッションで使用可能)

**Validation Rules**:
- file_size <= 500MB (524,288,000 bytes)
- format in ["mp4"]
- title length <= 100 characters
- file_path must be unique

**State Transitions**:
```
[新規] → processing → active
active → archived (user action)
active → error (playback failure)
error → active (after fix)
```

### DisplaySession
動画表示セッションの管理

**Fields**:
- `id`: string (UUID) - Primary key
- `video_id`: string - 表示中の動画ID（FK）
- `start_time`: datetime - セッション開始時刻
- `end_time`: datetime - セッション終了時刻（nullable）
- `session_type`: enum - manual, scheduled, loop
- `current_position`: float - 再生位置（秒）
- `playback_status`: enum - playing, paused, stopped, loading
- `display_mode`: enum - fullscreen, windowed
- `loop_enabled`: boolean - ループ再生フラグ
- `created_by`: string - セッション作成者（"web", "m5stack"）

**Relationships**:
- Many-to-One with Video
- One-to-Many with ControlEvent

**Validation Rules**:
- start_time <= end_time (if end_time exists)
- current_position <= video.duration
- active session per display = 1

### UserDevice
アクセスデバイスの管理

**Fields**:
- `id`: string (UUID) - Primary key  
- `device_type`: enum - web_browser, m5stack
- `device_name`: string - デバイス名
- `ip_address`: string - IPアドレス
- `user_agent`: string - ブラウザ/デバイス情報
- `last_seen`: datetime - 最終アクセス時刻
- `session_count`: integer - セッション数
- `is_active`: boolean - 現在アクティブか

**Validation Rules**:
- device_type required
- ip_address format validation
- device_name length <= 50

### SystemStatus
システム全体の状態監視

**Fields**:
- `id`: string (UUID) - Primary key
- `timestamp`: datetime - 記録時刻
- `cpu_usage`: float - CPU使用率（%）
- `memory_usage`: float - メモリ使用率（%）
- `disk_usage`: float - ディスク使用率（%）
- `uptime`: integer - 稼働時間（秒）
- `active_sessions`: integer - アクティブセッション数
- `total_videos`: integer - 総動画数
- `m5stack_status`: enum - online, offline, error
- `display_status`: enum - active, idle, error
- `api_status`: enum - healthy, degraded, error

**Validation Rules**:
- percentage fields: 0.0 <= value <= 100.0
- uptime >= 0
- counts >= 0

### ControlEvent
操作ログとイベント追跡

**Fields**:
- `id`: string (UUID) - Primary key
- `session_id`: string - 関連セッションID（FK）
- `device_id`: string - 操作デバイスID（FK）
- `event_type`: enum - play, pause, stop, next, previous, volume, upload
- `event_data`: json - イベント詳細データ
- `timestamp`: datetime - イベント発生時刻
- `success`: boolean - 操作成功フラグ
- `error_message`: string - エラーメッセージ（nullable）

**Relationships**:
- Many-to-One with DisplaySession
- Many-to-One with UserDevice

## Database Schema (SQLite)

```sql
-- Videos table
CREATE TABLE videos (
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
CREATE TABLE display_sessions (
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
CREATE TABLE user_devices (
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
CREATE TABLE system_status (
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
CREATE TABLE control_events (
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
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_upload_time ON videos(upload_timestamp DESC);
CREATE INDEX idx_sessions_video_id ON display_sessions(video_id);
CREATE INDEX idx_sessions_start_time ON display_sessions(start_time DESC);
CREATE INDEX idx_events_timestamp ON control_events(timestamp DESC);
CREATE INDEX idx_events_session_id ON control_events(session_id);
```

## Business Rules

### Video Management
1. 同時に1つのアクティブ表示セッションのみ許可
2. 動画削除時は関連セッション・イベントも削除（CASCADE）
3. アップロード時は自動でサムネイル生成
4. ファイルサイズ上限チェック（500MB）

### Session Management  
1. セッション終了時は自動でend_time更新
2. システム再起動時は未終了セッションを自動クローズ
3. 24時間以上のセッションは自動終了

### Monitoring
1. システム状態は5分間隔で記録
2. 古いログは7日で自動削除
3. エラー発生時はM5STACKに通知表示

## Migration Strategy

初期データベース作成後:
1. Default video entry作成（テスト用）
2. System status monitoring開始
3. Default device entries作成（localhost, M5STACK）

データ整合性確保:
- Foreign key constraints有効化
- Transaction単位での操作
- Backup機能（日次）