/**
 * T4B-003 Red Phase Tests
 * Tests for AIGenerationDashboard UI→API integration functionality
 * Verify that UI parameter input correctly triggers real API calls
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import userEvent from '@testing-library/user-event';
import AIGenerationDashboard from '../../src/ai/components/AIGenerationDashboard';
import { apiClient } from '../../src/services/api';

// Mock the API client for T4B-003 UI→API integration testing
vi.mock('../../src/services/api', () => ({
  apiClient: {
    generateImage: vi.fn(),
    getGenerationStatus: vi.fn(),
    getGenerationHistory: vi.fn(),
  },
  isGenerationComplete: vi.fn((status) => status === 'completed'),
  isGenerationFailed: vi.fn((status) => status === 'failed'),
  isGenerationInProgress: vi.fn((status) => status === 'pending' || status === 'processing'),
}));

const mockApiClient = apiClient as any;

// Mock generation data for consistent test results
const mockGenerations = [
  {
    id: 'gen_1',
    prompt: 'Beautiful sunset over mountains',
    status: 'completed',
    created_at: '2025-09-18T10:00:00Z',
    createdAt: '2025-09-18T10:00:00Z',
    duration: 30,
    quality: 'hd',
    downloadUrl: 'https://storage.example.com/video1.mp4',
    image_path: 'https://storage.example.com/video1.mp4',
    cost: 0.25,
    request: {
      variables: { prompt: 'Beautiful sunset over mountains' },
      quality: 'hd',
      aspect_ratio: '16:9',
      style_preset: 'photographic'
    },
    metadata: {
      theme: 'nature',
      style: 'cinematic',
      generation_time: 30
    }
  }
];

describe('T4B-003 Red Phase: UI→API Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock console.error to suppress error messages in tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
    
    // Setup default mock responses with data to load dashboard properly
    mockApiClient.getGenerationHistory.mockResolvedValue(mockGenerations);
    mockApiClient.generateImage.mockResolvedValue({
      generation_id: 'test-gen-123',
      status: 'pending'
    });
  });

  describe('RED PHASE: UI parameter input should trigger API calls', () => {
    it('should fail: Create Generation button does not trigger generateImage API call', async () => {
      const user = userEvent.setup();
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Open create form
      await user.click(screen.getByText('Create New Generation'));
      
      // Fill form with test parameters
      const promptInput = screen.getByLabelText('Prompt');
      await user.type(promptInput, 'Test prompt for API integration');
      
      // Submit form
      const startButton = screen.getByText('Start Generation');
      await user.click(startButton);
      
      // RED PHASE: This should FAIL because generateImage API is not being called
      // In Green phase, this should pass when UI properly calls the API
      await waitFor(() => {
        expect(mockApiClient.generateImage).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: expect.objectContaining({
              prompt: 'Test prompt for API integration'
            })
          })
        );
      });
    });

    it('should fail: UI parameters are not correctly passed to API request', async () => {
      const user = userEvent.setup();
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Open create form
      await user.click(screen.getByText('Create New Generation'));
      
      // Fill form with specific parameters
      await user.type(screen.getByLabelText('Prompt'), 'Specific test prompt');
      
      // Change quality setting
      const qualitySelect = screen.getByLabelText('Quality');
      await user.selectOptions(qualitySelect, 'hd');
      
      // Change aspect ratio
      const aspectRatioSelect = screen.getByLabelText('Aspect Ratio');
      await user.selectOptions(aspectRatioSelect, '16:9');
      
      // Submit form
      await user.click(screen.getByText('Start Generation'));
      
      // RED PHASE: This should FAIL because parameters are not correctly passed
      await waitFor(() => {
        expect(mockApiClient.generateImage).toHaveBeenCalledWith({
          prompt_template_id: 'default',
          model: 'gemini-1.5-flash',
          quality: 'hd',
          aspect_ratio: '16:9',
          temperature: 0.7,
          top_k: 40,
          top_p: 0.95,
          max_tokens: 2048,
          variables: { prompt: 'Specific test prompt' }
        });
      });
    });

    it('should fail: API response is not handled in UI', async () => {
      const user = userEvent.setup();
      
      // Mock successful API response
      mockApiClient.generateImage.mockResolvedValue({
        generation_id: 'test-gen-456',
        status: 'pending'
      });
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Open create form and submit
      await user.click(screen.getByText('Create New Generation'));
      await user.type(screen.getByLabelText('Prompt'), 'Test prompt');
      await user.click(screen.getByText('Start Generation'));
      
      // RED PHASE: This should FAIL because UI doesn't handle API response
      // Form should close and data should refresh after successful API call
      await waitFor(() => {
        expect(screen.queryByText('Create AI Generation')).not.toBeInTheDocument();
      });
      
      // Should refresh data after successful generation
      expect(mockApiClient.getGenerationHistory).toHaveBeenCalledTimes(2); // Initial + after creation
    });

    it('should fail: API errors are not displayed in UI', async () => {
      const user = userEvent.setup();
      
      // Mock API error
      mockApiClient.generateImage.mockRejectedValue(new Error('API quota exceeded'));
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Open create form and submit
      await user.click(screen.getByText('Create New Generation'));
      await user.type(screen.getByLabelText('Prompt'), 'Test prompt');
      await user.click(screen.getByText('Start Generation'));
      
      // RED PHASE: This should FAIL because API errors are not shown in UI
      await waitFor(() => {
        expect(screen.getByText('Error: API quota exceeded')).toBeInTheDocument();
      });
    });
  });

  describe('RED PHASE: Form validation and UX', () => {
    it('should fail: Empty prompt submission should be prevented', async () => {
      const user = userEvent.setup();
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Open create form
      await user.click(screen.getByText('Create New Generation'));
      
      // Try to submit with empty prompt
      const startButton = screen.getByText('Start Generation');
      
      // RED PHASE: This should FAIL if empty prompt is allowed
      expect(startButton).toBeDisabled();
      
      // API should not be called with empty prompt
      await user.click(startButton);
      expect(mockApiClient.generateImage).not.toHaveBeenCalled();
    });

    it('should fail: Form should reset after successful submission', async () => {
      const user = userEvent.setup();
      
      mockApiClient.generateImage.mockResolvedValue({
        generation_id: 'test-gen-789',
        status: 'pending'
      });
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Open create form and fill
      await user.click(screen.getByText('Create New Generation'));
      const promptInput = screen.getByLabelText('Prompt');
      await user.type(promptInput, 'Test prompt for reset');
      
      // Submit form
      await user.click(screen.getByText('Start Generation'));
      
      // Wait for form to close
      await waitFor(() => {
        expect(screen.queryByText('Create AI Generation')).not.toBeInTheDocument();
      });
      
      // Open form again - should be reset
      await user.click(screen.getByText('Create New Generation'));
      
      // RED PHASE: This should FAIL if form is not reset
      const newPromptInput = screen.getByLabelText('Prompt');
      expect(newPromptInput).toHaveValue('');
    });
  });

  describe('RED PHASE: Real-time UI updates', () => {
    it('should fail: Loading state is not shown during API call', async () => {
      const user = userEvent.setup();
      
      // Mock slow API response
      let resolveGeneration: (value: any) => void;
      const slowApiCall = new Promise(resolve => {
        resolveGeneration = resolve;
      });
      mockApiClient.generateImage.mockReturnValue(slowApiCall);
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Open create form and submit
      await user.click(screen.getByText('Create New Generation'));
      await user.type(screen.getByLabelText('Prompt'), 'Test prompt');
      await user.click(screen.getByText('Start Generation'));
      
      // RED PHASE: This should FAIL if loading state is not shown
      await waitFor(() => {
        expect(screen.getByText('Generating...')).toBeInTheDocument();
      });
      
      // Complete the API call
      resolveGeneration!({ generation_id: 'test-gen-loading', status: 'pending' });
    });

    it('should fail: Generation history is not refreshed after new creation', async () => {
      const user = userEvent.setup();
      
      mockApiClient.generateImage.mockResolvedValue({
        generation_id: 'test-gen-refresh',
        status: 'pending'
      });
      
      await act(async () => {
        render(<AIGenerationDashboard />);
      });
      
      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText('Create New Generation')).toBeInTheDocument();
      });
      
      // Initial load
      expect(mockApiClient.getGenerationHistory).toHaveBeenCalledTimes(1);
      
      // Create new generation
      await user.click(screen.getByText('Create New Generation'));
      await user.type(screen.getByLabelText('Prompt'), 'Test prompt');
      await user.click(screen.getByText('Start Generation'));
      
      // RED PHASE: This should FAIL if history is not refreshed
      await waitFor(() => {
        expect(mockApiClient.getGenerationHistory).toHaveBeenCalledTimes(2);
      });
    });
  });
});