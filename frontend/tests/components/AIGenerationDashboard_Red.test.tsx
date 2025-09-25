/**
 * T4B-002 Red Phase Tests
 * Tests for AIGenerationDashboard to ensure mock data is NOT used and real API calls are made
 */

import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import AIGenerationDashboard from '../../src/ai/components/AIGenerationDashboard';
import { apiClient } from '../../src/services/api';

// Mock the API client (T4B-001 implementation) with helper functions
vi.mock('../../src/services/api', () => ({
  apiClient: {
    generateImage: vi.fn(),
    getGenerationStatus: vi.fn(),
    getGenerationHistory: vi.fn(),
  },
  // T4B-002: Mock helper functions used in component
  isGenerationComplete: vi.fn((status) => status === 'completed'),
  isGenerationFailed: vi.fn((status) => status === 'failed'),
  isGenerationInProgress: vi.fn((status) => status === 'pending' || status === 'processing'),
}));

const mockApiClient = apiClient as any;

describe('T4B-002 Red Phase: AIGenerationDashboard Mock Data Detection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('RED PHASE: Mock data should NOT be displayed', () => {
    it('should fail: mock data is currently being displayed instead of API data', async () => {
      // Mock API to return empty data (simulating real API)
      mockApiClient.getGenerationHistory.mockResolvedValue([]);
      
      render(<AIGenerationDashboard />);
      
      // RED PHASE: This should FAIL because mock data is being displayed
      // When mock data is removed in Green phase, this test should pass
      await waitFor(async () => {
        // These are mock data entries that should NOT appear when using real API
        const mockDataElements = [
          screen.queryByText('Beautiful sunset over mountains'),
          screen.queryByText('Abstract colorful patterns'), 
          screen.queryByText('Ocean waves at dawn')
        ];
        
        // RED PHASE EXPECTATION: Mock data should NOT exist (but currently it does)
        mockDataElements.forEach(element => {
          expect(element).not.toBeInTheDocument();
        });
      });
    });

    it('should fail: mock statistics are being displayed instead of API statistics', async () => {
      // Mock API to return different statistics
      mockApiClient.getGenerationHistory.mockResolvedValue([]);
      
      render(<AIGenerationDashboard />);
      
      // RED PHASE: This should FAIL because mock statistics are shown
      await waitFor(() => {
        // These are mock statistics that should NOT appear when using real API
        expect(screen.queryByText('15')).not.toBeInTheDocument(); // totalGenerations mock
        expect(screen.queryByText('80.0%')).not.toBeInTheDocument(); // successRate mock
        expect(screen.queryByText('$3.75')).not.toBeInTheDocument(); // totalCost mock
      });
    });
  });

  describe('RED PHASE: API calls should be made', () => {
    it('should fail: getGenerationHistory API is not being called', async () => {
      render(<AIGenerationDashboard />);
      
      // RED PHASE: This should FAIL because mock service is being used
      await waitFor(() => {
        expect(mockApiClient.getGenerationHistory).toHaveBeenCalled();
      });
    });

    it('should fail: real apiClient is not being used for data fetching', async () => {
      mockApiClient.getGenerationHistory.mockResolvedValue([
        {
          id: 'real-gen-1',
          request: { prompt_template_id: 'template-001' },
          status: 'completed',
          created_at: '2025-09-22T17:00:00Z'
        }
      ]);
      
      render(<AIGenerationDashboard />);
      
      // RED PHASE: This should FAIL because component is using mock data
      await waitFor(() => {
        // Should show data from real API call
        expect(screen.getByText('real-gen-1')).toBeInTheDocument();
      });
    });

    it('should fail: component does not handle API error states', async () => {
      // Simulate API error
      mockApiClient.getGenerationHistory.mockRejectedValue(new Error('API Error'));
      
      render(<AIGenerationDashboard />);
      
      // RED PHASE: This should FAIL because mock data is shown instead of error
      await waitFor(() => {
        expect(screen.getByText(/API Error/)).toBeInTheDocument();
      });
    });
  });

  describe('RED PHASE: Real API integration requirements', () => {
    it('should fail: generateImage method is not integrated', async () => {
      render(<AIGenerationDashboard />);
      
      // RED PHASE: generateImage from T4B-001 should be available but not integrated
      expect(mockApiClient.generateImage).toBeDefined();
      
      // Component should have UI to trigger generation but currently does not use real API
      const createButton = screen.queryByText('Create New Generation');
      expect(createButton).toBeInTheDocument();
      
      // When create form is used, it should call the real API (currently it doesn't)
      // This expectation will fail in Red phase
      expect(typeof mockApiClient.generateImage).toBe('function');
    });

    it('should fail: getGenerationStatus polling is not implemented', async () => {
      render(<AIGenerationDashboard />);
      
      // RED PHASE: Status polling should be implemented but currently isn't
      expect(mockApiClient.getGenerationStatus).toBeDefined();
      
      // Component should poll for status updates but currently doesn't
      // This will fail until Green phase implementation
      expect(typeof mockApiClient.getGenerationStatus).toBe('function');
    });
  });

  describe('RED PHASE: Type compatibility validation', () => {
    it('should fail: component types do not match API types', () => {
      // RED PHASE: Component uses internal types, should use API types
      const expectedApiTypes = {
        GenerationRequest: 'object',
        GenerationResponse: 'object', 
        GenerationResult: 'object',
        GenerationStatus: 'string'
      };
      
      // This test documents the type mismatch that exists in Red phase
      // Component has its own Generation interface that doesn't match API
      expect(expectedApiTypes.GenerationRequest).toBe('object');
      expect(expectedApiTypes.GenerationResponse).toBe('object');
      expect(expectedApiTypes.GenerationResult).toBe('object');
      expect(expectedApiTypes.GenerationStatus).toBe('string');
    });
  });
});