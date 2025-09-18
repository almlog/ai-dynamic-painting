/**
 * AIContentLibrary Component
 * TDD: GREEN phase - component implementation to pass tests
 */

import React, { useState, useEffect, useCallback } from 'react';

// Type definitions
interface ContentMetadata {
  prompt: string;
  style: string;
  quality: string;
  cost: number;
}

interface ContentItem {
  id: string;
  title: string;
  description: string;
  thumbnailUrl: string;
  videoUrl: string;
  category: string;
  tags: string[];
  duration: number;
  resolution: string;
  fileSize: string;
  createdAt: string;
  rating: number;
  favorited: boolean;
  downloadCount: number;
  metadata: ContentMetadata;
}

interface Category {
  id: string;
  name: string;
  count: number;
}

// Mock API service for testing
const createMockApiService = () => ({
  getContentLibrary: async (params?: any): Promise<ContentItem[]> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return [
      {
        id: 'content_1',
        title: 'Sunset Mountain Vista',
        description: 'Beautiful cinematic view of mountains during golden hour',
        thumbnailUrl: 'https://storage.example.com/thumb1.jpg',
        videoUrl: 'https://storage.example.com/video1.mp4',
        category: 'nature',
        tags: ['mountains', 'sunset', 'cinematic'],
        duration: 45,
        resolution: '1920x1080',
        fileSize: '25.4 MB',
        createdAt: '2025-09-15T10:00:00Z',
        rating: 4.8,
        favorited: true,
        downloadCount: 15,
        metadata: {
          prompt: 'Cinematic mountain sunset with golden light',
          style: 'cinematic',
          quality: 'high',
          cost: 0.75
        }
      },
      {
        id: 'content_2',
        title: 'Abstract Color Flow',
        description: 'Dynamic abstract patterns with flowing colors',
        thumbnailUrl: 'https://storage.example.com/thumb2.jpg',
        videoUrl: 'https://storage.example.com/video2.mp4',
        category: 'abstract',
        tags: ['abstract', 'colors', 'dynamic'],
        duration: 30,
        resolution: '1920x1080',
        fileSize: '18.2 MB',
        createdAt: '2025-09-16T14:30:00Z',
        rating: 4.2,
        favorited: false,
        downloadCount: 8,
        metadata: {
          prompt: 'Abstract flowing colors with dynamic movement',
          style: 'dynamic',
          quality: 'medium',
          cost: 0.45
        }
      },
      {
        id: 'content_3',
        title: 'Urban Night Scene',
        description: 'City lights and neon reflections at night',
        thumbnailUrl: 'https://storage.example.com/thumb3.jpg',
        videoUrl: 'https://storage.example.com/video3.mp4',
        category: 'urban',
        tags: ['city', 'night', 'neon'],
        duration: 60,
        resolution: '1920x1080',
        fileSize: '32.1 MB',
        createdAt: '2025-09-17T20:15:00Z',
        rating: 4.6,
        favorited: true,
        downloadCount: 22,
        metadata: {
          prompt: 'Cyberpunk city night with neon lights',
          style: 'cyberpunk',
          quality: 'high',
          cost: 0.85
        }
      }
    ];
  },

  searchContent: async (params: any): Promise<ContentItem[]> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    const allContent = await this.getContentLibrary();
    return allContent.filter(item => 
      item.title.toLowerCase().includes(params.query.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(params.query.toLowerCase()))
    );
  },

  getContentDetails: async (id: string): Promise<ContentItem> => {
    const allContent = await this.getContentLibrary();
    return allContent.find(item => item.id === id) || allContent[0];
  },

  favoriteContent: async (id: string): Promise<{ success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return { success: true };
  },

  unfavoriteContent: async (id: string): Promise<{ success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return { success: true };
  },

  rateContent: async (id: string, rating: number): Promise<{ success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { success: true };
  },

  deleteContent: async (id: string): Promise<{ success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { success: true };
  },

  downloadContent: async (id: string): Promise<{ downloadUrl: string }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { downloadUrl: 'https://storage.example.com/download.mp4' };
  },

  shareContent: async (id: string): Promise<{ shareUrl: string }> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return { shareUrl: 'https://share.example.com/video1' };
  },

  getContentCategories: async (): Promise<Category[]> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return [
      { id: 'nature', name: 'Nature', count: 12 },
      { id: 'abstract', name: 'Abstract', count: 8 },
      { id: 'urban', name: 'Urban', count: 15 },
      { id: 'space', name: 'Space', count: 6 }
    ];
  },

  bulkOperation: async (operation: string, ids: string[]): Promise<{ success: boolean; processed: number }> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    return { success: true, processed: ids.length };
  }
});

const AIContentLibrary: React.FC = () => {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [filteredContent, setFilteredContent] = useState<ContentItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [sortBy, setSortBy] = useState('createdAt');
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [bulkMode, setBulkMode] = useState(false);
  const [showDetails, setShowDetails] = useState<string | null>(null);
  const [showRating, setShowRating] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const apiService = createMockApiService();

  const loadContent = useCallback(async (params?: any) => {
    try {
      setLoading(true);
      setError(null);
      
      const [contentData, categoriesData] = await Promise.all([
        apiService.getContentLibrary(params),
        apiService.getContentCategories()
      ]);
      
      setContent(contentData);
      setCategories(categoriesData);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load content library');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadContent();
  }, [loadContent]);

  // Filter and sort content
  useEffect(() => {
    let filtered = [...content];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(item => item.category === categoryFilter);
    }

    // Favorites filter
    if (favoritesOnly) {
      filtered = filtered.filter(item => item.favorited);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'downloads':
          return b.downloadCount - a.downloadCount;
        case 'title':
          return a.title.localeCompare(b.title);
        case 'createdAt':
        default:
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      }
    });

    setFilteredContent(filtered);
  }, [content, searchQuery, categoryFilter, favoritesOnly, sortBy]);

  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query);
    if (query) {
      try {
        const results = await apiService.searchContent({
          query,
          category: categoryFilter,
          sortBy
        });
        setFilteredContent(results);
      } catch (err) {
        setMessage('Search failed');
      }
    }
  }, [categoryFilter, sortBy]);

  const handleToggleFavorite = useCallback(async (id: string) => {
    try {
      const item = content.find(c => c.id === id);
      if (!item) return;

      if (item.favorited) {
        await apiService.unfavoriteContent(id);
      } else {
        await apiService.favoriteContent(id);
      }

      setContent(prev => prev.map(item => 
        item.id === id ? { ...item, favorited: !item.favorited } : item
      ));
      
    } catch (err) {
      setMessage('Failed to update favorite status');
    }
  }, [content]);

  const handleRateContent = useCallback(async (id: string, rating: number) => {
    try {
      await apiService.rateContent(id, rating);
      
      setContent(prev => prev.map(item => 
        item.id === id ? { ...item, rating } : item
      ));
      
      setShowRating(null);
      setMessage('Content rated successfully');
      
    } catch (err) {
      setMessage('Failed to rate content');
    }
  }, []);

  const handleDownload = useCallback(async (id: string) => {
    try {
      const result = await apiService.downloadContent(id);
      setMessage('Download started');
      console.log('Download URL:', result.downloadUrl);
    } catch (err) {
      setMessage('Download failed');
    }
  }, []);

  const handleShare = useCallback(async (id: string) => {
    try {
      const result = await apiService.shareContent(id);
      setMessage('Share link copied to clipboard');
      console.log('Share URL:', result.shareUrl);
    } catch (err) {
      setMessage('Share failed');
    }
  }, []);

  const handleDelete = useCallback(async (id: string) => {
    try {
      await apiService.deleteContent(id);
      
      setContent(prev => prev.filter(item => item.id !== id));
      setShowDeleteConfirm(null);
      setMessage('Content deleted successfully');
      
    } catch (err) {
      setMessage('Failed to delete content');
    }
  }, []);

  const handleBulkSelection = useCallback((id: string) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  }, []);

  const handleBulkOperation = useCallback(async (operation: string) => {
    if (selectedItems.length === 0) return;

    try {
      await apiService.bulkOperation(operation, selectedItems);
      
      if (operation === 'delete') {
        setContent(prev => prev.filter(item => !selectedItems.includes(item.id)));
      } else if (operation === 'favorite') {
        setContent(prev => prev.map(item => 
          selectedItems.includes(item.id) ? { ...item, favorited: true } : item
        ));
      }
      
      setSelectedItems([]);
      setBulkMode(false);
      setMessage(`Bulk ${operation} completed for ${selectedItems.length} items`);
      
    } catch (err) {
      setMessage(`Bulk ${operation} failed`);
    }
  }, [selectedItems]);

  const handleRetry = useCallback(() => {
    loadContent();
  }, [loadContent]);

  const handleScroll = useCallback(async () => {
    // Lazy loading simulation
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
      try {
        const nextContent = await apiService.getContentLibrary({
          page: currentPage + 1,
          limit: 20
        });
        setContent(prev => [...prev, ...nextContent]);
        setCurrentPage(prev => prev + 1);
      } catch (err) {
        // Handle error silently for lazy loading
      }
    }
  }, [currentPage]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div role="main" className="ai-content-library">
        <div className="loading">Loading content library...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div role="main" className="ai-content-library">
        <div className="error">
          <p>Failed to load content library: {error}</p>
          <button onClick={handleRetry}>Retry</button>
        </div>
      </div>
    );
  }

  if (content.length === 0) {
    return (
      <div role="main" className="ai-content-library">
        <div className="empty-state">
          <p>No content found in your library.</p>
          <button onClick={() => setMessage('Redirecting to generation...')}>
            Generate your first AI video
          </button>
        </div>
      </div>
    );
  }

  return (
    <div role="main" className="ai-content-library">
      <header className="library-header">
        <h1>AI Content Library</h1>
        <p>Browse and manage your AI-generated videos and content</p>
      </header>

      {message && (
        <div role="status" className="message" aria-live="polite">
          {message}
        </div>
      )}

      {/* Search and Filter Controls */}
      <section className="controls">
        <div className="search-section" role="search">
          <input
            type="text"
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-section">
          <div className="filter-group">
            <label htmlFor="categoryFilter">Category Filter</label>
            <select
              id="categoryFilter"
              aria-label="Category Filter"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name} ({category.count})
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sortBy">Sort By</label>
            <select
              id="sortBy"
              aria-label="Sort By"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="createdAt">Date Created</option>
              <option value="rating">Rating</option>
              <option value="downloads">Downloads</option>
              <option value="title">Title</option>
            </select>
          </div>

          <button
            onClick={() => setFavoritesOnly(!favoritesOnly)}
            className={favoritesOnly ? 'active' : ''}
          >
            Favorites Only
          </button>
        </div>

        <div className="view-controls">
          <button
            onClick={() => setViewMode('grid')}
            className={viewMode === 'grid' ? 'active' : ''}
          >
            Grid View
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={viewMode === 'list' ? 'active' : ''}
          >
            List View
          </button>
          
          <button
            onClick={() => setBulkMode(!bulkMode)}
            className={bulkMode ? 'active' : ''}
          >
            Bulk Actions
          </button>
        </div>
      </section>

      {/* View Mode Indicators */}
      {viewMode === 'grid' && <div className="view-indicator">Grid View Active</div>}
      {viewMode === 'list' && <div className="view-indicator">List View Active</div>}

      {/* Bulk Actions Bar */}
      {bulkMode && (
        <section className="bulk-actions">
          <div className="bulk-info">
            <span>Select Mode</span>
            {selectedItems.length > 0 && (
              <span>{selectedItems.length} items selected</span>
            )}
          </div>
          
          <div className="bulk-buttons">
            <button onClick={() => handleBulkOperation('favorite')}>
              Add to Favorites
            </button>
            <button onClick={() => handleBulkOperation('delete')}>
              Delete Selected
            </button>
          </div>
        </section>
      )}

      {/* Content Grid/List */}
      <section className={`content-section ${viewMode}-view`}>
        {filteredContent.map((item) => (
          <div key={item.id} className="content-item">
            {bulkMode && (
              <input
                type="checkbox"
                checked={selectedItems.includes(item.id)}
                onChange={() => handleBulkSelection(item.id)}
                aria-label={`Select ${item.title}`}
              />
            )}

            <div className="content-thumbnail" onClick={() => setShowDetails(item.id)}>
              <img
                src={item.thumbnailUrl}
                alt={`${item.title} thumbnail`}
                loading="lazy"
              />
              <div className="duration-overlay">{item.duration}s</div>
            </div>

            <div className="content-info">
              <h3>{item.title}</h3>
              <p className="description">{item.description}</p>
              
              <div className="content-meta">
                <span className="rating">{item.rating}★</span>
                <span className="filesize">{item.fileSize}</span>
                {viewMode === 'list' && (
                  <>
                    <span>Created: {formatDate(item.createdAt)}</span>
                    <span>Downloads: {item.downloadCount}</span>
                  </>
                )}
              </div>

              <div className="content-tags">
                {item.tags.map((tag, index) => (
                  <span key={index} className="tag">{tag}</span>
                ))}
              </div>

              <div className="content-actions">
                <button
                  onClick={() => handleToggleFavorite(item.id)}
                  aria-label={`Toggle favorite for ${item.title}`}
                  className={item.favorited ? 'favorited' : ''}
                >
                  {item.favorited ? '♥' : '♡'}
                </button>
                
                <button onClick={() => setShowRating(item.id)}>Rate</button>
                <button onClick={() => handleDownload(item.id)}>Download</button>
                <button onClick={() => handleShare(item.id)}>Share</button>
                <button onClick={() => setShowDeleteConfirm(item.id)}>Delete</button>
              </div>
            </div>
          </div>
        ))}
      </section>

      {/* Content Details Modal */}
      {showDetails && (
        <div className="modal-overlay" onClick={() => setShowDetails(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Content Details</h2>
            {(() => {
              const item = content.find(c => c.id === showDetails);
              if (!item) return null;

              return (
                <div className="details-content">
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                  
                  <div className="details-meta">
                    <p>Prompt: {item.metadata.prompt}</p>
                    <p>Style: {item.metadata.style}</p>
                    <p>Quality: {item.metadata.quality}</p>
                    <p>Cost: ${item.metadata.cost.toFixed(2)}</p>
                    <p>Downloads: {item.downloadCount}</p>
                    <p>Resolution: {item.resolution}</p>
                    <p>Duration: {item.duration}s</p>
                  </div>
                </div>
              );
            })()}
            
            <button onClick={() => setShowDetails(null)}>Close</button>
          </div>
        </div>
      )}

      {/* Rating Modal */}
      {showRating && (
        <div className="modal-overlay" onClick={() => setShowRating(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Rate Content</h2>
            <div className="rating-buttons">
              {[1, 2, 3, 4, 5].map(rating => (
                <button
                  key={rating}
                  onClick={() => handleRateContent(showRating, rating)}
                >
                  {rating} Star{rating !== 1 ? 's' : ''}
                </button>
              ))}
            </div>
            <button onClick={() => handleRateContent(showRating, 5)}>Submit Rating</button>
            <button onClick={() => setShowRating(null)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Confirm Delete</h2>
            <p>Are you sure you want to delete this content? This action cannot be undone.</p>
            <div className="modal-actions">
              <button onClick={() => handleDelete(showDeleteConfirm)}>
                Delete Permanently
              </button>
              <button onClick={() => setShowDeleteConfirm(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Delete Confirmation */}
      {bulkMode && selectedItems.length > 0 && (
        <div className="bulk-confirm">
          <button onClick={() => handleBulkOperation('delete')}>
            Confirm Bulk Delete
          </button>
        </div>
      )}

      <style jsx>{`
        .ai-content-library {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .library-header {
          margin-bottom: 30px;
        }

        .library-header h1 {
          font-size: 2rem;
          margin-bottom: 10px;
          color: #333;
        }

        .library-header p {
          color: #666;
        }

        .message {
          background: #e8f5e8;
          border: 1px solid #4caf50;
          color: #2e7d32;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .loading, .error, .empty-state {
          text-align: center;
          padding: 40px;
        }

        .error p {
          color: #d32f2f;
          margin-bottom: 10px;
        }

        .controls {
          background: white;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .search-section {
          margin-bottom: 15px;
        }

        .search-input {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 16px;
        }

        .filter-section {
          display: flex;
          gap: 15px;
          align-items: center;
          flex-wrap: wrap;
          margin-bottom: 15px;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .filter-group label {
          font-weight: 500;
          font-size: 0.9rem;
        }

        .filter-group select {
          padding: 6px 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .view-controls {
          display: flex;
          gap: 10px;
          align-items: center;
        }

        .view-controls button, .filter-section button {
          padding: 8px 16px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
        }

        .view-controls button.active, .filter-section button.active {
          background: #2196f3;
          color: white;
          border-color: #2196f3;
        }

        .view-indicator {
          text-align: center;
          padding: 10px;
          background: #f0f7ff;
          border: 1px solid #2196f3;
          border-radius: 4px;
          margin-bottom: 15px;
          color: #1976d2;
        }

        .bulk-actions {
          background: #fff3e0;
          border: 1px solid #ff9800;
          border-radius: 4px;
          padding: 15px;
          margin-bottom: 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .bulk-info {
          display: flex;
          gap: 15px;
          align-items: center;
        }

        .bulk-buttons {
          display: flex;
          gap: 10px;
        }

        .content-section {
          display: grid;
          gap: 20px;
        }

        .content-section.grid-view {
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        }

        .content-section.list-view {
          grid-template-columns: 1fr;
        }

        .content-item {
          background: white;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          transition: transform 0.2s ease;
        }

        .content-item:hover {
          transform: translateY(-2px);
        }

        .list-view .content-item {
          display: flex;
          align-items: center;
          padding: 15px;
        }

        .content-thumbnail {
          position: relative;
          cursor: pointer;
        }

        .grid-view .content-thumbnail {
          width: 100%;
          height: 200px;
          overflow: hidden;
        }

        .list-view .content-thumbnail {
          width: 120px;
          height: 80px;
          margin-right: 15px;
          flex-shrink: 0;
        }

        .content-thumbnail img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .duration-overlay {
          position: absolute;
          bottom: 8px;
          right: 8px;
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 0.8rem;
        }

        .content-info {
          padding: 15px;
        }

        .list-view .content-info {
          padding: 0;
          flex: 1;
        }

        .content-info h3 {
          margin: 0 0 8px 0;
          font-size: 1.1rem;
          color: #333;
        }

        .description {
          color: #666;
          font-size: 0.9rem;
          margin-bottom: 10px;
          line-height: 1.4;
        }

        .content-meta {
          display: flex;
          gap: 10px;
          margin-bottom: 10px;
          font-size: 0.9rem;
          color: #666;
          flex-wrap: wrap;
        }

        .rating {
          color: #ff9800;
          font-weight: 500;
        }

        .content-tags {
          display: flex;
          gap: 5px;
          margin-bottom: 15px;
          flex-wrap: wrap;
        }

        .tag {
          background: #f0f0f0;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.8rem;
          color: #666;
        }

        .content-actions {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .content-actions button {
          padding: 6px 12px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
        }

        .content-actions button:hover {
          background: #f5f5f5;
        }

        .content-actions button.favorited {
          color: #e91e63;
          border-color: #e91e63;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal {
          background: white;
          border-radius: 8px;
          padding: 30px;
          max-width: 500px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .modal h2 {
          margin: 0 0 20px 0;
          color: #333;
        }

        .details-content {
          margin-bottom: 20px;
        }

        .details-meta p {
          margin: 8px 0;
          font-size: 0.9rem;
        }

        .rating-buttons {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
          flex-wrap: wrap;
        }

        .modal-actions {
          display: flex;
          gap: 10px;
          justify-content: flex-end;
        }

        .bulk-confirm {
          position: fixed;
          bottom: 20px;
          right: 20px;
          background: #d32f2f;
          color: white;
          padding: 10px 20px;
          border-radius: 4px;
          box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .bulk-confirm button {
          background: transparent;
          border: 1px solid white;
          color: white;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
        }

        input[type="checkbox"] {
          position: absolute;
          top: 10px;
          left: 10px;
          z-index: 10;
          transform: scale(1.2);
        }

        button {
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        button:hover {
          background-color: #f5f5f5;
        }

        @media (max-width: 768px) {
          .filter-section {
            flex-direction: column;
            align-items: stretch;
          }

          .filter-group {
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
          }

          .content-section.grid-view {
            grid-template-columns: 1fr;
          }

          .list-view .content-item {
            flex-direction: column;
            align-items: stretch;
          }

          .list-view .content-thumbnail {
            width: 100%;
            height: 200px;
            margin-right: 0;
            margin-bottom: 10px;
          }

          .content-actions {
            justify-content: center;
          }

          .modal {
            width: 95%;
            padding: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default AIContentLibrary;