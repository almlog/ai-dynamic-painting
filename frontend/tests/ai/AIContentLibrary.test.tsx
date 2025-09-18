/**
 * Tests for AIContentLibrary component
 * TDD: RED phase - tests written before component implementation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import AIContentLibrary from '../../src/ai/components/AIContentLibrary';

// Mock API functions
const mockApiService = {
  getContentLibrary: vi.fn(),
  searchContent: vi.fn(),
  getContentDetails: vi.fn(),
  favoriteContent: vi.fn(),
  unfavoriteContent: vi.fn(),
  rateContent: vi.fn(),
  deleteContent: vi.fn(),
  downloadContent: vi.fn(),
  shareContent: vi.fn(),
  getContentCategories: vi.fn(),
  bulkOperation: vi.fn()
};

// Mock content library data
const mockContentLibrary = [
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

const mockCategories = [
  { id: 'nature', name: 'Nature', count: 12 },
  { id: 'abstract', name: 'Abstract', count: 8 },
  { id: 'urban', name: 'Urban', count: 15 },
  { id: 'space', name: 'Space', count: 6 }
];

describe('AIContentLibrary Component', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    
    // Setup default mock implementations
    mockApiService.getContentLibrary.mockResolvedValue(mockContentLibrary);
    mockApiService.searchContent.mockResolvedValue(mockContentLibrary);
    mockApiService.getContentDetails.mockResolvedValue(mockContentLibrary[0]);
    mockApiService.favoriteContent.mockResolvedValue({ success: true });
    mockApiService.unfavoriteContent.mockResolvedValue({ success: true });
    mockApiService.rateContent.mockResolvedValue({ success: true });
    mockApiService.deleteContent.mockResolvedValue({ success: true });
    mockApiService.downloadContent.mockResolvedValue({ downloadUrl: 'https://storage.example.com/download.mp4' });
    mockApiService.shareContent.mockResolvedValue({ shareUrl: 'https://share.example.com/video1' });
    mockApiService.getContentCategories.mockResolvedValue(mockCategories);
    mockApiService.bulkOperation.mockResolvedValue({ success: true, processed: 2 });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render main content library header', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByText('AI Content Library')).toBeInTheDocument();
        expect(screen.getByText(/browse and manage your ai-generated videos/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should render search and filter controls', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search content...')).toBeInTheDocument();
        expect(screen.getByLabelText('Category Filter')).toBeInTheDocument();
        expect(screen.getByLabelText('Sort By')).toBeInTheDocument();
      });
    });

    it('should display content grid with thumbnails', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByText('Sunset Mountain Vista')).toBeInTheDocument();
        expect(screen.getByText('Abstract Color Flow')).toBeInTheDocument();
        expect(screen.getByText('Urban Night Scene')).toBeInTheDocument();
      });
    });

    it('should show content metadata', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByText('45s')).toBeInTheDocument(); // duration
        expect(screen.getByText('25.4 MB')).toBeInTheDocument(); // file size
        expect(screen.getByText('4.8★')).toBeInTheDocument(); // rating
      });
    });
  });

  describe('Content Filtering and Search', () => {
    it('should filter content by category', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.change(screen.getByLabelText('Category Filter'), {
          target: { value: 'nature' }
        });
      });
      
      await waitFor(() => {
        expect(screen.getByText('Sunset Mountain Vista')).toBeInTheDocument();
        expect(screen.queryByText('Abstract Color Flow')).not.toBeInTheDocument();
      });
    });

    it('should search content by title and tags', async () => {
      render(<AIContentLibrary />);
      
      const searchInput = screen.getByPlaceholderText('Search content...');
      fireEvent.change(searchInput, {
        target: { value: 'mountain' }
      });
      
      await waitFor(() => {
        expect(mockApiService.searchContent).toHaveBeenCalledWith({
          query: 'mountain',
          category: 'all',
          sortBy: 'createdAt'
        });
      });
    });

    it('should sort content by different criteria', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.change(screen.getByLabelText('Sort By'), {
          target: { value: 'rating' }
        });
      });
      
      await waitFor(() => {
        const titles = screen.getAllByText(/Vista|Flow|Scene/);
        expect(titles[0]).toHaveTextContent('Sunset Mountain Vista'); // highest rating 4.8
      });
    });

    it('should filter by favorites only', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Favorites Only'));
      });
      
      await waitFor(() => {
        expect(screen.getByText('Sunset Mountain Vista')).toBeInTheDocument();
        expect(screen.getByText('Urban Night Scene')).toBeInTheDocument();
        expect(screen.queryByText('Abstract Color Flow')).not.toBeInTheDocument();
      });
    });
  });

  describe('Content Actions', () => {
    it('should toggle favorite status', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const favoriteButtons = screen.getAllByLabelText(/toggle favorite/i);
        fireEvent.click(favoriteButtons[1]); // Abstract Color Flow (not favorited)
      });
      
      await waitFor(() => {
        expect(mockApiService.favoriteContent).toHaveBeenCalledWith('content_2');
      });
    });

    it('should rate content', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Rate'));
      });
      
      expect(screen.getByText('Rate Content')).toBeInTheDocument();
      
      const starButtons = screen.getAllByRole('button');
      const fiveStarButton = starButtons.find(btn => btn.textContent?.includes('5'));
      if (fiveStarButton) {
        fireEvent.click(fiveStarButton);
      }
      
      fireEvent.click(screen.getByText('Submit Rating'));
      
      await waitFor(() => {
        expect(mockApiService.rateContent).toHaveBeenCalledWith('content_1', 5);
      });
    });

    it('should download content', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const downloadButtons = screen.getAllByText('Download');
        fireEvent.click(downloadButtons[0]);
      });
      
      await waitFor(() => {
        expect(mockApiService.downloadContent).toHaveBeenCalledWith('content_1');
        expect(screen.getByText('Download started')).toBeInTheDocument();
      });
    });

    it('should share content', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const shareButtons = screen.getAllByText('Share');
        fireEvent.click(shareButtons[0]);
      });
      
      await waitFor(() => {
        expect(mockApiService.shareContent).toHaveBeenCalledWith('content_1');
        expect(screen.getByText('Share link copied to clipboard')).toBeInTheDocument();
      });
    });

    it('should delete content with confirmation', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const deleteButtons = screen.getAllByText('Delete');
        fireEvent.click(deleteButtons[0]);
      });
      
      expect(screen.getByText('Confirm Delete')).toBeInTheDocument();
      expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Delete Permanently'));
      
      await waitFor(() => {
        expect(mockApiService.deleteContent).toHaveBeenCalledWith('content_1');
      });
    });
  });

  describe('Content Details Modal', () => {
    it('should open content details on thumbnail click', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const thumbnails = screen.getAllByAltText(/thumbnail/i);
        fireEvent.click(thumbnails[0]);
      });
      
      expect(screen.getByText('Content Details')).toBeInTheDocument();
      expect(screen.getByText('Sunset Mountain Vista')).toBeInTheDocument();
      expect(screen.getByText('Beautiful cinematic view of mountains during golden hour')).toBeInTheDocument();
    });

    it('should display full metadata in details modal', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const thumbnails = screen.getAllByAltText(/thumbnail/i);
        fireEvent.click(thumbnails[0]);
      });
      
      expect(screen.getByText('Prompt: Cinematic mountain sunset with golden light')).toBeInTheDocument();
      expect(screen.getByText('Style: cinematic')).toBeInTheDocument();
      expect(screen.getByText('Quality: high')).toBeInTheDocument();
      expect(screen.getByText('Cost: $0.75')).toBeInTheDocument();
      expect(screen.getByText('Downloads: 15')).toBeInTheDocument();
    });

    it('should close details modal', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const thumbnails = screen.getAllByAltText(/thumbnail/i);
        fireEvent.click(thumbnails[0]);
      });
      
      fireEvent.click(screen.getByText('Close'));
      
      await waitFor(() => {
        expect(screen.queryByText('Content Details')).not.toBeInTheDocument();
      });
    });
  });

  describe('Bulk Operations', () => {
    it('should enable bulk selection mode', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Bulk Actions'));
      });
      
      expect(screen.getByText('Select Mode')).toBeInTheDocument();
      expect(screen.getAllByRole('checkbox')).toHaveLength(3); // One for each content item
    });

    it('should select multiple items', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Bulk Actions'));
      });
      
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);
      fireEvent.click(checkboxes[1]);
      
      expect(screen.getByText('2 items selected')).toBeInTheDocument();
    });

    it('should perform bulk delete', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Bulk Actions'));
      });
      
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);
      fireEvent.click(checkboxes[1]);
      
      fireEvent.click(screen.getByText('Delete Selected'));
      fireEvent.click(screen.getByText('Confirm Bulk Delete'));
      
      await waitFor(() => {
        expect(mockApiService.bulkOperation).toHaveBeenCalledWith('delete', ['content_1', 'content_2']);
      });
    });

    it('should perform bulk favorite', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Bulk Actions'));
      });
      
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[1]); // Abstract Color Flow
      
      fireEvent.click(screen.getByText('Add to Favorites'));
      
      await waitFor(() => {
        expect(mockApiService.bulkOperation).toHaveBeenCalledWith('favorite', ['content_2']);
      });
    });
  });

  describe('View Modes', () => {
    it('should switch between grid and list view', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('List View'));
      });
      
      expect(screen.getByText('List View Active')).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Grid View'));
      
      expect(screen.getByText('Grid View Active')).toBeInTheDocument();
    });

    it('should display different information in list view', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('List View'));
      });
      
      await waitFor(() => {
        expect(screen.getByText('Created: 2025-09-15')).toBeInTheDocument();
        expect(screen.getByText('Downloads: 15')).toBeInTheDocument();
      });
    });
  });

  describe('Performance and Loading', () => {
    it('should show loading state', async () => {
      // Delay the API response
      mockApiService.getContentLibrary.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(mockContentLibrary), 2000))
      );
      
      render(<AIContentLibrary />);
      
      expect(screen.getByText('Loading content library...')).toBeInTheDocument();
    });

    it('should implement lazy loading for large libraries', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        fireEvent.scroll(window, { target: { scrollY: 1000 } });
      });
      
      // Should load more content when scrolling
      expect(mockApiService.getContentLibrary).toHaveBeenCalledWith({
        page: 2,
        limit: 20
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      mockApiService.getContentLibrary.mockRejectedValue(new Error('Network error'));
      
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load content library/i)).toBeInTheDocument();
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
    });

    it('should retry failed operations', async () => {
      mockApiService.getContentLibrary.mockRejectedValueOnce(new Error('Network error'));
      mockApiService.getContentLibrary.mockResolvedValueOnce(mockContentLibrary);
      
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Retry'));
      
      await waitFor(() => {
        expect(screen.getByText('Sunset Mountain Vista')).toBeInTheDocument();
      });
    });

    it('should handle empty library state', async () => {
      mockApiService.getContentLibrary.mockResolvedValue([]);
      
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByText(/no content found/i)).toBeInTheDocument();
        expect(screen.getByText('Generate your first AI video')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByRole('main')).toBeInTheDocument();
        expect(screen.getByRole('search')).toBeInTheDocument();
        expect(screen.getByLabelText('Category Filter')).toBeInTheDocument();
      });
    });

    it('should support keyboard navigation', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText('Search content...');
        searchInput.focus();
        
        expect(document.activeElement).toBe(searchInput);
        
        // Tab to next element
        fireEvent.keyDown(searchInput, { key: 'Tab' });
        
        expect(document.activeElement).not.toBe(searchInput);
      });
    });

    it('should announce content updates to screen readers', async () => {
      render(<AIContentLibrary />);
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });
});