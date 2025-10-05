/**
 * Dashboard Component - T047
 * Phase 1 手動動画管理システム - メインダッシュボード
 */

import React, { useState } from 'react';
import type { DashboardProps } from '../types';

const Dashboard: React.FC<DashboardProps> = ({
  systemStatus,
  currentVideo,
  usageStats,
  recentVideos
}) => {
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  // システム状態インジケーター
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#4CAF50';
      case 'degraded': return '#FF9800';
      case 'unhealthy': return '#f44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '🟢';
      case 'degraded': return '🟡';
      case 'unhealthy': return '🔴';
      default: return '⚪';
    }
  };

  // アップタイム表示フォーマット
  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return `${days}日 ${remainingHours}時間`;
    } else if (hours > 0) {
      return `${hours}時間 ${minutes}分`;
    } else {
      return `${minutes}分`;
    }
  };

  // ファイルサイズフォーマット
  const formatFileSize = (bytes: number) => {
    if (bytes >= 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)}GB`;
    } else {
      return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    }
  };

  // 使用率カラー
  const getUsageColor = (used: number, total: number) => {
    const percentage = (used / total) * 100;
    if (percentage >= 90) return '#f44336';
    if (percentage >= 75) return '#FF9800';
    return '#4CAF50';
  };

  // クイックアクション処理
  const handleQuickAction = (action: string) => {
    setSelectedAction(action);
    // 実際のアクション処理はここに実装
    console.log(`Quick action: ${action}`);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>AI Dynamic Painting - Control Panel</h1>
        <div className="last-updated">
          最終更新: {new Date(systemStatus.timestamp).toLocaleString('ja-JP')}
        </div>
      </div>

      {/* システム状態セクション */}
      <section className="status-section">
        <h2>現在の状態</h2>
        <div className="status-cards">
          <div className="status-card">
            <div className="card-header">
              <h3>システム状態</h3>
              <span className="status-icon">
                {getStatusIcon(systemStatus.status)}
              </span>
            </div>
            <div className="card-content">
              <div className="status-value" style={{ color: getStatusColor(systemStatus.status) }}>
                {systemStatus.status === 'healthy' ? '正常' : 
                 systemStatus.status === 'degraded' ? '注意' : '異常'}
              </div>
              <div className="status-detail">
                アップタイム: {formatUptime(systemStatus.uptime_seconds)}
              </div>
              <div className="status-detail">
                Ver: {systemStatus.version}
              </div>
            </div>
          </div>

          <div className="status-card">
            <div className="card-header">
              <h3>動画再生中</h3>
              <span className="status-icon">🎬</span>
            </div>
            <div className="card-content">
              {currentVideo ? (
                <>
                  <div className="status-value">{currentVideo.title}</div>
                  <div className="status-detail">
                    再生時間: {Math.round(currentVideo.duration)}秒
                  </div>
                  <div className="status-detail">
                    視聴回数: {currentVideo.view_count}回
                  </div>
                </>
              ) : (
                <>
                  <div className="status-value">待機中</div>
                  <div className="status-detail">動画が選択されていません</div>
                </>
              )}
            </div>
          </div>

          <div className="status-card">
            <div className="card-header">
              <h3>月間使用量</h3>
              <span className="status-icon">📊</span>
            </div>
            <div className="card-content">
              <div className="status-value" style={{ color: getUsageColor(usageStats.monthly_used ?? 0, usageStats.monthly_limit ?? 0) }}>
                {usageStats.monthly_used ?? 0}/{usageStats.monthly_limit ?? 0}
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${((usageStats.monthly_used ?? 0) / (usageStats.monthly_limit ?? 1)) * 100}%`,
                    backgroundColor: getUsageColor(usageStats.monthly_used ?? 0, usageStats.monthly_limit ?? 0)
                  }}
                ></div>
              </div>
              <div className="status-detail">
                今日: {usageStats.daily_used ?? 0}/{usageStats.daily_limit ?? 0}
              </div>
            </div>
          </div>

          <div className="status-card">
            <div className="card-header">
              <h3>ストレージ</h3>
              <span className="status-icon">💾</span>
            </div>
            <div className="card-content">
              <div className="status-value">
                {formatFileSize((usageStats.storage_used_gb ?? 0) * 1024 * 1024 * 1024)} / 
                {formatFileSize((usageStats.storage_total_gb ?? 0) * 1024 * 1024 * 1024)}
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${((usageStats.storage_used_gb ?? 0) / (usageStats.storage_total_gb ?? 1)) * 100}%`,
                    backgroundColor: getUsageColor(usageStats.storage_used_gb ?? 0, usageStats.storage_total_gb ?? 0)
                  }}
                ></div>
              </div>
              <div className="status-detail">
                動画数: {usageStats.total_videos}本
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* クイックアクションセクション */}
      <section className="actions-section">
        <h2>クイックアクション</h2>
        <div className="action-buttons">
          <button 
            className={`action-btn ${selectedAction === 'next' ? 'active' : ''}`}
            onClick={() => handleQuickAction('next')}
          >
            <span className="btn-icon">⏭️</span>
            次の動画
          </button>
          <button 
            className={`action-btn ${selectedAction === 'generate' ? 'active' : ''}`}
            onClick={() => handleQuickAction('generate')}
          >
            <span className="btn-icon">✨</span>
            生成リクエスト
          </button>
          <button 
            className={`action-btn ${selectedAction === 'restart' ? 'active' : ''}`}
            onClick={() => handleQuickAction('restart')}
          >
            <span className="btn-icon">🔄</span>
            再起動
          </button>
          <button 
            className={`action-btn ${selectedAction === 'maintenance' ? 'active' : ''}`}
            onClick={() => handleQuickAction('maintenance')}
          >
            <span className="btn-icon">🔧</span>
            メンテナンス
          </button>
        </div>
      </section>

      {/* 最近の動画セクション */}
      <section className="recent-videos-section">
        <div className="section-header">
          <h2>最近の動画 ({recentVideos.length}件)</h2>
          <button className="view-all-btn">すべて表示</button>
        </div>
        <div className="recent-videos-grid">
          {recentVideos.map(video => (
            <div key={video.id} className="recent-video-card">
              <div className="video-thumbnail">
                <img 
                  src={video.thumbnail_url} 
                  alt={video.title}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/thumbnails/default.jpg';
                  }}
                />
                <div className="play-overlay">
                  <span className="play-icon">▶️</span>
                </div>
              </div>
              
              <div className="video-info">
                <h4 className="video-title">{video.title}</h4>
                <div className="video-metadata">
                  <span className="rating">
                    {'★'.repeat(Math.floor(video.user_rating))}
                    {'☆'.repeat(5 - Math.floor(video.user_rating))}
                  </span>
                  <span className="views">👁️ {video.view_count}</span>
                </div>
                <div className="video-actions">
                  <button className="mini-btn play-btn">▶️</button>
                  <button className="mini-btn star-btn">⭐</button>
                  <button className="mini-btn delete-btn">🗑️</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
};

export default Dashboard;