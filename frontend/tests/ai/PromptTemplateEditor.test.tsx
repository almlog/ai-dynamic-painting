/**
 * Tests for PromptTemplateEditor component
 * TDD: RED phase - tests written before component implementation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import PromptTemplateEditor from '../../src/ai/components/PromptTemplateEditor';

// Mock prompt template data
const mockPromptTemplates = [
  {
    id: 'template_1',
    name: 'Nature Scenes',
    description: 'Template for beautiful nature scenes',
    template: 'A {adjective} {time_of_day} scene showing {subject} in {location}, {style} style',
    variables: [
      { name: 'adjective', type: 'select', options: ['beautiful', 'serene', 'dramatic', 'peaceful'] },
      { name: 'time_of_day', type: 'select', options: ['sunrise', 'sunset', 'dawn', 'dusk', 'midday'] },
      { name: 'subject', type: 'text', placeholder: 'e.g., mountains, forest, lake' },
      { name: 'location', type: 'text', placeholder: 'e.g., forest, meadow, coastline' },
      { name: 'style', type: 'select', options: ['cinematic', 'photorealistic', 'artistic', 'dreamy'] }
    ],
    category: 'nature',
    tags: ['landscape', 'nature', 'scenery'],
    isPublic: true,
    createdBy: 'system',
    createdAt: '2025-09-18T10:00:00Z',
    updatedAt: '2025-09-18T10:00:00Z',
    usageCount: 15
  },
  {
    id: 'template_2',
    name: 'Abstract Art',
    description: 'Template for abstract artistic videos',
    template: '{colors} abstract {pattern} with {movement} motion, {mood} atmosphere',
    variables: [
      { name: 'colors', type: 'multiselect', options: ['vibrant', 'muted', 'monochrome', 'pastel', 'neon'] },
      { name: 'pattern', type: 'select', options: ['geometric shapes', 'flowing lines', 'fractals', 'organic forms'] },
      { name: 'movement', type: 'select', options: ['slow', 'rhythmic', 'dynamic', 'chaotic', 'gentle'] },
      { name: 'mood', type: 'select', options: ['energetic', 'calm', 'mysterious', 'uplifting', 'meditative'] }
    ],
    category: 'abstract',
    tags: ['abstract', 'art', 'patterns'],
    isPublic: false,
    createdBy: 'user_123',
    createdAt: '2025-09-18T11:00:00Z',
    updatedAt: '2025-09-18T12:00:00Z',
    usageCount: 8
  }
];

const mockCategories = [
  { id: 'nature', name: 'Nature', description: 'Natural scenes and landscapes' },
  { id: 'abstract', name: 'Abstract', description: 'Abstract and artistic content' },
  { id: 'urban', name: 'Urban', description: 'City and urban environments' },
  { id: 'portrait', name: 'Portrait', description: 'People and character-focused content' }
];

// Mock API functions
const mockApiService = {
  getPromptTemplates: vi.fn(),
  createPromptTemplate: vi.fn(),
  updatePromptTemplate: vi.fn(),
  deletePromptTemplate: vi.fn(),
  getTemplateCategories: vi.fn(),
  generatePreview: vi.fn()
};

// Mock WebSocket for collaborative editing
const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
};

describe('PromptTemplateEditor Component', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    
    // Setup default mock implementations
    mockApiService.getPromptTemplates.mockResolvedValue(mockPromptTemplates);
    mockApiService.getTemplateCategories.mockResolvedValue(mockCategories);
    mockApiService.createPromptTemplate.mockResolvedValue({ id: 'new_template', ...mockPromptTemplates[0] });
    mockApiService.updatePromptTemplate.mockResolvedValue({ success: true });
    mockApiService.deletePromptTemplate.mockResolvedValue({ success: true });
    mockApiService.generatePreview.mockResolvedValue({
      preview: 'A beautiful sunrise scene showing mountains in forest, cinematic style'
    });
    
    // Mock WebSocket
    global.WebSocket = vi.fn(() => mockWebSocket);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render editor header with title', async () => {
      render(<PromptTemplateEditor />);
      
      expect(screen.getByText('Prompt Template Editor')).toBeInTheDocument();
      expect(screen.getByText(/create and manage ai prompt templates/i)).toBeInTheDocument();
    });

    it('should render template library section', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Template Library')).toBeInTheDocument();
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
        expect(screen.getByText('Abstract Art')).toBeInTheDocument();
      });
    });

    it('should render template creation form', async () => {
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      
      expect(screen.getByText('Create Template')).toBeInTheDocument();
      expect(screen.getByLabelText('Template Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Description')).toBeInTheDocument();
      expect(screen.getByLabelText('Template')).toBeInTheDocument();
    });

    it('should display template categories', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature')).toBeInTheDocument();
        expect(screen.getByText('Abstract')).toBeInTheDocument();
        expect(screen.getByText('Urban')).toBeInTheDocument();
        expect(screen.getByText('Portrait')).toBeInTheDocument();
      });
    });
  });

  describe('Template Management', () => {
    it('should create new template with correct data', async () => {
      render(<PromptTemplateEditor />);
      
      // Open create form
      fireEvent.click(screen.getByText('Create New Template'));
      
      // Fill form
      fireEvent.change(screen.getByLabelText('Template Name'), {
        target: { value: 'Test Template' }
      });
      fireEvent.change(screen.getByLabelText('Description'), {
        target: { value: 'Test description' }
      });
      fireEvent.change(screen.getByLabelText('Template'), {
        target: { value: 'A {subject} in {location}' }
      });
      
      // Select category
      fireEvent.change(screen.getByLabelText('Category'), {
        target: { value: 'nature' }
      });
      
      // Submit form
      fireEvent.click(screen.getByText('Create Template'));
      
      await waitFor(() => {
        expect(mockApiService.createPromptTemplate).toHaveBeenCalledWith({
          name: 'Test Template',
          description: 'Test description',
          template: 'A {subject} in {location}',
          category: 'nature',
          variables: expect.any(Array),
          tags: expect.any(Array),
          isPublic: false
        });
      });
    });

    it('should edit existing template', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
      });
      
      // Click edit button
      const editButtons = screen.getAllByText('Edit');
      fireEvent.click(editButtons[0]);
      
      // Modify template
      const nameInput = screen.getByDisplayValue('Nature Scenes');
      fireEvent.change(nameInput, {
        target: { value: 'Updated Nature Scenes' }
      });
      
      // Save changes
      fireEvent.click(screen.getByText('Save Changes'));
      
      await waitFor(() => {
        expect(mockApiService.updatePromptTemplate).toHaveBeenCalledWith('template_1', {
          name: 'Updated Nature Scenes',
          description: expect.any(String),
          template: expect.any(String),
          category: expect.any(String),
          variables: expect.any(Array),
          tags: expect.any(Array),
          isPublic: expect.any(Boolean)
        });
      });
    });

    it('should delete template with confirmation', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
      });
      
      // Click delete button
      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);
      
      // Confirm deletion
      expect(screen.getByText('Confirm Deletion')).toBeInTheDocument();
      fireEvent.click(screen.getByText('Confirm Delete'));
      
      await waitFor(() => {
        expect(mockApiService.deletePromptTemplate).toHaveBeenCalledWith('template_1');
      });
    });

    it('should handle template creation errors', async () => {
      mockApiService.createPromptTemplate.mockRejectedValue(new Error('Template name already exists'));
      
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      fireEvent.change(screen.getByLabelText('Template Name'), {
        target: { value: 'Duplicate Template' }
      });
      fireEvent.click(screen.getByText('Create Template'));
      
      await waitFor(() => {
        expect(screen.getByText('Error: Template name already exists')).toBeInTheDocument();
      });
    });
  });

  describe('Variable Management', () => {
    it('should detect variables in template text', async () => {
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      
      // Enter template with variables
      fireEvent.change(screen.getByLabelText('Template'), {
        target: { value: 'A {color} {animal} in {location}' }
      });
      
      // Variables should be detected automatically
      await waitFor(() => {
        expect(screen.getByText('Detected Variables')).toBeInTheDocument();
        expect(screen.getByText('color')).toBeInTheDocument();
        expect(screen.getByText('animal')).toBeInTheDocument();
        expect(screen.getByText('location')).toBeInTheDocument();
      });
    });

    it('should configure variable types and options', async () => {
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      fireEvent.change(screen.getByLabelText('Template'), {
        target: { value: 'A {color} sunset' }
      });
      
      await waitFor(() => {
        expect(screen.getByText('color')).toBeInTheDocument();
      });
      
      // Configure variable type
      fireEvent.change(screen.getByLabelText('Variable Type for color'), {
        target: { value: 'select' }
      });
      
      // Add options
      fireEvent.change(screen.getByLabelText('Options for color'), {
        target: { value: 'red, orange, pink, purple' }
      });
      
      expect(screen.getByDisplayValue('red, orange, pink, purple')).toBeInTheDocument();
    });

    it('should validate variable syntax', async () => {
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      
      // Enter invalid template syntax
      fireEvent.change(screen.getByLabelText('Template'), {
        target: { value: 'A {unclosed variable and {invalid syntax' }
      });
      
      await waitFor(() => {
        expect(screen.getByText(/invalid variable syntax/i)).toBeInTheDocument();
      });
    });

    it('should add custom variables manually', async () => {
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      
      // Add custom variable
      fireEvent.click(screen.getByText('Add Variable'));
      
      fireEvent.change(screen.getByLabelText('Variable Name'), {
        target: { value: 'custom_var' }
      });
      fireEvent.change(screen.getByLabelText('Variable Type'), {
        target: { value: 'text' }
      });
      
      expect(screen.getByDisplayValue('custom_var')).toBeInTheDocument();
    });
  });

  describe('Template Preview', () => {
    it('should generate template preview with variables', async () => {
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      
      // Set template
      fireEvent.change(screen.getByLabelText('Template'), {
        target: { value: 'A {adjective} {subject} in {location}' }
      });
      
      // Set variable values
      fireEvent.change(screen.getByLabelText('Value for adjective'), {
        target: { value: 'beautiful' }
      });
      fireEvent.change(screen.getByLabelText('Value for subject'), {
        target: { value: 'sunset' }
      });
      fireEvent.change(screen.getByLabelText('Value for location'), {
        target: { value: 'mountains' }
      });
      
      // Generate preview
      fireEvent.click(screen.getByText('Generate Preview'));
      
      await waitFor(() => {
        expect(mockApiService.generatePreview).toHaveBeenCalledWith({
          template: 'A {adjective} {subject} in {location}',
          variables: {
            adjective: 'beautiful',
            subject: 'sunset',
            location: 'mountains'
          }
        });
        expect(screen.getByText('A beautiful sunrise scene showing mountains in forest, cinematic style')).toBeInTheDocument();
      });
    });

    it('should update preview in real-time', async () => {
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      
      // Enable real-time preview
      fireEvent.click(screen.getByLabelText('Real-time Preview'));
      
      // Change template
      fireEvent.change(screen.getByLabelText('Template'), {
        target: { value: 'A {color} sky' }
      });
      
      // Should automatically generate preview
      await waitFor(() => {
        expect(mockApiService.generatePreview).toHaveBeenCalled();
      }, { timeout: 3000 });
    });

    it('should show preview errors gracefully', async () => {
      mockApiService.generatePreview.mockRejectedValue(new Error('Preview generation failed'));
      
      render(<PromptTemplateEditor />);
      
      fireEvent.click(screen.getByText('Create New Template'));
      fireEvent.click(screen.getByText('Generate Preview'));
      
      await waitFor(() => {
        expect(screen.getByText(/preview generation failed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Template Filtering and Search', () => {
    it('should filter templates by category', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
        expect(screen.getByText('Abstract Art')).toBeInTheDocument();
      });
      
      // Filter by nature category
      fireEvent.click(screen.getByText('Nature'));
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
        expect(screen.queryByText('Abstract Art')).not.toBeInTheDocument();
      });
    });

    it('should search templates by name and description', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
      });
      
      // Search for specific template
      fireEvent.change(screen.getByPlaceholderText('Search templates...'), {
        target: { value: 'abstract' }
      });
      
      await waitFor(() => {
        expect(screen.queryByText('Nature Scenes')).not.toBeInTheDocument();
        expect(screen.getByText('Abstract Art')).toBeInTheDocument();
      });
    });

    it('should filter by template visibility', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
        expect(screen.getByText('Abstract Art')).toBeInTheDocument();
      });
      
      // Filter by private templates only
      fireEvent.click(screen.getByLabelText('Show Private Only'));
      
      await waitFor(() => {
        expect(screen.queryByText('Nature Scenes')).not.toBeInTheDocument();
        expect(screen.getByText('Abstract Art')).toBeInTheDocument();
      });
    });

    it('should sort templates by usage and date', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
      });
      
      // Sort by usage count
      fireEvent.click(screen.getByText('Sort by Usage'));
      
      // Templates should be reordered (Nature Scenes has higher usage)
      const templateCards = screen.getAllByRole('article');
      expect(templateCards[0]).toHaveTextContent('Nature Scenes');
    });
  });

  describe('Collaborative Features', () => {
    it('should establish WebSocket connection for collaboration', () => {
      render(<PromptTemplateEditor />);
      
      expect(global.WebSocket).toHaveBeenCalledWith(
        expect.stringContaining('/ws/templates')
      );
    });

    it('should handle real-time template updates', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
      });
      
      // Simulate WebSocket message for template update
      const messageHandler = mockWebSocket.addEventListener.mock.calls
        .find(call => call[0] === 'message')[1];
      
      messageHandler({
        data: JSON.stringify({
          type: 'template_updated',
          templateId: 'template_1',
          updatedFields: {
            name: 'Updated Nature Scenes',
            updatedBy: 'another_user'
          }
        })
      });
      
      await waitFor(() => {
        expect(screen.getByText('Updated Nature Scenes')).toBeInTheDocument();
        expect(screen.getByText(/updated by another_user/i)).toBeInTheDocument();
      });
    });

    it('should show active collaborators', async () => {
      render(<PromptTemplateEditor />);
      
      // Simulate collaboration status message
      const messageHandler = mockWebSocket.addEventListener.mock.calls
        .find(call => call[0] === 'message')[1];
      
      messageHandler({
        data: JSON.stringify({
          type: 'collaboration_status',
          activeUsers: [
            { id: 'user_1', name: 'Alice', editing: 'template_1' },
            { id: 'user_2', name: 'Bob', editing: null }
          ]
        })
      });
      
      await waitFor(() => {
        expect(screen.getByText('Active Collaborators')).toBeInTheDocument();
        expect(screen.getByText('Alice')).toBeInTheDocument();
        expect(screen.getByText('Bob')).toBeInTheDocument();
      });
    });
  });

  describe('Template Import/Export', () => {
    it('should export template as JSON', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
      });
      
      // Export template
      const exportButtons = screen.getAllByText('Export');
      fireEvent.click(exportButtons[0]);
      
      // Should trigger download
      expect(screen.getByText(/template exported successfully/i)).toBeInTheDocument();
    });

    it('should import template from JSON file', async () => {
      render(<PromptTemplateEditor />);
      
      // Create mock file
      const mockFile = new File(
        [JSON.stringify(mockPromptTemplates[0])],
        'template.json',
        { type: 'application/json' }
      );
      
      // Upload file
      const fileInput = screen.getByLabelText('Import Template');
      fireEvent.change(fileInput, { target: { files: [mockFile] } });
      
      await waitFor(() => {
        expect(mockApiService.createPromptTemplate).toHaveBeenCalled();
      });
    });

    it('should validate imported template format', async () => {
      render(<PromptTemplateEditor />);
      
      // Create invalid file
      const invalidFile = new File(
        ['invalid json content'],
        'invalid.json',
        { type: 'application/json' }
      );
      
      const fileInput = screen.getByLabelText('Import Template');
      fireEvent.change(fileInput, { target: { files: [invalidFile] } });
      
      await waitFor(() => {
        expect(screen.getByText(/invalid template format/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      mockApiService.getPromptTemplates.mockRejectedValue(new Error('Network error'));
      
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load templates/i)).toBeInTheDocument();
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
    });

    it('should retry failed operations', async () => {
      mockApiService.getPromptTemplates.mockRejectedValueOnce(new Error('Network error'));
      mockApiService.getPromptTemplates.mockResolvedValueOnce(mockPromptTemplates);
      
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Retry'));
      
      await waitFor(() => {
        expect(screen.getByText('Nature Scenes')).toBeInTheDocument();
      });
    });

    it('should handle WebSocket connection errors', async () => {
      render(<PromptTemplateEditor />);
      
      // Simulate WebSocket error
      const errorHandler = mockWebSocket.addEventListener.mock.calls
        .find(call => call[0] === 'error')[1];
      
      errorHandler(new Error('WebSocket connection failed'));
      
      await waitFor(() => {
        expect(screen.getByText(/collaboration features unavailable/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', async () => {
      render(<PromptTemplateEditor />);
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByLabelText('Template search')).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      render(<PromptTemplateEditor />);
      
      const createButton = screen.getByText('Create New Template');
      createButton.focus();
      
      expect(document.activeElement).toBe(createButton);
      
      // Tab navigation
      fireEvent.keyDown(createButton, { key: 'Tab' });
      expect(document.activeElement).not.toBe(createButton);
    });

    it('should announce changes to screen readers', async () => {
      render(<PromptTemplateEditor />);
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });
});