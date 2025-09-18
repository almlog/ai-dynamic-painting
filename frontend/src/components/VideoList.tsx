/**
 * Video List Management UI - T046
 * Phase 1 手動動画管理システム - 動画一覧・管理機能
 */

import React, { useState, useMemo, useCallback } from 'react';
import type { VideoListProps, Video } from '../types';

const VideoList: React.FC<VideoListProps> = ({
  videos,
  filterOptions,
  onVideoSelect,
  onVideoUpload,
  onVideoDelete
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<'date' | 'rating' | 'views' | 'name'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // フィルタリングとソート処理
  const filteredAndSortedVideos = useMemo(() => {
    let filtered = [...videos];

    // カテゴリーフィルター
    if (selectedCategory !== 'All') {
      filtered = filtered.filter(video => {
        switch (selectedCategory) {
          case 'Generated':
            return !video.is_manual_upload;
          case 'Uploaded':
            return video.is_manual_upload;
          case 'Favorites':
            return video.user_rating >= 4.0;
          default:
            return true;
        }
      });
    }

    // 検索クエリフィルター
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(video =>
        video.title.toLowerCase().includes(query) ||
        video.description.toLowerCase().includes(query) ||
        video.filename.toLowerCase().includes(query) ||
        video.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // タグフィルター
    if (selectedTags.length > 0) {
      filtered = filtered.filter(video =>
        selectedTags.every(tag => video.tags.includes(tag))
      );
    }

    // ソート処理
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'date':
          aValue = new Date(a.uploaded_at).getTime();
          bValue = new Date(b.uploaded_at).getTime();
          break;
        case 'rating':
          aValue = a.user_rating;
          bValue = b.user_rating;
          break;
        case 'views':
          aValue = a.view_count;
          bValue = b.view_count;
          break;
        case 'name':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [videos, selectedCategory, searchQuery, selectedTags, sortBy, sortOrder]);

  // タグ選択トグル
  const toggleTag = useCallback((tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  }, []);

  // 星評価コンポーネント
  const StarRating: React.FC<{ rating: number; size?: number }> = ({ rating, size = 16 }) => {
    const stars = Array.from({ length: 5 }, (_, i) => {
      const filled = i < Math.floor(rating);
      const half = i === Math.floor(rating) && rating % 1 >= 0.5;
      
      return (
        <span
          key={i}
          className={`star ${filled ? 'filled' : half ? 'half' : 'empty'}`}
          style={{ fontSize: `${size}px` }}
        >
          {filled ? '★' : half ? '☆' : '☆'}
        </span>
      );
    });
    return <div className="star-rating">{stars}</div>;
  };

  // 動画カードコンポーネント
  const VideoCard: React.FC<{ video: Video }> = ({ video }) => (
    <div className={`video-card ${viewMode}`} onClick={() => onVideoSelect(video)}>
      <div className="thumbnail-container">
        <img 
          src={video.thumbnail_url} 
          alt={video.title}
          className="thumbnail"
          onError={(e) => {
            (e.target as HTMLImageElement).src = '/thumbnails/default.jpg';
          }}
        />
        <div className="duration-badge">
          {Math.round(video.duration)}s
        </div>
        <div className="status-badge">
          {video.playback_status === 'playing' && '▶️'}
          {video.playback_status === 'paused' && '⏸️'}
        </div>
      </div>
      
      <div className="video-info">
        <h4 className="video-title">{video.title}</h4>
        <p className="video-description">{video.description}</p>
        
        <div className="video-metadata">
          <StarRating rating={video.user_rating} />
          <span className="views">👁️ {video.view_count}</span>
          <span className="file-size">{(video.file_size / 1024 / 1024).toFixed(1)}MB</span>
        </div>
        
        <div className="video-tags">
          {video.tags.slice(0, 3).map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
          {video.tags.length > 3 && <span className="tag-more">+{video.tags.length - 3}</span>}
        </div>
        
        <div className="video-actions">
          <button className="action-btn play" onClick={(e) => {
            e.stopPropagation();
            onVideoSelect(video);
          }}>
            ▶️
          </button>
          <button className="action-btn favorite">⭐</button>
          <button 
            className="action-btn delete"
            onClick={(e) => {
              e.stopPropagation();
              if (window.confirm(`「${video.title}」を削除しますか？`)) {
                onVideoDelete(video.id);
              }
            }}
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="video-list">
      {/* ヘッダーとコントロール */}
      <div className="list-header">
        <div className="header-title">
          <h2>動画ライブラリ ({filteredAndSortedVideos.length}件)</h2>
          <button className="upload-btn" onClick={onVideoUpload}>
            + Upload Video
          </button>
        </div>
        
        <div className="list-controls">
          {/* カテゴリーフィルター */}
          <div className="filter-group">
            <label>カテゴリー:</label>
            <select 
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {filterOptions.categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          
          {/* 検索ボックス */}
          <div className="filter-group">
            <label>検索:</label>
            <input
              type="text"
              placeholder="タイトル、説明、タグで検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
          
          {/* ソート */}
          <div className="filter-group">
            <label>並び順:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)}>
              <option value="date">日付</option>
              <option value="rating">評価</option>
              <option value="views">再生回数</option>
              <option value="name">名前</option>
            </select>
            <button 
              className="sort-toggle"
              onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'desc' ? '↓' : '↑'}
            </button>
          </div>
          
          {/* 表示モード */}
          <div className="filter-group">
            <button 
              className={`view-mode-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              ⊞
            </button>
            <button 
              className={`view-mode-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              ☰
            </button>
          </div>
        </div>
      </div>
      
      {/* タグフィルター */}
      <div className="tag-filter">
        <span>タグ:</span>
        {filterOptions.tags.map(tag => (
          <button
            key={tag}
            className={`tag-btn ${selectedTags.includes(tag) ? 'selected' : ''}`}
            onClick={() => toggleTag(tag)}
          >
            {tag}
          </button>
        ))}
        {selectedTags.length > 0 && (
          <button className="clear-tags" onClick={() => setSelectedTags([])}>
            クリア
          </button>
        )}
      </div>
      
      {/* 動画一覧 */}
      <div className={`video-grid ${viewMode}`}>
        {filteredAndSortedVideos.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📹</div>
            <h3>動画が見つかりません</h3>
            <p>検索条件を変更するか、新しい動画をアップロードしてください。</p>
            <button className="upload-btn" onClick={onVideoUpload}>
              動画をアップロード
            </button>
          </div>
        ) : (
          filteredAndSortedVideos.map(video => (
            <VideoCard key={video.id} video={video} />
          ))
        )}
      </div>
      
    </div>
  );
};

export default VideoList;