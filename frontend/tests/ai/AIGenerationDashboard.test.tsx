/**
 * Tests for AIGenerationDashboard component
 * TDD: RED phase - tests written before component implementation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import AIGenerationDashboard from '../../src/ai/components/AIGenerationDashboard';

// Mock API functions
const mockApiService = {
  getGenerationHistory: vi.fn(),
  createGeneration: vi.fn(),
  getGenerationStatus: vi.fn(),
  deleteGeneration: vi.fn(),
  getGenerationStatistics: vi.fn()
};

// Mock WebSocket for real-time updates
const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
};

// Mock generation data
const mockGenerations = [
  {
    id: 'gen_1',
    prompt: 'Beautiful sunset over mountains',
    status: 'completed',
    createdAt: '2025-09-18T10:00:00Z',
    duration: 30,
    quality: 'high',
    downloadUrl: 'https://storage.example.com/video1.mp4',
    cost: 0.25,
    metadata: {
      theme: 'nature',
      style: 'cinematic'
    }
  },
  {
    id: 'gen_2', 
    prompt: 'Abstract colorful patterns',
    status: 'processing',
    createdAt: '2025-09-18T11:00:00Z',
    duration: 45,
    quality: 'medium',
    progress: 65,
    cost: 0.15,
    metadata: {
      theme: 'abstract',
      style: 'dynamic'
    }
  },
  {
    id: 'gen_3',
    prompt: 'Ocean waves at dawn',
    status: 'failed',
    createdAt: '2025-09-18T09:00:00Z',
    duration: 20,
    quality: 'high',
    error: 'API quota exceeded',
    cost: 0.0,
    metadata: {
      theme: 'nature',
      style: 'peaceful'
    }
  }
];

const mockStatistics = {
  totalGenerations: 15,
  successfulGenerations: 12,
  failedGenerations: 3,
  totalCost: 3.75,
  averageCost: 0.25,
  popularThemes: ['nature', 'abstract', 'urban'],
  popularStyles: ['cinematic', 'dynamic', 'peaceful'],
  successRate: 80.0
};

// Note: React hooks should not be mocked for component testing
// We'll use the actual React hooks for proper component behavior

// Create a mock module for the API service that doesn't exist yet
const createMockApiService = () => mockApiService;

describe('AIGenerationDashboard Component', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    
    // Setup default mock implementations
    mockApiService.getGenerationHistory.mockResolvedValue(mockGenerations);
    mockApiService.getGenerationStatistics.mockResolvedValue(mockStatistics);
    mockApiService.createGeneration.mockResolvedValue({ id: 'gen_new', status: 'started' });
    mockApiService.getGenerationStatus.mockResolvedValue({ status: 'processing', progress: 50 });
    mockApiService.deleteGeneration.mockResolvedValue({ success: true });
    
    // Mock WebSocket
    global.WebSocket = vi.fn(() => mockWebSocket);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render dashboard header with title', async () => {
      render(<AIGenerationDashboard />);
      
      expect(screen.getByText('AI Generation Dashboard')).toBeInTheDocument();
      expect(screen.getByText(/manage your ai video generations/i)).toBeInTheDocument();
    });

    it('should render statistics summary cards', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Total Generations')).toBeInTheDocument();
        expect(screen.getByText('15')).toBeInTheDocument();
        expect(screen.getByText('Success Rate')).toBeInTheDocument();
        expect(screen.getByText('80.0%')).toBeInTheDocument();
        expect(screen.getByText('Total Cost')).toBeInTheDocument();
        expect(screen.getByText('$3.75')).toBeInTheDocument();
      });
    });

    it('should render generation history table', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Generation History')).toBeInTheDocument();
        expect(screen.getByText('Beautiful sunset over mountains')).toBeInTheDocument();
        expect(screen.getByText('Abstract colorful patterns')).toBeInTheDocument();
        expect(screen.getByText('Ocean waves at dawn')).toBeInTheDocument();
      });
    });

    it('should display generation status badges correctly', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('completed')).toBeInTheDocument();
        expect(screen.getByText('processing')).toBeInTheDocument();
        expect(screen.getByText('failed')).toBeInTheDocument();
      });
    });
  });

  describe('Generation Management', () => {
    it('should show new generation form when create button clicked', async () => {
      render(<AIGenerationDashboard />);
      
      const createButton = screen.getByText('Create New Generation');
      fireEvent.click(createButton);
      
      expect(screen.getByText('Create AI Generation')).toBeInTheDocument();
      expect(screen.getByLabelText('Prompt')).toBeInTheDocument();
      expect(screen.getByLabelText('Duration (seconds)')).toBeInTheDocument();
      expect(screen.getByLabelText('Quality')).toBeInTheDocument();
    });

    it('should submit new generation with correct data', async () => {
      render(<AIGenerationDashboard />);
      
      // Open create form
      fireEvent.click(screen.getByText('Create New Generation'));
      
      // Fill form
      fireEvent.change(screen.getByLabelText('Prompt'), {
        target: { value: 'Test prompt for new generation' }
      });
      fireEvent.change(screen.getByLabelText('Duration (seconds)'), {
        target: { value: '30' }
      });
      fireEvent.change(screen.getByLabelText('Quality'), {
        target: { value: 'high' }
      });
      
      // Submit form
      fireEvent.click(screen.getByText('Start Generation'));
      
      await waitFor(() => {
        expect(mockApiService.createGeneration).toHaveBeenCalledWith({
          prompt: 'Test prompt for new generation',
          duration: 30,
          quality: 'high'
        });
      });
    });

    it('should handle generation creation errors', async () => {
      mockApiService.createGeneration.mockRejectedValue(new Error('API quota exceeded'));
      
      render(<AIGenerationDashboard />);
      
      fireEvent.click(screen.getByText('Create New Generation'));
      fireEvent.change(screen.getByLabelText('Prompt'), {
        target: { value: 'Test prompt' }
      });
      fireEvent.click(screen.getByText('Start Generation'));
      
      await waitFor(() => {
        expect(screen.getByText('Error: API quota exceeded')).toBeInTheDocument();
      });
    });
  });

  describe('Generation Actions', () => {
    it('should show download button for completed generations', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        const downloadButtons = screen.getAllByText('Download');
        expect(downloadButtons).toHaveLength(1); // Only completed generation
      });
    });

    it('should show progress bar for processing generations', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('65%')).toBeInTheDocument();
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
      });
    });

    it('should show retry button for failed generations', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
        expect(screen.getByText('API quota exceeded')).toBeInTheDocument();
      });
    });

    it('should delete generation when delete button clicked', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        const deleteButtons = screen.getAllByText('Delete');
        fireEvent.click(deleteButtons[0]);
      });
      
      // Confirm deletion
      fireEvent.click(screen.getByText('Confirm Delete'));
      
      await waitFor(() => {
        expect(mockApiService.deleteGeneration).toHaveBeenCalledWith('gen_1');
      });
    });
  });

  describe('Real-time Updates', () => {
    it('should establish WebSocket connection on mount', () => {
      render(<AIGenerationDashboard />);
      
      expect(global.WebSocket).toHaveBeenCalledWith(
        expect.stringContaining('/ws/generations')
      );
    });

    it('should update generation status from WebSocket messages', async () => {
      render(<AIGenerationDashboard />);
      
      // Simulate WebSocket message
      const messageHandler = mockWebSocket.addEventListener.mock.calls
        .find(call => call[0] === 'message')[1];
      
      messageHandler({
        data: JSON.stringify({
          type: 'generation_update',
          generationId: 'gen_2',
          status: 'completed',
          progress: 100,
          downloadUrl: 'https://storage.example.com/video2.mp4'
        })
      });
      
      await waitFor(() => {
        expect(screen.getByText('completed')).toBeInTheDocument();
      });
    });

    it('should handle WebSocket connection errors', async () => {
      render(<AIGenerationDashboard />);
      
      // Simulate WebSocket error
      const errorHandler = mockWebSocket.addEventListener.mock.calls
        .find(call => call[0] === 'error')[1];
      
      errorHandler(new Error('WebSocket connection failed'));
      
      await waitFor(() => {
        expect(screen.getByText(/connection error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Filtering and Sorting', () => {
    it('should filter generations by status', async () => {
      render(<AIGenerationDashboard />);
      
      // Select status filter
      fireEvent.change(screen.getByLabelText('Filter by Status'), {
        target: { value: 'completed' }
      });
      
      await waitFor(() => {
        expect(screen.getByText('Beautiful sunset over mountains')).toBeInTheDocument();
        expect(screen.queryByText('Abstract colorful patterns')).not.toBeInTheDocument();
      });
    });

    it('should sort generations by creation date', async () => {
      render(<AIGenerationDashboard />);
      
      // Click sort by date
      fireEvent.click(screen.getByText('Sort by Date'));
      
      await waitFor(() => {
        const rows = screen.getAllByRole('row');
        // Check that most recent is first (excluding header row)
        expect(rows[1]).toHaveTextContent('Abstract colorful patterns');
      });
    });

    it('should search generations by prompt text', async () => {
      render(<AIGenerationDashboard />);
      
      // Enter search query
      fireEvent.change(screen.getByPlaceholderText('Search generations...'), {
        target: { value: 'sunset' }
      });
      
      await waitFor(() => {
        expect(screen.getByText('Beautiful sunset over mountains')).toBeInTheDocument();
        expect(screen.queryByText('Abstract colorful patterns')).not.toBeInTheDocument();
      });
    });
  });

  describe('Cost Monitoring', () => {
    it('should display total cost information', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Total Cost: $3.75')).toBeInTheDocument();
        expect(screen.getByText('Average Cost: $0.25')).toBeInTheDocument();
      });
    });

    it('should show cost breakdown by generation', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('$0.25')).toBeInTheDocument(); // gen_1 cost
        expect(screen.getByText('$0.15')).toBeInTheDocument(); // gen_2 cost
        expect(screen.getByText('$0.00')).toBeInTheDocument(); // gen_3 cost (failed)
      });
    });

    it('should warn when approaching cost limits', async () => {
      const highCostStats = { ...mockStatistics, totalCost: 9.50 };
      mockApiService.getGenerationStatistics.mockResolvedValue(highCostStats);
      
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText(/approaching cost limit/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      mockApiService.getGenerationHistory.mockRejectedValue(new Error('Network error'));
      
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load generations/i)).toBeInTheDocument();
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
    });

    it('should retry failed API calls', async () => {
      mockApiService.getGenerationHistory.mockRejectedValueOnce(new Error('Network error'));
      mockApiService.getGenerationHistory.mockResolvedValueOnce(mockGenerations);
      
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Retry'));
      
      await waitFor(() => {
        expect(screen.getByText('Beautiful sunset over mountains')).toBeInTheDocument();
      });
    });

    it('should handle empty generation history', async () => {
      mockApiService.getGenerationHistory.mockResolvedValue([]);
      
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText(/no generations found/i)).toBeInTheDocument();
        expect(screen.getByText('Create your first AI generation')).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    it('should not re-fetch data unnecessarily', async () => {
      const { rerender } = render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(mockApiService.getGenerationHistory).toHaveBeenCalledTimes(1);
      });
      
      // Re-render component
      rerender(<AIGenerationDashboard />);
      
      // Should not fetch again
      expect(mockApiService.getGenerationHistory).toHaveBeenCalledTimes(1);
    });

    it('should debounce search input', async () => {
      render(<AIGenerationDashboard />);
      
      const searchInput = screen.getByPlaceholderText('Search generations...');
      
      // Type rapidly
      fireEvent.change(searchInput, { target: { value: 's' } });
      fireEvent.change(searchInput, { target: { value: 'su' } });
      fireEvent.change(searchInput, { target: { value: 'sun' } });
      
      // Should debounce and only filter once
      await waitFor(() => {
        expect(screen.getByText('Beautiful sunset over mountains')).toBeInTheDocument();
      }, { timeout: 1000 });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', async () => {
      render(<AIGenerationDashboard />);
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByLabelText('Generation status filter')).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      render(<AIGenerationDashboard />);
      
      const createButton = screen.getByText('Create New Generation');
      createButton.focus();
      
      expect(document.activeElement).toBe(createButton);
      
      // Tab to next element
      fireEvent.keyDown(createButton, { key: 'Tab' });
      
      expect(document.activeElement).not.toBe(createButton);
    });

    it('should announce status changes to screen readers', async () => {
      render(<AIGenerationDashboard />);
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });
});