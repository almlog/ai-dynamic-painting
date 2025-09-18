/**
 * Tests for LearningAnalytics component
 * TDD: RED phase - tests written before component implementation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import LearningAnalytics from '../../src/ai/components/LearningAnalytics';

// Mock API functions
const mockApiService = {
  getLearningData: vi.fn(),
  getPreferenceInsights: vi.fn(),
  getUserInteractionPatterns: vi.fn(),
  getContentPerformanceMetrics: vi.fn(),
  getLearningRecommendations: vi.fn(),
  updatePreferences: vi.fn(),
  exportLearningData: vi.fn(),
  triggerLearningUpdate: vi.fn()
};

// Mock learning data
const mockLearningData = {
  userPreferences: {
    favoriteThemes: ['nature', 'abstract', 'urban'],
    preferredStyles: ['cinematic', 'dynamic', 'peaceful'],
    optimalTimingPatterns: {
      morning: { theme: 'nature', style: 'peaceful' },
      afternoon: { theme: 'urban', style: 'dynamic' },
      evening: { theme: 'abstract', style: 'cinematic' }
    },
    averageViewingDuration: 45,
    engagementScore: 85.5,
    lastUpdated: '2025-09-18T10:00:00Z'
  },
  contentPerformance: [
    {
      id: 'content_1',
      theme: 'nature',
      style: 'cinematic',
      viewCount: 25,
      averageViewTime: 42,
      userRating: 4.8,
      engagementMetrics: {
        skipRate: 0.12,
        replayRate: 0.35,
        shareRate: 0.08
      }
    },
    {
      id: 'content_2',
      theme: 'abstract',
      style: 'dynamic',
      viewCount: 18,
      averageViewTime: 38,
      userRating: 4.2,
      engagementMetrics: {
        skipRate: 0.25,
        replayRate: 0.22,
        shareRate: 0.03
      }
    }
  ],
  learningInsights: {
    strongPreferences: [
      'User shows strong preference for nature themes during morning hours',
      'Cinematic style consistently receives highest engagement',
      'Content duration sweet spot is 40-50 seconds'
    ],
    improvementAreas: [
      'Abstract content could benefit from more dynamic elements',
      'Evening content shows lower engagement - consider style adjustments'
    ],
    recommendations: [
      'Increase nature content generation during 6-10 AM',
      'Focus on cinematic style for high-engagement content',
      'Experiment with mixed themes during evening hours'
    ]
  },
  interactionPatterns: {
    hourlyActivity: {
      '06': 15, '07': 22, '08': 18, '09': 12, '10': 8,
      '11': 5, '12': 12, '13': 15, '14': 20, '15': 25,
      '16': 30, '17': 35, '18': 40, '19': 38, '20': 32,
      '21': 28, '22': 20, '23': 10
    },
    devicePreferences: {
      mobile: 0.45,
      desktop: 0.35,
      tablet: 0.20
    },
    sessionDuration: {
      average: 12.5,
      median: 8.0,
      longest: 45.0
    }
  }
};

const mockRecommendations = [
  {
    type: 'content_optimization',
    priority: 'high',
    title: 'Optimize Morning Content',
    description: 'Increase nature-themed content generation during morning hours (6-10 AM)',
    impact: 'Could improve engagement by 25%',
    actions: [
      'Adjust scheduling algorithm for nature themes',
      'Create morning-specific prompt templates',
      'Monitor morning engagement metrics'
    ]
  },
  {
    type: 'style_enhancement',
    priority: 'medium',
    title: 'Enhance Cinematic Style',
    description: 'Focus more on cinematic style elements for higher engagement',
    impact: 'Could improve user satisfaction by 15%',
    actions: [
      'Update prompt templates with cinematic keywords',
      'Analyze successful cinematic content patterns',
      'A/B test different cinematic approaches'
    ]
  }
];

describe('LearningAnalytics Component', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    
    // Setup default mock implementations
    mockApiService.getLearningData.mockResolvedValue(mockLearningData);
    mockApiService.getPreferenceInsights.mockResolvedValue(mockLearningData.userPreferences);
    mockApiService.getUserInteractionPatterns.mockResolvedValue(mockLearningData.interactionPatterns);
    mockApiService.getContentPerformanceMetrics.mockResolvedValue(mockLearningData.contentPerformance);
    mockApiService.getLearningRecommendations.mockResolvedValue(mockRecommendations);
    mockApiService.updatePreferences.mockResolvedValue({ success: true });
    mockApiService.exportLearningData.mockResolvedValue({ downloadUrl: 'http://example.com/export.json' });
    mockApiService.triggerLearningUpdate.mockResolvedValue({ status: 'started' });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render main dashboard header', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Learning Analytics Dashboard')).toBeInTheDocument();
        expect(screen.getByText(/analyze user preferences and content performance/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should render preference summary cards', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Favorite Themes')).toBeInTheDocument();
        expect(screen.getByText('nature, abstract, urban')).toBeInTheDocument();
        expect(screen.getByText('Preferred Styles')).toBeInTheDocument();
        expect(screen.getByText('cinematic, dynamic, peaceful')).toBeInTheDocument();
        expect(screen.getByText('Engagement Score')).toBeInTheDocument();
        expect(screen.getByText('85.5%')).toBeInTheDocument();
      });
    });

    it('should render content performance table', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Content Performance')).toBeInTheDocument();
        expect(screen.getByText('nature - cinematic')).toBeInTheDocument();
        expect(screen.getByText('abstract - dynamic')).toBeInTheDocument();
        expect(screen.getByText('25 views')).toBeInTheDocument();
        expect(screen.getByText('18 views')).toBeInTheDocument();
      });
    });

    it('should render learning insights section', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Learning Insights')).toBeInTheDocument();
        expect(screen.getByText('Strong Preferences')).toBeInTheDocument();
        expect(screen.getByText('Improvement Areas')).toBeInTheDocument();
        expect(screen.getByText(/nature themes during morning hours/i)).toBeInTheDocument();
      });
    });
  });

  describe('User Interaction Patterns', () => {
    it('should display hourly activity chart', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Hourly Activity Patterns')).toBeInTheDocument();
        expect(screen.getByText('Peak Activity: 18:00 (40 interactions)')).toBeInTheDocument();
      });
    });

    it('should show device preference breakdown', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Device Preferences')).toBeInTheDocument();
        expect(screen.getByText('Mobile: 45%')).toBeInTheDocument();
        expect(screen.getByText('Desktop: 35%')).toBeInTheDocument();
        expect(screen.getByText('Tablet: 20%')).toBeInTheDocument();
      });
    });

    it('should display session duration statistics', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Session Duration')).toBeInTheDocument();
        expect(screen.getByText('Average: 12.5 min')).toBeInTheDocument();
        expect(screen.getByText('Median: 8 min')).toBeInTheDocument();
        expect(screen.getByText('Longest: 45 min')).toBeInTheDocument();
      });
    });
  });

  describe('Learning Recommendations', () => {
    it('should display recommendation cards', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Learning Recommendations')).toBeInTheDocument();
        expect(screen.getByText('Optimize Morning Content')).toBeInTheDocument();
        expect(screen.getByText('Enhance Cinematic Style')).toBeInTheDocument();
        expect(screen.getByText('Could improve engagement by 25%')).toBeInTheDocument();
      });
    });

    it('should show recommendation priorities', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('high')).toBeInTheDocument();
        expect(screen.getByText('medium')).toBeInTheDocument();
      });
    });

    it('should display actionable steps for recommendations', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Adjust scheduling algorithm for nature themes')).toBeInTheDocument();
        expect(screen.getByText('Create morning-specific prompt templates')).toBeInTheDocument();
      });
    });
  });

  describe('Preference Management', () => {
    it('should allow editing theme preferences', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        const editButton = screen.getByText('Edit Preferences');
        fireEvent.click(editButton);
      });
      
      expect(screen.getByText('Edit User Preferences')).toBeInTheDocument();
      expect(screen.getByLabelText('Favorite Themes')).toBeInTheDocument();
    });

    it('should save preference changes', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Edit Preferences'));
      });
      
      const themeInput = screen.getByLabelText('Favorite Themes');
      fireEvent.change(themeInput, {
        target: { value: 'nature,urban,space' }
      });
      
      fireEvent.click(screen.getByText('Save Preferences'));
      
      await waitFor(() => {
        expect(mockApiService.updatePreferences).toHaveBeenCalledWith({
          favoriteThemes: ['nature', 'urban', 'space']
        });
      });
    });

    it('should handle preference update errors', async () => {
      mockApiService.updatePreferences.mockRejectedValue(new Error('Network error'));
      
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Edit Preferences'));
      });
      
      fireEvent.click(screen.getByText('Save Preferences'));
      
      await waitFor(() => {
        expect(screen.getByText('Error updating preferences: Network error')).toBeInTheDocument();
      });
    });
  });

  describe('Data Export and Actions', () => {
    it('should export learning data', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Export Data'));
      });
      
      await waitFor(() => {
        expect(mockApiService.exportLearningData).toHaveBeenCalled();
        expect(screen.getByText('Data exported successfully')).toBeInTheDocument();
      });
    });

    it('should trigger learning update', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Update Learning Model'));
      });
      
      await waitFor(() => {
        expect(mockApiService.triggerLearningUpdate).toHaveBeenCalled();
        expect(screen.getByText('Learning update started')).toBeInTheDocument();
      });
    });

    it('should refresh analytics data', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Refresh'));
      });
      
      await waitFor(() => {
        expect(mockApiService.getLearningData).toHaveBeenCalledTimes(2); // Initial load + refresh
      });
    });
  });

  describe('Time Range Filtering', () => {
    it('should filter data by time range', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.change(screen.getByLabelText('Time Range'), {
          target: { value: 'last_7_days' }
        });
      });
      
      await waitFor(() => {
        expect(mockApiService.getLearningData).toHaveBeenCalledWith({
          timeRange: 'last_7_days'
        });
      });
    });

    it('should support custom date range', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.change(screen.getByLabelText('Time Range'), {
          target: { value: 'custom' }
        });
      });
      
      expect(screen.getByLabelText('Start Date')).toBeInTheDocument();
      expect(screen.getByLabelText('End Date')).toBeInTheDocument();
      
      fireEvent.change(screen.getByLabelText('Start Date'), {
        target: { value: '2025-09-01' }
      });
      fireEvent.change(screen.getByLabelText('End Date'), {
        target: { value: '2025-09-15' }
      });
      
      fireEvent.click(screen.getByText('Apply Date Range'));
      
      await waitFor(() => {
        expect(mockApiService.getLearningData).toHaveBeenCalledWith({
          timeRange: 'custom',
          startDate: '2025-09-01',
          endDate: '2025-09-15'
        });
      });
    });
  });

  describe('Content Performance Analysis', () => {
    it('should sort content by performance metrics', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Sort by Rating'));
      });
      
      await waitFor(() => {
        const rows = screen.getAllByRole('row');
        // Check that highest rated content is first (excluding header row)
        expect(rows[1]).toHaveTextContent('nature - cinematic'); // 4.8 rating
      });
    });

    it('should filter content by theme', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.change(screen.getByLabelText('Filter by Theme'), {
          target: { value: 'nature' }
        });
      });
      
      await waitFor(() => {
        expect(screen.getByText('nature - cinematic')).toBeInTheDocument();
        expect(screen.queryByText('abstract - dynamic')).not.toBeInTheDocument();
      });
    });

    it('should show detailed performance metrics', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('View Details'));
      });
      
      expect(screen.getByText('Skip Rate: 12%')).toBeInTheDocument();
      expect(screen.getByText('Replay Rate: 35%')).toBeInTheDocument();
      expect(screen.getByText('Share Rate: 8%')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      mockApiService.getLearningData.mockRejectedValue(new Error('Network error'));
      
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load learning data/i)).toBeInTheDocument();
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
    });

    it('should retry failed API calls', async () => {
      mockApiService.getLearningData.mockRejectedValueOnce(new Error('Network error'));
      mockApiService.getLearningData.mockResolvedValueOnce(mockLearningData);
      
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Retry'));
      
      await waitFor(() => {
        expect(screen.getByText('Learning Analytics Dashboard')).toBeInTheDocument();
        expect(screen.getByText('85.5%')).toBeInTheDocument();
      });
    });

    it('should handle empty learning data', async () => {
      mockApiService.getLearningData.mockResolvedValue({
        userPreferences: null,
        contentPerformance: [],
        learningInsights: { strongPreferences: [], improvementAreas: [], recommendations: [] },
        interactionPatterns: null
      });
      
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText(/no learning data available/i)).toBeInTheDocument();
        expect(screen.getByText('Start collecting data')).toBeInTheDocument();
      });
    });
  });

  describe('Real-time Updates', () => {
    it('should update learning data in real-time', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByText('85.5%')).toBeInTheDocument();
      });
      
      // Simulate real-time update
      const updatedData = {
        ...mockLearningData,
        userPreferences: {
          ...mockLearningData.userPreferences,
          engagementScore: 87.2
        }
      };
      
      mockApiService.getLearningData.mockResolvedValue(updatedData);
      
      // Simulate periodic refresh
      fireEvent.click(screen.getByText('Refresh'));
      
      await waitFor(() => {
        expect(screen.getByText('87.2%')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', async () => {
      render(<LearningAnalytics />);
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByLabelText('Filter by Theme')).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      render(<LearningAnalytics />);
      
      const refreshButton = screen.getByText('Refresh');
      refreshButton.focus();
      
      expect(document.activeElement).toBe(refreshButton);
      
      // Tab to next element
      fireEvent.keyDown(refreshButton, { key: 'Tab' });
      
      expect(document.activeElement).not.toBe(refreshButton);
    });

    it('should announce data updates to screen readers', async () => {
      render(<LearningAnalytics />);
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });
});