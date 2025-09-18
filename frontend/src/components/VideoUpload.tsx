/**
 * Video Upload Component - T045
 * Phase 1 手動動画管理システム - 動画アップロード機能
 */

import React, { useState, useCallback, useRef } from 'react';
import type { VideoUploadProps, Video } from '../types';

const VideoUpload: React.FC<VideoUploadProps> = ({
  onUploadComplete,
  onUploadError,
  maxFileSize = 200 * 1024 * 1024, // 200MB default
  acceptedFormats = ['.mp4', '.avi', '.mov', '.mkv']
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ファイル検証
  const validateFile = (file: File): string | null => {
    // ファイルサイズチェック
    if (file.size > maxFileSize) {
      return `ファイルサイズが大きすぎます (最大: ${Math.round(maxFileSize / 1024 / 1024)}MB)`;
    }

    // ファイル形式チェック
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFormats.includes(fileExtension)) {
      return `対応していないファイル形式です (対応形式: ${acceptedFormats.join(', ')})`;
    }

    return null;
  };

  // ファイル選択処理
  const handleFileSelect = useCallback((file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      onUploadError(validationError);
      return;
    }

    setSelectedFile(file);
  }, [maxFileSize, acceptedFormats, onUploadError]);

  // ドラッグアンドドロップ処理
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, [handleFileSelect]);

  // ファイル入力変更処理
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  // アップロード実行（実際のAPIコール部分）
  const executeUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      // プログレス更新のシミュレーション
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      // APIクライアント経由でアップロード
      const { apiClient, convertApiVideoToVideo } = await import('../services/api');
      const title = selectedFile.name.replace(/\.[^/.]+$/, "");
      const response = await apiClient.uploadVideo(selectedFile, title);
      
      // 完了時にプログレスを100%に
      clearInterval(progressInterval);
      setUploadProgress(100);

      // APIレスポンスをVideo型に変換
      const uploadedVideo: Video = convertApiVideoToVideo(response);

      onUploadComplete(uploadedVideo);
      setSelectedFile(null);
      setUploadProgress(0);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onUploadError(`アップロードエラー: ${errorMessage}`);
    } finally {
      setUploading(false);
    }
  };

  // アップロードキャンセル
  const handleCancel = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="video-upload">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedFormats.join(',')}
          onChange={handleInputChange}
          style={{ display: 'none' }}
          disabled={uploading}
        />
        
        {!selectedFile && !uploading && (
          <div className="upload-placeholder">
            <div className="upload-icon">📁</div>
            <h3>動画をアップロード</h3>
            <p>ファイルをドラッグ＆ドロップするか、クリックして選択してください</p>
            <p className="format-info">
              対応形式: {acceptedFormats.join(', ')} | 最大: {Math.round(maxFileSize / 1024 / 1024)}MB
            </p>
          </div>
        )}

        {selectedFile && !uploading && (
          <div className="file-selected">
            <div className="file-icon">🎬</div>
            <div className="file-info">
              <h4>{selectedFile.name}</h4>
              <p>サイズ: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <div className="file-actions">
              <button onClick={executeUpload} className="upload-btn">
                アップロード開始
              </button>
              <button onClick={handleCancel} className="cancel-btn">
                キャンセル
              </button>
            </div>
          </div>
        )}

        {uploading && (
          <div className="upload-progress">
            <div className="progress-icon">📤</div>
            <h4>アップロード中...</h4>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p>{uploadProgress}% 完了</p>
          </div>
        )}
      </div>

    </div>
  );
};

export default VideoUpload;