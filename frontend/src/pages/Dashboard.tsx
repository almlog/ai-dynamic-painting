/**
 * Main Dashboard Page - T049
 * Phase 1 手動動画管理システム - メインダッシュボードページ
 * すべてのコンポーネントを統合した中央管理画面
 */

import React, { useState, useEffect } from 'react';
import VideoUpload from '../components/VideoUpload';
import VideoList from '../components/VideoList';
import DisplayController from '../components/DisplayController';
import Dashboard from '../components/Dashboard';
import VideoGeneration from '../components/VideoGeneration';
import type { Video, SystemStatus, DisplayStatus } from '../types';
import type { VideoGenerationResponse } from '../types/video';

const MainDashboard: React.FC = () => {
  // 状態管理
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null);
  const [displayStatus, setDisplayStatus] = useState<DisplayStatus>({
    mode: 'idle',
    current_content_id: null,
    brightness: 100,
    overlay_enabled: false,
    fullscreen: false,
    last_updated: new Date().toISOString()
  });
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    uptime_seconds: 0,
    database: {
      connected: true,
      tables_count: 5
    },
    storage: {
      videos_directory_exists: true,
      free_space_mb: 1000
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // API通信用のベースURL
  const API_BASE_URL = 'http://localhost:8000/api';

  // 動画リスト取得
  const fetchVideos = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/videos`);
      if (!response.ok) throw new Error('動画リストの取得に失敗しました');
      
      const data = await response.json();
      setVideos(data.videos || []);
    } catch (err) {
      console.error('動画取得エラー:', err);
      setError('動画リストの読み込みに失敗しました');
    }
  };

  // システム状態取得
  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/system/health`);
      if (!response.ok) throw new Error('システム状態の取得に失敗しました');
      
      const data = await response.json();
      setSystemStatus(prev => ({ ...prev, ...data }));
    } catch (err) {
      console.error('システム状態取得エラー:', err);
    }
  };

  // 表示状態取得
  const fetchDisplayStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/display/status`);
      if (!response.ok) throw new Error('表示状態の取得に失敗しました');
      
      const data = await response.json();
      setDisplayStatus(prev => ({ ...prev, mode: data.status === 'playing' ? 'video' : 'idle', last_updated: new Date().toISOString() }));
      
      if (data.current_video_id) {
        const video = videos.find(v => v.id === data.current_video_id);
        setCurrentVideo(video || null);
      }
    } catch (err) {
      console.error('表示状態取得エラー:', err);
    }
  };

  // 初期データ読み込み
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      await Promise.all([
        fetchVideos(),
        fetchSystemStatus(),
        fetchDisplayStatus()
      ]);
      setLoading(false);
    };

    loadInitialData();
  }, []);

  // 定期更新
  useEffect(() => {
    const interval = setInterval(async () => {
      await Promise.all([
        fetchSystemStatus(),
        fetchDisplayStatus()
      ]);
    }, 5000); // 5秒ごと

    return () => clearInterval(interval);
  }, [videos]);

  // 動画アップロード成功時
  const handleVideoUploadSuccess = (newVideo: Video) => {
    setVideos(prev => [newVideo, ...prev]);
    fetchSystemStatus(); // 統計情報更新
  };

  // 動画削除
  const handleVideoDelete = async (videoId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/videos/${videoId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('動画の削除に失敗しました');
      
      setVideos(prev => prev.filter(v => v.id !== videoId));
      
      // 削除された動画が現在再生中の場合
      if (currentVideo?.id === videoId) {
        setCurrentVideo(null);
        setDisplayStatus(prev => ({ ...prev, mode: 'idle', current_content_id: null, last_updated: new Date().toISOString() }));
      }
      
      fetchSystemStatus(); // 統計情報更新
    } catch (err) {
      console.error('動画削除エラー:', err);
      setError('動画の削除に失敗しました');
    }
  };






  // VEO動画生成完了時
  const handleVideoGenerationComplete = (response: VideoGenerationResponse) => {
    console.log('✅ VEO動画生成完了:', response);
    // TODO: 生成履歴UI実装時に生成ログを更新
  };

  // VEO動画生成エラー時
  const handleVideoGenerationError = (errorMessage: string) => {
    console.error('❌ VEO動画生成エラー:', errorMessage);
    setError(`動画生成エラー: ${errorMessage}`);
  };

  // VEO動画生成進捗更新時
  const handleVideoGenerationProgress = (progress: number) => {
    console.log(`🎬 VEO動画生成進捗: ${progress}%`);
    // TODO: プログレス表示UI実装時に進捗バーを更新
  };

  // エラー表示クリア
  const clearError = () => {
    setError(null);
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>🤖 AI動的絵画システムを起動中...</p>
      </div>
    );
  }

  return (
    <div className="main-dashboard">
      {/* ヘッダー */}
      <header className="dashboard-header">
        <h1>🎨 AI動的絵画システム - Phase 6</h1>
        <p className="subtitle">VEO API統合 AI動画生成システム v6.0</p>
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={clearError} className="error-close">✕</button>
          </div>
        )}
      </header>

      {/* メインコンテンツ */}
      <main className="dashboard-main">
        {/* 左カラム: アップロード & 動画リスト */}
        <div className="left-column">
          <section className="upload-section">
            <VideoUpload 
              onUploadComplete={handleVideoUploadSuccess}
              onUploadError={(error) => setError(error)}
              maxFileSize={100 * 1024 * 1024} // 100MB
              acceptedFormats={['mp4', 'avi', 'mov', 'mkv']}
            />
          </section>

          <section className="veo-generation-section">
            <VideoGeneration
              onGenerationComplete={handleVideoGenerationComplete}
              onGenerationError={handleVideoGenerationError}
              onProgressUpdate={handleVideoGenerationProgress}
            />
          </section>
          
          <section className="video-list-section">
            <VideoList 
              videos={videos}
              currentVideo={currentVideo}
              filterOptions={{ sortBy: 'name', filterBy: 'all' }}
              onVideoSelect={setCurrentVideo}
              onVideoUpload={() => {}}
              onVideoDelete={handleVideoDelete}
            />
          </section>
        </div>

        {/* 右カラム: 制御 & 状態 */}
        <div className="right-column">
          <section className="display-control-section">
            <DisplayController
              status={displayStatus}
              onModeChange={(mode) => setDisplayStatus(prev => ({ ...prev, mode, last_updated: new Date().toISOString() }))}
              onBrightnessChange={(brightness) => setDisplayStatus(prev => ({ ...prev, brightness, last_updated: new Date().toISOString() }))}
              onOverlayToggle={() => setDisplayStatus(prev => ({ ...prev, overlay_enabled: !prev.overlay_enabled, last_updated: new Date().toISOString() }))}
              onFullscreenToggle={() => setDisplayStatus(prev => ({ ...prev, fullscreen: !prev.fullscreen, last_updated: new Date().toISOString() }))}
            />
          </section>

          <section className="system-status-section">
            <Dashboard
              systemStatus={systemStatus}
              currentVideo={currentVideo}
              usageStats={{
                total_videos: videos.length,
                total_size: videos.reduce((sum, v) => sum + (v.file_size || 0), 0),
                avg_duration: videos.length > 0 
                  ? videos.reduce((sum, v) => sum + (v.duration || 0), 0) / videos.length 
                  : 0
              }}
              recentVideos={videos.slice(0, 5)}
            />
          </section>
        </div>
      </main>

      {/* フッター */}
      <footer className="dashboard-footer">
        <div className="footer-info">
          <span>🤖 博士のAI動的絵画システム</span>
          <span>Phase 6: VEO API統合完了</span>
          <span>稼働時間: {Math.floor(systemStatus.uptime_seconds / 3600)}時間</span>
        </div>
      </footer>

      <style>{`
        .main-dashboard {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .loading-screen {
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .loading-spinner {
          width: 50px;
          height: 50px;
          border: 5px solid rgba(255, 255, 255, 0.3);
          border-top: 5px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 20px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .dashboard-header {
          padding: 20px;
          text-align: center;
          background: rgba(0, 0, 0, 0.2);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .dashboard-header h1 {
          margin: 0 0 10px 0;
          font-size: 2.5em;
          font-weight: 700;
          text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .subtitle {
          margin: 0;
          color: rgba(255, 255, 255, 0.8);
          font-size: 1.2em;
        }

        .error-banner {
          background: rgba(244, 67, 54, 0.2);
          border: 1px solid rgba(244, 67, 54, 0.5);
          border-radius: 8px;
          padding: 15px;
          margin: 15px auto;
          max-width: 600px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .error-close {
          background: none;
          border: none;
          color: white;
          font-size: 1.2em;
          cursor: pointer;
          padding: 0;
          margin-left: 15px;
        }

        .dashboard-main {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          padding: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .left-column, .right-column {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        section {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 15px;
          padding: 20px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .dashboard-footer {
          background: rgba(0, 0, 0, 0.3);
          padding: 15px;
          text-align: center;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .footer-info {
          display: flex;
          justify-content: center;
          gap: 30px;
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9em;
        }

        @media (max-width: 1024px) {
          .dashboard-main {
            grid-template-columns: 1fr;
            gap: 15px;
            padding: 15px;
          }
          
          .dashboard-header h1 {
            font-size: 2em;
          }
          
          .footer-info {
            flex-direction: column;
            gap: 10px;
          }
        }

        @media (max-width: 768px) {
          .dashboard-header {
            padding: 15px;
          }
          
          .dashboard-header h1 {
            font-size: 1.8em;
          }
          
          .subtitle {
            font-size: 1em;
          }
          
          section {
            padding: 15px;
          }
        }
      `}</style>
    </div>
  );
};

export default MainDashboard;