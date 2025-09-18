-- AI Dynamic Painting System - Phase 2 Database Schema Extensions
-- This schema extends the Phase 1 base schema with AI-specific tables

-- AI Generation Tasks Table
CREATE TABLE IF NOT EXISTS ai_generation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    prompt TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'processing', 'completed', 'failed')),
    scheduled_time TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    video_id INTEGER,
    generation_params TEXT,  -- JSON string of generation parameters
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    api_cost_usd REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);

-- AI Prompts History Table
CREATE TABLE IF NOT EXISTS ai_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_text TEXT NOT NULL,
    context_type TEXT CHECK(context_type IN ('morning', 'afternoon', 'evening', 'night', 'custom')),
    weather_context TEXT,  -- JSON string of weather data
    season TEXT CHECK(season IN ('spring', 'summer', 'autumn', 'winter')),
    generation_task_id INTEGER,
    success_rate REAL,
    user_rating REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generation_task_id) REFERENCES ai_generation_tasks(id)
);

-- User Preferences Learning Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    category TEXT CHECK(category IN ('theme', 'style', 'color', 'mood', 'content')),
    feedback_count INTEGER DEFAULT 0,
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    skip_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(preference_key, category)
);

-- User Feedback Table
CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    feedback_type TEXT NOT NULL CHECK(feedback_type IN ('good', 'bad', 'skip')),
    feedback_source TEXT CHECK(feedback_source IN ('m5stack', 'web_ui', 'api')),
    prompt_id INTEGER,
    context_data TEXT,  -- JSON string of context when feedback was given
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id),
    FOREIGN KEY (prompt_id) REFERENCES ai_prompts(id)
);

-- Weather Context Cache Table
CREATE TABLE IF NOT EXISTS weather_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    weather_data TEXT NOT NULL,  -- JSON string of weather API response
    temperature_celsius REAL,
    weather_condition TEXT,
    humidity_percent REAL,
    wind_speed_mps REAL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- API Cost Tracking Table
CREATE TABLE IF NOT EXISTS api_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_name TEXT NOT NULL CHECK(api_name IN ('veo', 'weather', 'other')),
    operation TEXT NOT NULL,
    cost_usd REAL NOT NULL,
    request_count INTEGER DEFAULT 1,
    generation_task_id INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    billing_period TEXT,  -- Format: YYYY-MM
    FOREIGN KEY (generation_task_id) REFERENCES ai_generation_tasks(id)
);

-- Generation Schedule Table
CREATE TABLE IF NOT EXISTS generation_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_type TEXT NOT NULL CHECK(schedule_type IN ('daily', 'interval', 'custom')),
    time_of_day TEXT,  -- Format: HH:MM for daily schedules
    interval_seconds INTEGER,  -- For interval-based schedules
    context_type TEXT CHECK(context_type IN ('morning', 'afternoon', 'evening', 'night', 'auto')),
    is_active BOOLEAN DEFAULT 1,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Model Performance Metrics Table
CREATE TABLE IF NOT EXISTS ai_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL CHECK(metric_type IN ('generation_time', 'quality_score', 'user_satisfaction', 'api_latency', 'cost_efficiency')),
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    generation_task_id INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generation_task_id) REFERENCES ai_generation_tasks(id)
);

-- Feature Flags Table (for gradual AI feature rollout)
CREATE TABLE IF NOT EXISTS feature_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name TEXT UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT 0,
    rollout_percentage REAL DEFAULT 0.0 CHECK(rollout_percentage >= 0 AND rollout_percentage <= 100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_generation_tasks_status ON ai_generation_tasks(status);
CREATE INDEX IF NOT EXISTS idx_generation_tasks_scheduled ON ai_generation_tasks(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_user_feedback_video ON user_feedback(video_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_api_costs_period ON api_costs(billing_period);
CREATE INDEX IF NOT EXISTS idx_api_costs_name ON api_costs(api_name);
CREATE INDEX IF NOT EXISTS idx_weather_cache_location ON weather_cache(location);
CREATE INDEX IF NOT EXISTS idx_weather_cache_expires ON weather_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_preferences_category ON user_preferences(category);
CREATE INDEX IF NOT EXISTS idx_ai_metrics_type ON ai_metrics(metric_type);

-- Initial feature flags
INSERT OR IGNORE INTO feature_flags (feature_name, is_enabled, rollout_percentage, description) VALUES
    ('ai_generation', 1, 100.0, 'Enable AI video generation using VEO API'),
    ('weather_integration', 1, 100.0, 'Enable weather-based context for video generation'),
    ('user_learning', 1, 100.0, 'Enable user preference learning system'),
    ('scheduled_generation', 1, 100.0, 'Enable automatic scheduled video generation'),
    ('cost_management', 1, 100.0, 'Enable API cost tracking and limits');

-- Initial generation schedules
INSERT OR IGNORE INTO generation_schedule (schedule_type, time_of_day, context_type, is_active) VALUES
    ('daily', '06:00', 'morning', 1),
    ('daily', '12:00', 'afternoon', 1),
    ('daily', '18:00', 'evening', 1),
    ('daily', '22:00', 'night', 1);