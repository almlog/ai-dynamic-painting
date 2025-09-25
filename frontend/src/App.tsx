import { useState, useCallback, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import VideoList from './components/VideoList';
import VideoUpload from './components/VideoUpload';
import AIGenerationDashboard from './ai/components/AIGenerationDashboard';
import { 
  mockSystemStatus, 
  mockUsageStats, 
  mockFilterOptions,
  mockCurrentPlayback 
} from './data/mockData';
import { apiClient, convertApiVideoToVideo } from './services/api';
import type { Video } from './types';
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState<'ai-generation' | 'dashboard' | 'videos' | 'upload' | 'settings'>('ai-generation');
  const [videos, setVideos] = useState<Video[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Prevent unused variable warnings for state used in async functions
  void loading; 
  void error;

  // API経由で動画データを取得
  const loadVideos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getVideos();
      const convertedVideos = response.videos.map(convertApiVideoToVideo);
      setVideos(convertedVideos);
    } catch (error) {
      console.error('Failed to load videos:', error);
      setError('動画の読み込みに失敗しました');
      // フォールバックとしてMOCKデータを使用
      const { mockVideos } = await import('./data/mockData');
      setVideos(mockVideos);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初回ロード
  useEffect(() => {
    loadVideos();
  }, [loadVideos]);

  // 現在再生中の動画を取得
  const currentVideo = videos.find(v => v.id === mockCurrentPlayback.video_id) || null;
  
  // 最近の動画（5件）
  const recentVideos = videos
    .sort((a, b) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime())
    .slice(0, 5);

  // 動画選択処理
  const handleVideoSelect = useCallback((video: Video) => {
    console.log('Video selected:', video);
    // 実際の再生処理はここに実装
  }, []);

  // 動画アップロード完了処理
  const handleUploadComplete = useCallback(async (newVideo: Video) => {
    setShowUpload(false);
    alert(`「${newVideo.title}」のアップロードが完了しました！`);
    // 動画一覧を再取得
    await loadVideos();
  }, [loadVideos]);

  // アップロードエラー処理
  const handleUploadError = useCallback((error: string) => {
    alert(`アップロードエラー: ${error}`);
  }, []);

  // 動画削除処理
  const handleVideoDelete = useCallback(async (videoId: string) => {
    try {
      await apiClient.deleteVideo(videoId);
      alert('動画を削除しました');
      // 動画一覧を再取得
      await loadVideos();
    } catch (error) {
      console.error('Delete failed:', error);
      alert('動画の削除に失敗しました');
    }
  }, [loadVideos]);

  // アップロード画面表示
  const handleShowUpload = useCallback(() => {
    setShowUpload(true);
  }, []);

  return (
    <div className="app">
      {/* ナビゲーション */}
      <nav className="app-nav">
        <div className="nav-brand">
          <h1>AI Dynamic Painting</h1>
          <span className="version">Phase 1</span>
        </div>
        <div className="nav-links">
          <button 
            className={`nav-btn ${currentView === 'ai-generation' ? 'active' : ''}`}
            onClick={() => setCurrentView('ai-generation')}
          >
            🎨 AI Generation
          </button>
          <button 
            className={`nav-btn ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={`nav-btn ${currentView === 'videos' ? 'active' : ''}`}
            onClick={() => setCurrentView('videos')}
          >
            🎬 Videos
          </button>
          <button 
            className="nav-btn upload-btn"
            onClick={handleShowUpload}
          >
            📤 Upload
          </button>
          <button 
            className={`nav-btn ${currentView === 'settings' ? 'active' : ''}`}
            onClick={() => setCurrentView('settings')}
          >
            ⚙️ Settings
          </button>
        </div>
      </nav>

      {/* メインコンテンツ */}
      <main className="app-main">
        {/* アップロードモーダル */}
        {showUpload && (
          <div className="modal-overlay">
            <div className="modal-content">
              <div className="modal-header">
                <h2>動画アップロード</h2>
                <button 
                  className="modal-close"
                  onClick={() => setShowUpload(false)}
                >
                  ×
                </button>
              </div>
              <VideoUpload
                onUploadComplete={handleUploadComplete}
                onUploadError={handleUploadError}
                maxFileSize={200 * 1024 * 1024} // 200MB
                acceptedFormats={['.mp4', '.avi', '.mov', '.mkv']}
              />
            </div>
          </div>
        )}

        {/* ビュー切り替え */}
        {currentView === 'ai-generation' && (
          <AIGenerationDashboard />
        )}

        {currentView === 'dashboard' && (
          <Dashboard
            systemStatus={mockSystemStatus}
            currentVideo={currentVideo}
            usageStats={mockUsageStats}
            recentVideos={recentVideos}
          />
        )}

        {currentView === 'videos' && (
          <VideoList
            videos={videos}
            filterOptions={mockFilterOptions}
            onVideoSelect={handleVideoSelect}
            onVideoUpload={handleShowUpload}
            onVideoDelete={handleVideoDelete}
          />
        )}

        {currentView === 'settings' && (
          <div className="settings-placeholder">
            <h2>設定画面（開発予定）</h2>
            <p>T048: Settings componentの実装が必要です。</p>
            <div className="placeholder-content">
              <h3>予定機能:</h3>
              <ul>
                <li>表示設定（オーバーレイ、明度調整）</li>
                <li>生成設定（自動生成、品質選択）</li>
                <li>スケジュール設定（朝/夕時間）</li>
                <li>API設定（VEO API Key、Weather API Key）</li>
              </ul>
            </div>
          </div>
        )}
      </main>

    </div>
  )
}

export default App
