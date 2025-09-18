/**
 * DisplayController Component - T047
 * Phase 1 手動動画管理システム - 動画表示制御コンポーネント
 * 再生・一時停止・停止・音量・フルスクリーン制御
 */

import React, { useState, useEffect } from 'react';
import type { DisplayControllerProps, DisplayStatus } from '../types';

const DisplayController: React.FC<DisplayControllerProps> = ({
  currentVideo,
  displayStatus,
  onPlay,
  onPause,
  onStop,
  onVolumeChange,
  onFullscreenToggle
}) => {
  const [volume, setVolume] = useState(75);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  // 表示状態のアイコンとラベル
  const getStatusDisplay = (status: DisplayStatus) => {
    switch (status) {
      case 'playing': return { icon: '▶️', label: '再生中', color: '#4CAF50' };
      case 'paused': return { icon: '⏸️', label: '一時停止', color: '#FF9800' };
      case 'stopped': return { icon: '⏹️', label: '停止中', color: '#757575' };
      case 'loading': return { icon: '⏳', label: '読み込み中', color: '#2196F3' };
      default: return { icon: '⚪', label: '待機中', color: '#9E9E9E' };
    }
  };

  const statusInfo = getStatusDisplay(displayStatus);

  // 時間フォーマット（秒 → mm:ss）
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 再生制御イベントハンドラー
  const handlePlay = async () => {
    try {
      await onPlay?.(currentVideo?.id);
    } catch (error) {
      console.error('再生エラー:', error);
    }
  };

  const handlePause = async () => {
    try {
      await onPause?.();
    } catch (error) {
      console.error('一時停止エラー:', error);
    }
  };

  const handleStop = async () => {
    try {
      await onStop?.();
      setCurrentTime(0);
    } catch (error) {
      console.error('停止エラー:', error);
    }
  };

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
    onVolumeChange?.(newVolume);
  };

  const handleFullscreenToggle = () => {
    const newFullscreenState = !isFullscreen;
    setIsFullscreen(newFullscreenState);
    onFullscreenToggle?.(newFullscreenState);
  };

  // 現在時刻更新（デモ用）
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (displayStatus === 'playing' && currentVideo) {
      interval = setInterval(() => {
        setCurrentTime(prev => Math.min(prev + 1, currentVideo.duration || 0));
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [displayStatus, currentVideo]);

  return (
    <div className="display-controller">
      {/* 現在の動画情報 */}
      <div className="current-video-info">
        <h3>🎬 現在の動画</h3>
        {currentVideo ? (
          <div className="video-details">
            <div className="video-title">{currentVideo.title}</div>
            <div className="video-metadata">
              <span className="duration">{formatTime(currentVideo.duration || 0)}</span>
              <span className="format">・{currentVideo.format?.toUpperCase()}</span>
              <span className="size">・{Math.round((currentVideo.file_size || 0) / 1024 / 1024)}MB</span>
            </div>
            <div className="progress-info">
              <span className="current-time">{formatTime(currentTime)}</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${currentVideo.duration ? (currentTime / currentVideo.duration) * 100 : 0}%` 
                  }}
                />
              </div>
              <span className="total-time">{formatTime(currentVideo.duration || 0)}</span>
            </div>
          </div>
        ) : (
          <div className="no-video">動画が選択されていません</div>
        )}
      </div>

      {/* 再生状態表示 */}
      <div className="status-display">
        <div 
          className="status-indicator"
          style={{ backgroundColor: statusInfo.color }}
        >
          <span className="status-icon">{statusInfo.icon}</span>
          <span className="status-label">{statusInfo.label}</span>
        </div>
      </div>

      {/* メイン制御ボタン */}
      <div className="main-controls">
        <button 
          className="control-btn play-btn"
          onClick={handlePlay}
          disabled={!currentVideo || displayStatus === 'playing'}
          title="再生"
        >
          ▶️ 再生
        </button>

        <button 
          className="control-btn pause-btn"
          onClick={handlePause}
          disabled={displayStatus !== 'playing'}
          title="一時停止"
        >
          ⏸️ 一時停止
        </button>

        <button 
          className="control-btn stop-btn"
          onClick={handleStop}
          disabled={displayStatus === 'stopped'}
          title="停止"
        >
          ⏹️ 停止
        </button>
      </div>

      {/* 音量制御 */}
      <div className="volume-control">
        <label className="volume-label">
          🔊 音量: {volume}%
        </label>
        <input
          type="range"
          min="0"
          max="100"
          value={volume}
          onChange={(e) => handleVolumeChange(parseInt(e.target.value))}
          className="volume-slider"
        />
        <div className="volume-presets">
          <button onClick={() => handleVolumeChange(0)} className="volume-preset">🔇</button>
          <button onClick={() => handleVolumeChange(25)} className="volume-preset">🔈</button>
          <button onClick={() => handleVolumeChange(50)} className="volume-preset">🔉</button>
          <button onClick={() => handleVolumeChange(75)} className="volume-preset">🔊</button>
          <button onClick={() => handleVolumeChange(100)} className="volume-preset">📢</button>
        </div>
      </div>

      {/* 表示オプション */}
      <div className="display-options">
        <button 
          className={`option-btn fullscreen-btn ${isFullscreen ? 'active' : ''}`}
          onClick={handleFullscreenToggle}
          title="フルスクリーン切替"
        >
          {isFullscreen ? '🔳 ウィンドウ' : '⬛ フルスクリーン'}
        </button>
      </div>

      {/* 緊急停止ボタン */}
      <div className="emergency-controls">
        <button 
          className="emergency-stop-btn"
          onClick={handleStop}
          title="緊急停止"
        >
          🛑 緊急停止
        </button>
      </div>

      <style jsx>{`
        .display-controller {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 15px;
          padding: 20px;
          color: white;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .current-video-info h3 {
          margin: 0 0 15px 0;
          font-size: 1.2em;
          font-weight: 600;
        }

        .video-details {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          padding: 15px;
          margin-bottom: 20px;
        }

        .video-title {
          font-size: 1.1em;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .video-metadata {
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9em;
          margin-bottom: 12px;
        }

        .progress-info {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 0.9em;
        }

        .progress-bar {
          flex: 1;
          height: 6px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #4CAF50;
          transition: width 0.3s ease;
        }

        .no-video {
          text-align: center;
          color: rgba(255, 255, 255, 0.6);
          padding: 20px;
          font-style: italic;
        }

        .status-display {
          display: flex;
          justify-content: center;
          margin: 20px 0;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          border-radius: 25px;
          font-weight: 600;
          color: white;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .main-controls {
          display: flex;
          gap: 15px;
          justify-content: center;
          margin: 25px 0;
        }

        .control-btn {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-size: 1em;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          background: rgba(255, 255, 255, 0.2);
          color: white;
          backdrop-filter: blur(10px);
        }

        .control-btn:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.3);
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .control-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .volume-control {
          margin: 25px 0;
          text-align: center;
        }

        .volume-label {
          display: block;
          margin-bottom: 10px;
          font-weight: 600;
        }

        .volume-slider {
          width: 100%;
          max-width: 300px;
          margin-bottom: 15px;
        }

        .volume-presets {
          display: flex;
          justify-content: center;
          gap: 10px;
        }

        .volume-preset {
          padding: 8px 12px;
          border: none;
          background: rgba(255, 255, 255, 0.2);
          color: white;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .volume-preset:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .display-options {
          text-align: center;
          margin: 25px 0;
        }

        .option-btn {
          padding: 10px 20px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          background: rgba(255, 255, 255, 0.1);
          color: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
          font-weight: 600;
        }

        .option-btn.active {
          background: rgba(255, 255, 255, 0.3);
          border-color: rgba(255, 255, 255, 0.6);
        }

        .option-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .emergency-controls {
          text-align: center;
          margin-top: 30px;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
          padding-top: 20px;
        }

        .emergency-stop-btn {
          padding: 15px 30px;
          border: 2px solid #f44336;
          background: rgba(244, 67, 54, 0.2);
          color: white;
          border-radius: 10px;
          font-size: 1.1em;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .emergency-stop-btn:hover {
          background: rgba(244, 67, 54, 0.4);
          transform: scale(1.05);
          box-shadow: 0 6px 20px rgba(244, 67, 54, 0.3);
        }
      `}</style>
    </div>
  );
};

export default DisplayController;