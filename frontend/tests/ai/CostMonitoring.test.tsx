/**
 * Tests for CostMonitoring component
 * TDD: RED phase - tests written before component implementation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import CostMonitoring from '../../src/ai/components/CostMonitoring';

// Mock API functions
const mockApiService = {
  getCostData: vi.fn(),
  getCostBreakdown: vi.fn(),
  getBudgetSettings: vi.fn(),
  updateBudgetSettings: vi.fn(),
  getCostProjections: vi.fn(),
  exportCostReport: vi.fn(),
  getCostAlerts: vi.fn(),
  dismissAlert: vi.fn(),
  createBudgetAlert: vi.fn()
};

// Mock cost data
const mockCostData = {
  totalCost: 24.75,
  currentMonth: 18.50,
  previousMonth: 12.25,
  dailyAverage: 0.62,
  costBreakdown: {
    videoGeneration: 16.80,
    apiCalls: 4.20,
    storage: 2.15,
    processing: 1.60
  },
  monthlyTrend: [
    { month: 'Jul', cost: 8.50 },
    { month: 'Aug', cost: 12.25 },
    { month: 'Sep', cost: 18.50 }
  ],
  dailyCosts: [
    { date: '2025-09-16', cost: 0.85 },
    { date: '2025-09-17', cost: 1.20 },
    { date: '2025-09-18', cost: 0.45 }
  ],
  usage: {
    generationsThisMonth: 24,
    totalGenerations: 68,
    averageCostPerGeneration: 0.77,
    peakUsageDay: 'Monday',
    peakUsageCost: 2.15
  }
};

const mockBudgetSettings = {
  monthlyBudget: 25.00,
  dailyBudget: 1.00,
  alertThresholds: {
    warning: 0.75,
    critical: 0.90
  },
  autoStopEnabled: true,
  autoStopThreshold: 0.95,
  notifications: {
    email: true,
    dashboard: true,
    webhook: false
  }
};

const mockCostProjections = {
  endOfMonth: 26.75,
  confidence: 0.85,
  factors: [
    'Current usage trend indicates 15% increase',
    'Weekend usage typically 40% lower',
    'Seasonal pattern suggests stable consumption'
  ],
  recommendations: [
    'Consider increasing monthly budget by $5',
    'Review generation quality settings to optimize cost',
    'Schedule more generations during off-peak hours'
  ]
};

const mockCostAlerts = [
  {
    id: 'alert_1',
    type: 'warning',
    title: 'Monthly Budget at 75%',
    message: 'You have used $18.50 of your $25.00 monthly budget',
    timestamp: '2025-09-18T10:30:00Z',
    dismissed: false
  },
  {
    id: 'alert_2',
    type: 'info',
    title: 'High Usage Day',
    message: 'Today\'s usage ($2.15) is above average ($0.62)',
    timestamp: '2025-09-18T14:15:00Z',
    dismissed: false
  }
];

describe('CostMonitoring Component', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    
    // Setup default mock implementations
    mockApiService.getCostData.mockResolvedValue(mockCostData);
    mockApiService.getCostBreakdown.mockResolvedValue(mockCostData.costBreakdown);
    mockApiService.getBudgetSettings.mockResolvedValue(mockBudgetSettings);
    mockApiService.updateBudgetSettings.mockResolvedValue({ success: true });
    mockApiService.getCostProjections.mockResolvedValue(mockCostProjections);
    mockApiService.exportCostReport.mockResolvedValue({ downloadUrl: 'http://example.com/report.pdf' });
    mockApiService.getCostAlerts.mockResolvedValue(mockCostAlerts);
    mockApiService.dismissAlert.mockResolvedValue({ success: true });
    mockApiService.createBudgetAlert.mockResolvedValue({ id: 'new_alert', success: true });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render main cost monitoring header', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Cost Monitoring Dashboard')).toBeInTheDocument();
        expect(screen.getByText(/track and manage ai generation costs/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should render cost summary cards', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Total Cost')).toBeInTheDocument();
        expect(screen.getByText('$24.75')).toBeInTheDocument();
        expect(screen.getByText('This Month')).toBeInTheDocument();
        expect(screen.getByText('$18.50')).toBeInTheDocument();
        expect(screen.getByText('Daily Average')).toBeInTheDocument();
        expect(screen.getByText('$0.62')).toBeInTheDocument();
      });
    });

    it('should render cost breakdown chart', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Cost Breakdown')).toBeInTheDocument();
        expect(screen.getByText('Video Generation: $16.80')).toBeInTheDocument();
        expect(screen.getByText('API Calls: $4.20')).toBeInTheDocument();
        expect(screen.getByText('Storage: $2.15')).toBeInTheDocument();
        expect(screen.getByText('Processing: $1.60')).toBeInTheDocument();
      });
    });

    it('should render monthly trend chart', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Monthly Trend')).toBeInTheDocument();
        expect(screen.getByText('Jul: $8.50')).toBeInTheDocument();
        expect(screen.getByText('Aug: $12.25')).toBeInTheDocument();
        expect(screen.getByText('Sep: $18.50')).toBeInTheDocument();
      });
    });
  });

  describe('Budget Management', () => {
    it('should display current budget settings', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Budget Settings')).toBeInTheDocument();
        expect(screen.getByText('Monthly Budget: $25.00')).toBeInTheDocument();
        expect(screen.getByText('Daily Budget: $1.00')).toBeInTheDocument();
        expect(screen.getByText('Auto-stop at 95%')).toBeInTheDocument();
      });
    });

    it('should show budget utilization progress', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Budget Utilization')).toBeInTheDocument();
        expect(screen.getByText('74%')).toBeInTheDocument(); // 18.50/25.00 = 0.74
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
      });
    });

    it('should allow editing budget settings', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Edit Budget'));
      });
      
      expect(screen.getByText('Edit Budget Settings')).toBeInTheDocument();
      expect(screen.getByLabelText('Monthly Budget')).toBeInTheDocument();
      expect(screen.getByLabelText('Daily Budget')).toBeInTheDocument();
    });

    it('should save budget changes', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Edit Budget'));
      });
      
      const monthlyInput = screen.getByLabelText('Monthly Budget');
      fireEvent.change(monthlyInput, {
        target: { value: '30.00' }
      });
      
      fireEvent.click(screen.getByText('Save Budget'));
      
      await waitFor(() => {
        expect(mockApiService.updateBudgetSettings).toHaveBeenCalledWith({
          monthlyBudget: 30.00
        });
      });
    });
  });

  describe('Cost Alerts', () => {
    it('should display active cost alerts', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Cost Alerts')).toBeInTheDocument();
        expect(screen.getByText('Monthly Budget at 75%')).toBeInTheDocument();
        expect(screen.getByText('High Usage Day')).toBeInTheDocument();
      });
    });

    it('should show alert types with proper styling', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('warning')).toBeInTheDocument();
        expect(screen.getByText('info')).toBeInTheDocument();
      });
    });

    it('should dismiss individual alerts', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        const dismissButtons = screen.getAllByText('Dismiss');
        fireEvent.click(dismissButtons[0]);
      });
      
      await waitFor(() => {
        expect(mockApiService.dismissAlert).toHaveBeenCalledWith('alert_1');
      });
    });

    it('should create new budget alerts', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Create Alert'));
      });
      
      expect(screen.getByText('Create Budget Alert')).toBeInTheDocument();
      expect(screen.getByLabelText('Alert Type')).toBeInTheDocument();
      expect(screen.getByLabelText('Threshold')).toBeInTheDocument();
      
      fireEvent.change(screen.getByLabelText('Threshold'), {
        target: { value: '0.85' }
      });
      
      fireEvent.click(screen.getByText('Create Alert'));
      
      await waitFor(() => {
        expect(mockApiService.createBudgetAlert).toHaveBeenCalledWith({
          threshold: 0.85
        });
      });
    });
  });

  describe('Cost Projections', () => {
    it('should display end-of-month projections', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Cost Projections')).toBeInTheDocument();
        expect(screen.getByText('End of Month: $26.75')).toBeInTheDocument();
        expect(screen.getByText('Confidence: 85%')).toBeInTheDocument();
      });
    });

    it('should show projection factors', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Projection Factors')).toBeInTheDocument();
        expect(screen.getByText(/current usage trend indicates 15% increase/i)).toBeInTheDocument();
        expect(screen.getByText(/weekend usage typically 40% lower/i)).toBeInTheDocument();
      });
    });

    it('should display cost optimization recommendations', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Recommendations')).toBeInTheDocument();
        expect(screen.getByText(/consider increasing monthly budget by \$5/i)).toBeInTheDocument();
        expect(screen.getByText(/review generation quality settings/i)).toBeInTheDocument();
      });
    });
  });

  describe('Usage Analytics', () => {
    it('should display usage statistics', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Usage Statistics')).toBeInTheDocument();
        expect(screen.getByText('24 generations this month')).toBeInTheDocument();
        expect(screen.getByText('68 total generations')).toBeInTheDocument();
        expect(screen.getByText('$0.77 average per generation')).toBeInTheDocument();
      });
    });

    it('should show peak usage information', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Peak Usage')).toBeInTheDocument();
        expect(screen.getByText('Monday: $2.15')).toBeInTheDocument();
      });
    });

    it('should display daily cost history', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Daily History'));
      });
      
      expect(screen.getByText('2025-09-16: $0.85')).toBeInTheDocument();
      expect(screen.getByText('2025-09-17: $1.20')).toBeInTheDocument();
      expect(screen.getByText('2025-09-18: $0.45')).toBeInTheDocument();
    });
  });

  describe('Reporting and Export', () => {
    it('should export cost reports', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Export Report'));
      });
      
      await waitFor(() => {
        expect(mockApiService.exportCostReport).toHaveBeenCalled();
        expect(screen.getByText('Report exported successfully')).toBeInTheDocument();
      });
    });

    it('should support different report formats', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Export Options'));
      });
      
      expect(screen.getByText('PDF Report')).toBeInTheDocument();
      expect(screen.getByText('CSV Data')).toBeInTheDocument();
      expect(screen.getByText('JSON Export')).toBeInTheDocument();
    });

    it('should filter reports by date range', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        fireEvent.change(screen.getByLabelText('Report Period'), {
          target: { value: 'last_7_days' }
        });
      });
      
      expect(screen.getByDisplayValue('last_7_days')).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Generate Report'));
      
      await waitFor(() => {
        expect(mockApiService.exportCostReport).toHaveBeenCalledWith({
          period: 'last_7_days'
        });
      });
    });
  });

  describe('Real-time Monitoring', () => {
    it('should refresh cost data automatically', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(mockApiService.getCostData).toHaveBeenCalledTimes(1);
      });
      
      // Simulate auto-refresh after 30 seconds
      fireEvent.click(screen.getByText('Refresh'));
      
      await waitFor(() => {
        expect(mockApiService.getCostData).toHaveBeenCalledTimes(2);
      });
    });

    it('should display last updated timestamp', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText(/last updated/i)).toBeInTheDocument();
      });
    });

    it('should show live cost tracking indicator', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Live Tracking')).toBeInTheDocument();
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      mockApiService.getCostData.mockRejectedValue(new Error('Network error'));
      
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load cost data/i)).toBeInTheDocument();
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
    });

    it('should retry failed API calls', async () => {
      mockApiService.getCostData.mockRejectedValueOnce(new Error('Network error'));
      mockApiService.getCostData.mockResolvedValueOnce(mockCostData);
      
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Retry'));
      
      await waitFor(() => {
        expect(screen.getByText('$24.75')).toBeInTheDocument();
      });
    });

    it('should handle missing cost data', async () => {
      mockApiService.getCostData.mockResolvedValue({
        totalCost: 0,
        currentMonth: 0,
        costBreakdown: {},
        usage: null
      });
      
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText(/no cost data available/i)).toBeInTheDocument();
        expect(screen.getByText('Start monitoring costs')).toBeInTheDocument();
      });
    });
  });

  describe('Budget Threshold Warnings', () => {
    it('should show warning when approaching budget limit', async () => {
      const highCostData = {
        ...mockCostData,
        currentMonth: 22.50 // 90% of 25.00 budget
      };
      mockApiService.getCostData.mockResolvedValue(highCostData);
      
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText(/approaching budget limit/i)).toBeInTheDocument();
        expect(screen.getByText('90%')).toBeInTheDocument();
      });
    });

    it('should show critical alert when exceeding budget', async () => {
      const overBudgetData = {
        ...mockCostData,
        currentMonth: 26.50 // 106% of 25.00 budget
      };
      mockApiService.getCostData.mockResolvedValue(overBudgetData);
      
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText(/budget exceeded/i)).toBeInTheDocument();
        expect(screen.getByText('106%')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByRole('main')).toBeInTheDocument();
        expect(screen.getByLabelText('Monthly Budget')).toBeInTheDocument();
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
      });
    });

    it('should support keyboard navigation', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        const refreshButton = screen.getByText('Refresh');
        refreshButton.focus();
        
        expect(document.activeElement).toBe(refreshButton);
        
        // Tab to next element
        fireEvent.keyDown(refreshButton, { key: 'Tab' });
        
        expect(document.activeElement).not.toBe(refreshButton);
      });
    });

    it('should announce budget status to screen readers', async () => {
      render(<CostMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });
});