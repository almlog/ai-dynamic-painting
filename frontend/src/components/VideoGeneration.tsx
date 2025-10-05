/**
 * VEO Video Generation Component - Phase 6
 * VEO API動画生成UI - プロンプト入力・生成・進捗表示
 * 
 * @author Claude (博士)
 * @created Phase 6 VEO API統合
 * @requirements Geminiの要件: プロンプト入力・生成ボタン・ローディング状態
 */

import React, { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import type { VideoGenerationRequest, VideoGenerationResponse } from '../types/video';

interface VideoGenerationProps {
  /** 動画生成完了時のコールバック */
  onGenerationComplete?: (response: VideoGenerationResponse) => void;
  /** エラー発生時のコールバック */
  onGenerationError?: (error: string) => void;
  /** 生成進捗更新時のコールバック */
  onProgressUpdate?: (progress: number) => void;
}

const VideoGeneration: React.FC<VideoGenerationProps> = ({
  onGenerationComplete,
  onGenerationError,
  onProgressUpdate
}) => {
  // State管理
  const [prompt, setPrompt] = useState<string>('');
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState<number>(0);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [generationResponse, setGenerationResponse] = useState<VideoGenerationResponse | null>(null);

  // 動画生成パラメータ（デフォルト値）
  const [generationParams, setGenerationParams] = useState({
    duration_seconds: 5,
    resolution: '720p' as const,
    fps: 24 as const,
    quality: 'standard' as const
  });

  // プロンプト入力バリデーション
  const validatePrompt = useCallback((inputPrompt: string): string | null => {
    if (!inputPrompt.trim()) {
      return 'プロンプトを入力してください';
    }
    if (inputPrompt.length < 10) {
      return 'プロンプトは10文字以上で入力してください';
    }
    if (inputPrompt.length > 2000) {
      return 'プロンプトは2000文字以下で入力してください';
    }
    return null;
  }, []);

  // 動画生成実行
  const handleGenerateVideo = async () => {
    const validationError = validatePrompt(prompt);
    if (validationError) {
      onGenerationError?.(validationError);
      return;
    }

    setGenerating(true);
    setProgress(0);
    setTaskId(null);
    setGenerationResponse(null);

    try {
      // VEO API動画生成リクエスト作成
      const request: VideoGenerationRequest = {
        prompt: prompt.trim(),
        ...generationParams
      };

      console.log('🎬 VEO動画生成開始:', request);

      // APIクライアント経由で動画生成リクエスト送信
      const response = await apiClient.generateVideo(request, {
        timeout: 30000, // 30秒タイムアウト
        maxRetries: 2    // 2回リトライ
      });

      console.log('✅ VEO動画生成レスポンス:', response);

      setTaskId(response.task_id);
      setGenerationResponse(response);
      
      // 進捗シミュレーション開始
      startProgressSimulation();

      onGenerationComplete?.(response);

    } catch (error) {
      console.error('❌ VEO動画生成エラー:', error);
      const errorMessage = error instanceof Error ? error.message : '動画生成に失敗しました';
      onGenerationError?.(errorMessage);
    } finally {
      setGenerating(false);
    }
  };

  // 進捗シミュレーション（実際のVEO APIポーリングは別途実装予定）
  const startProgressSimulation = () => {
    let currentProgress = 0;
    const progressInterval = setInterval(() => {
      currentProgress += Math.random() * 10;
      if (currentProgress >= 90) {
        currentProgress = 90; // 90%で停止（完了通知は別途）
        clearInterval(progressInterval);
      }
      setProgress(currentProgress);
      onProgressUpdate?.(currentProgress);
    }, 1000);
  };

  // キャンセル処理
  const handleCancel = () => {
    setPrompt('');
    setGenerating(false);
    setProgress(0);
    setTaskId(null);
    setGenerationResponse(null);
  };

  return (
    <div className="video-generation">
      <div className="generation-header">
        <h3>🎬 VEO動画生成</h3>
        <p>AIで美しい風景動画を生成します</p>
      </div>

      {/* プロンプト入力エリア */}
      <div className="prompt-section">
        <label htmlFor="prompt-input" className="prompt-label">
          動画の内容を説明してください:
        </label>
        <textarea
          id="prompt-input"
          className="prompt-textarea"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例: 美しい山の風景、流れる川、穏やかな自然のループ動画"
          rows={4}
          maxLength={2000}
          disabled={generating}
        />
        <div className="prompt-counter">
          {prompt.length}/2000 文字
        </div>
      </div>

      {/* 生成パラメータ */}
      <div className="params-section">
        <h4>生成設定</h4>
        <div className="params-grid">
          <div className="param-item">
            <label>長さ:</label>
            <select 
              value={generationParams.duration_seconds}
              onChange={(e) => setGenerationParams(prev => ({
                ...prev, 
                duration_seconds: parseInt(e.target.value)
              }))}
              disabled={generating}
            >
              <option value={5}>5秒</option>
              <option value={10}>10秒</option>
              <option value={15}>15秒</option>
              <option value={30}>30秒</option>
            </select>
          </div>
          
          <div className="param-item">
            <label>解像度:</label>
            <select 
              value={generationParams.resolution}
              onChange={(e) => setGenerationParams(prev => ({
                ...prev, 
                resolution: e.target.value as any
              }))}
              disabled={generating}
            >
              <option value="720p">720p (HD)</option>
              <option value="1080p">1080p (Full HD)</option>
            </select>
          </div>

          <div className="param-item">
            <label>品質:</label>
            <select 
              value={generationParams.quality}
              onChange={(e) => setGenerationParams(prev => ({
                ...prev, 
                quality: e.target.value as any
              }))}
              disabled={generating}
            >
              <option value="standard">標準品質</option>
              <option value="premium">高品質</option>
            </select>
          </div>
        </div>
      </div>

      {/* 生成ボタンエリア */}
      <div className="action-section">
        {!generating ? (
          <button 
            onClick={handleGenerateVideo}
            className="generate-btn"
            disabled={!prompt.trim() || prompt.length < 10}
          >
            🎬 動画を生成
          </button>
        ) : (
          <div className="generating-section">
            <div className="loading-indicator">
              <div className="spinner"></div>
              <span>生成中です...</span>
            </div>
            
            {taskId && (
              <div className="task-info">
                <p>タスクID: {taskId.substring(0, 8)}...</p>
              </div>
            )}
            
            <div className="progress-section">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <span className="progress-text">{Math.round(progress)}% 完了</span>
            </div>
            
            <button onClick={handleCancel} className="cancel-btn">
              キャンセル
            </button>
          </div>
        )}
      </div>

      {/* 生成結果表示 */}
      {generationResponse && !generating && (
        <div className="result-section">
          <h4>✅ 生成開始完了</h4>
          <p>{generationResponse.message}</p>
          <div className="result-details">
            <p><strong>タスクID:</strong> {generationResponse.task_id}</p>
            <p><strong>ステータス:</strong> {generationResponse.status}</p>
            {generationResponse.estimated_completion_time && (
              <p><strong>完了予定:</strong> {new Date(generationResponse.estimated_completion_time).toLocaleString('ja-JP')}</p>
            )}
          </div>
        </div>
      )}

      <style>{`
        .video-generation {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 15px;
          padding: 20px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .generation-header {
          text-align: center;
          margin-bottom: 20px;
        }

        .generation-header h3 {
          margin: 0 0 5px 0;
          font-size: 1.5em;
          color: white;
        }

        .generation-header p {
          margin: 0;
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9em;
        }

        .prompt-section {
          margin-bottom: 20px;
        }

        .prompt-label {
          display: block;
          margin-bottom: 8px;
          color: white;
          font-weight: 500;
        }

        .prompt-textarea {
          width: 100%;
          min-height: 100px;
          padding: 12px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          font-size: 14px;
          resize: vertical;
          transition: border-color 0.3s ease;
        }

        .prompt-textarea:focus {
          outline: none;
          border-color: rgba(255, 255, 255, 0.6);
        }

        .prompt-textarea::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }

        .prompt-counter {
          text-align: right;
          margin-top: 5px;
          color: rgba(255, 255, 255, 0.7);
          font-size: 0.8em;
        }

        .params-section {
          margin-bottom: 20px;
        }

        .params-section h4 {
          margin: 0 0 10px 0;
          color: white;
          font-size: 1.1em;
        }

        .params-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 15px;
        }

        .param-item {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .param-item label {
          color: rgba(255, 255, 255, 0.9);
          font-size: 0.9em;
          font-weight: 500;
        }

        .param-item select {
          padding: 8px;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 6px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          font-size: 14px;
        }

        .action-section {
          margin-bottom: 20px;
        }

        .generate-btn {
          width: 100%;
          padding: 15px;
          background: linear-gradient(45deg, #4CAF50, #45a049);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }

        .generate-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }

        .generate-btn:disabled {
          background: rgba(255, 255, 255, 0.2);
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        .generating-section {
          text-align: center;
        }

        .loading-indicator {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          margin-bottom: 15px;
          color: white;
          font-size: 16px;
        }

        .spinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .task-info {
          margin-bottom: 15px;
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9em;
        }

        .progress-section {
          margin-bottom: 15px;
        }

        .progress-bar {
          width: 100%;
          height: 8px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 8px;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #4CAF50, #8BC34A);
          border-radius: 4px;
          transition: width 0.5s ease;
        }

        .progress-text {
          color: white;
          font-size: 0.9em;
        }

        .cancel-btn {
          padding: 8px 20px;
          background: rgba(244, 67, 54, 0.8);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.3s ease;
        }

        .cancel-btn:hover {
          background: rgba(244, 67, 54, 1);
        }

        .result-section {
          background: rgba(76, 175, 80, 0.2);
          border: 1px solid rgba(76, 175, 80, 0.5);
          border-radius: 8px;
          padding: 15px;
          margin-top: 15px;
        }

        .result-section h4 {
          margin: 0 0 10px 0;
          color: #4CAF50;
          font-size: 1.1em;
        }

        .result-section p {
          margin: 0 0 10px 0;
          color: rgba(255, 255, 255, 0.9);
        }

        .result-details {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 6px;
          padding: 10px;
          font-size: 0.9em;
        }

        .result-details p {
          margin: 5px 0;
          color: rgba(255, 255, 255, 0.8);
        }

        .result-details strong {
          color: white;
        }

        @media (max-width: 768px) {
          .video-generation {
            padding: 15px;
          }
          
          .params-grid {
            grid-template-columns: 1fr;
          }
          
          .generate-btn {
            font-size: 14px;
            padding: 12px;
          }
        }
      `}</style>
    </div>
  );
};

export default VideoGeneration;