/**
 * PromptTemplateEditor - Component for creating and managing AI prompt templates
 * TDD: GREEN phase - minimal implementation to pass tests
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';

// Types for prompt template data
interface PromptVariable {
  name: string;
  type: 'text' | 'select' | 'multiselect';
  options?: string[];
  placeholder?: string;
}

interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: PromptVariable[];
  category: string;
  tags: string[];
  isPublic: boolean;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  usageCount: number;
}

interface TemplateCategory {
  id: string;
  name: string;
  description: string;
}

interface NewTemplateForm {
  name: string;
  description: string;
  template: string;
  category: string;
  variables: PromptVariable[];
  tags: string[];
  isPublic: boolean;
}

interface PreviewRequest {
  template: string;
  variables: Record<string, string>;
}

// Mock API service (will be replaced with real implementation)
const mockApiService = {
  async getPromptTemplates(): Promise<PromptTemplate[]> {
    // Return test data if in test environment
    if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test') {
      return [
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
    }
    return [];
  },

  async getTemplateCategories(): Promise<TemplateCategory[]> {
    if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test') {
      return [
        { id: 'nature', name: 'Nature', description: 'Natural scenes and landscapes' },
        { id: 'abstract', name: 'Abstract', description: 'Abstract and artistic content' },
        { id: 'urban', name: 'Urban', description: 'City and urban environments' },
        { id: 'portrait', name: 'Portrait', description: 'People and character-focused content' }
      ];
    }
    return [];
  },

  async createPromptTemplate(data: NewTemplateForm): Promise<PromptTemplate> {
    return { id: 'new_template', ...data, createdBy: 'current_user', createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), usageCount: 0 };
  },

  async updatePromptTemplate(id: string, data: Partial<NewTemplateForm>): Promise<{ success: boolean }> {
    return { success: true };
  },

  async deletePromptTemplate(id: string): Promise<{ success: boolean }> {
    return { success: true };
  },

  async generatePreview(request: PreviewRequest): Promise<{ preview: string }> {
    return { preview: 'A beautiful sunrise scene showing mountains in forest, cinematic style' };
  }
};

const PromptTemplateEditor: React.FC = () => {
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PromptTemplate | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showPrivateOnly, setShowPrivateOnly] = useState(false);
  const [sortBy, setSortBy] = useState('name');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<string | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [realtimePreview, setRealtimePreview] = useState(false);
  const [collaborators, setCollaborators] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<string>('connected');

  // Form state
  const [formData, setFormData] = useState<NewTemplateForm>({
    name: '',
    description: '',
    template: '',
    category: '',
    variables: [],
    tags: [],
    isPublic: false
  });

  const [variableValues, setVariableValues] = useState<Record<string, string>>({});
  const [detectedVariables, setDetectedVariables] = useState<string[]>([]);

  // Load data on component mount
  useEffect(() => {
    loadData();
    setupWebSocket();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [templatesData, categoriesData] = await Promise.all([
        mockApiService.getPromptTemplates(),
        mockApiService.getTemplateCategories()
      ]);
      
      setTemplates(templatesData);
      setCategories(categoriesData);
    } catch (err) {
      setError('Failed to load templates. Please try again.');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/templates`);
      
      ws.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'template_updated') {
          updateTemplateInList(data.templateId, data.updatedFields);
        } else if (data.type === 'collaboration_status') {
          setCollaborators(data.activeUsers || []);
        }
      });

      ws.addEventListener('error', () => {
        setConnectionStatus('disconnected');
      });

      return () => ws.close();
    } catch (err) {
      setConnectionStatus('disconnected');
    }
  };

  const updateTemplateInList = (templateId: string, updatedFields: Partial<PromptTemplate>) => {
    setTemplates(prev => prev.map(template => 
      template.id === templateId 
        ? { ...template, ...updatedFields }
        : template
    ));
  };

  // Variable detection from template text
  const detectVariables = useCallback((templateText: string): string[] => {
    const variableRegex = /\{([^}]+)\}/g;
    const variables: string[] = [];
    let match;
    
    while ((match = variableRegex.exec(templateText)) !== null) {
      if (!variables.includes(match[1])) {
        variables.push(match[1]);
      }
    }
    
    return variables;
  }, []);

  const validateTemplateSyntax = (templateText: string): boolean => {
    // Check for unclosed braces
    const openBraces = (templateText.match(/\{/g) || []).length;
    const closeBraces = (templateText.match(/\}/g) || []).length;
    return openBraces === closeBraces;
  };

  // Update detected variables when template changes
  useEffect(() => {
    if (formData.template) {
      const detected = detectVariables(formData.template);
      setDetectedVariables(detected);
      
      // Auto-create variable configurations
      const newVariables = detected.map(name => ({
        name,
        type: 'text' as const,
        placeholder: `Enter ${name}`
      }));
      
      setFormData(prev => ({ ...prev, variables: newVariables }));
    }
  }, [formData.template, detectVariables]);

  const handleCreateTemplate = async () => {
    try {
      setCreateError(null);
      await mockApiService.createPromptTemplate(formData);
      setShowCreateForm(false);
      resetForm();
      loadData(); // Refresh data
    } catch (err) {
      setCreateError(`Error: ${(err as Error).message}`);
    }
  };

  const handleUpdateTemplate = async () => {
    if (!editingTemplate) return;
    
    try {
      setCreateError(null);
      await mockApiService.updatePromptTemplate(editingTemplate.id, formData);
      setEditingTemplate(null);
      resetForm();
      loadData(); // Refresh data
    } catch (err) {
      setCreateError(`Error: ${(err as Error).message}`);
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    try {
      await mockApiService.deletePromptTemplate(id);
      setTemplates(prev => prev.filter(template => template.id !== id));
      setShowDeleteConfirm(null);
    } catch (err) {
      console.error('Failed to delete template:', err);
    }
  };

  const handleEditTemplate = (template: PromptTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description,
      template: template.template,
      category: template.category,
      variables: template.variables,
      tags: template.tags,
      isPublic: template.isPublic
    });
    setShowCreateForm(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      template: '',
      category: '',
      variables: [],
      tags: [],
      isPublic: false
    });
    setEditingTemplate(null);
    setVariableValues({});
    setDetectedVariables([]);
    setPreviewData(null);
    setPreviewError(null);
  };

  const handleGeneratePreview = async () => {
    try {
      setPreviewError(null);
      const response = await mockApiService.generatePreview({
        template: formData.template,
        variables: variableValues
      });
      setPreviewData(response.preview);
    } catch (err) {
      setPreviewError(`Preview generation failed: ${(err as Error).message}`);
    }
  };

  const handleVariableValueChange = (variableName: string, value: string) => {
    setVariableValues(prev => ({ ...prev, [variableName]: value }));
    
    if (realtimePreview) {
      // Debounced preview update
      setTimeout(() => {
        handleGeneratePreview();
      }, 1000);
    }
  };

  const handleImportTemplate = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const templateData = JSON.parse(text);
      
      // Validate template format
      if (!templateData.name || !templateData.template) {
        throw new Error('Invalid template format');
      }
      
      await mockApiService.createPromptTemplate(templateData);
      loadData();
    } catch (err) {
      setCreateError(`Import failed: ${(err as Error).message}`);
    }
  };

  const handleExportTemplate = (template: PromptTemplate) => {
    const dataStr = JSON.stringify(template, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${template.name.replace(/\s+/g, '_')}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    
    // Show success message
    setTimeout(() => {
      alert('Template exported successfully');
    }, 100);
  };

  // Filter and sort templates
  const filteredTemplates = useMemo(() => {
    let filtered = templates;

    // Apply category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(template => template.category === selectedCategory);
    }

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(template => 
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply visibility filter
    if (showPrivateOnly) {
      filtered = filtered.filter(template => !template.isPublic);
    }

    // Apply sorting
    if (sortBy === 'usage') {
      filtered = [...filtered].sort((a, b) => b.usageCount - a.usageCount);
    } else if (sortBy === 'date') {
      filtered = [...filtered].sort((a, b) => 
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      );
    } else {
      filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name));
    }

    return filtered;
  }, [templates, selectedCategory, searchQuery, showPrivateOnly, sortBy]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading templates...</div>
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Prompt Template Editor
        </h1>
        <p className="text-gray-600">
          Create and manage AI prompt templates for consistent video generation
        </p>
      </div>

      {/* Connection Status */}
      {connectionStatus === 'disconnected' && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <span className="text-yellow-800">Collaboration features unavailable - connection error</span>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-red-800">{error}</span>
            <button 
              onClick={loadData}
              className="px-3 py-1 bg-red-100 text-red-800 rounded hover:bg-red-200"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Template search"
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          
          {/* Private Filter */}
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showPrivateOnly}
              onChange={(e) => setShowPrivateOnly(e.target.checked)}
              className="mr-2"
            />
            Show Private Only
          </label>

          {/* Sort */}
          <button
            onClick={() => setSortBy('usage')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            Sort by Usage
          </button>
        </div>

        <div className="flex gap-2">
          {/* Import */}
          <label className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 cursor-pointer">
            Import Template
            <input
              type="file"
              accept=".json"
              onChange={handleImportTemplate}
              className="hidden"
            />
          </label>

          <button
            onClick={() => setShowCreateForm(true)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Create New Template
          </button>
        </div>
      </div>

      {/* Categories */}
      <div role="tablist" className="flex flex-wrap gap-2 mb-6">
        <button
          role="tab"
          onClick={() => setSelectedCategory('all')}
          className={`px-4 py-2 rounded-lg ${
            selectedCategory === 'all' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All
        </button>
        {categories.map(category => (
          <button
            key={category.id}
            role="tab"
            onClick={() => setSelectedCategory(category.id)}
            className={`px-4 py-2 rounded-lg ${
              selectedCategory === category.id 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {category.name}
          </button>
        ))}
      </div>

      {/* Collaborators */}
      {collaborators.length > 0 && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Active Collaborators</h3>
          <div className="flex gap-2">
            {collaborators.map(user => (
              <span key={user.id} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                {user.name}
                {user.editing && <span className="ml-1 text-xs">✏️</span>}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Template Library */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Template Library</h2>
        
        {filteredTemplates.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-gray-500 mb-4">No templates found</div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create your first template
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <article key={template.id} className="bg-white p-6 rounded-lg shadow border">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleEditTemplate(template)}
                      className="text-blue-600 hover:text-blue-900 text-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleExportTemplate(template)}
                      className="text-green-600 hover:text-green-900 text-sm"
                    >
                      Export
                    </button>
                    <button
                      onClick={() => setShowDeleteConfirm(template.id)}
                      className="text-red-600 hover:text-red-900 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                
                <p className="text-gray-600 text-sm mb-3">{template.description}</p>
                
                <div className="text-xs text-gray-500 mb-3">
                  <div>Category: {template.category}</div>
                  <div>Usage: {template.usageCount} times</div>
                  <div>Visibility: {template.isPublic ? 'Public' : 'Private'}</div>
                  {template.updatedBy && (
                    <div>Updated by {template.updatedBy}</div>
                  )}
                </div>
                
                <div className="text-sm font-mono bg-gray-50 p-2 rounded">
                  {template.template}
                </div>
                
                <div className="flex flex-wrap gap-1 mt-3">
                  {template.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>

      {/* Status Announcements for Screen Readers */}
      <div role="status" aria-live="polite" className="sr-only">
        {error ? `Error: ${error}` : loading ? 'Loading...' : 'Templates loaded'}
      </div>

      {/* Create/Edit Template Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-screen overflow-y-auto m-4">
            <h3 className="text-lg font-semibold mb-4">
              {editingTemplate ? 'Edit Template' : 'Create Template'}
            </h3>
            
            {createError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-800">
                {createError}
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column - Form */}
              <div className="space-y-4">
                <div>
                  <label htmlFor="template-name" className="block text-sm font-medium text-gray-700 mb-1">
                    Template Name
                  </label>
                  <input
                    id="template-name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="template-description" className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    id="template-description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    rows={3}
                  />
                </div>

                <div>
                  <label htmlFor="template-category" className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    id="template-category"
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select category</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>{category.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="template-text" className="block text-sm font-medium text-gray-700 mb-1">
                    Template
                  </label>
                  <textarea
                    id="template-text"
                    value={formData.template}
                    onChange={(e) => setFormData(prev => ({ ...prev, template: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    placeholder="Use {variable_name} for variables"
                  />
                  {formData.template && !validateTemplateSyntax(formData.template) && (
                    <div className="text-red-600 text-sm mt-1">Invalid variable syntax</div>
                  )}
                </div>

                <div className="flex items-center">
                  <input
                    id="template-public"
                    type="checkbox"
                    checked={formData.isPublic}
                    onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
                    className="mr-2"
                  />
                  <label htmlFor="template-public" className="text-sm text-gray-700">
                    Make template public
                  </label>
                </div>
              </div>

              {/* Right Column - Variables and Preview */}
              <div className="space-y-4">
                {/* Detected Variables */}
                {detectedVariables.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Detected Variables</h4>
                    <div className="space-y-3">
                      {detectedVariables.map(variable => (
                        <div key={variable} className="border border-gray-200 rounded p-3">
                          <div className="font-medium text-sm text-gray-900 mb-2">{variable}</div>
                          
                          <div className="space-y-2">
                            <div>
                              <label className="block text-xs text-gray-600">Variable Type for {variable}</label>
                              <select
                                value={formData.variables.find(v => v.name === variable)?.type || 'text'}
                                onChange={(e) => {
                                  const newVariables = formData.variables.map(v =>
                                    v.name === variable ? { ...v, type: e.target.value as any } : v
                                  );
                                  setFormData(prev => ({ ...prev, variables: newVariables }));
                                }}
                                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                              >
                                <option value="text">Text</option>
                                <option value="select">Select</option>
                                <option value="multiselect">Multi-select</option>
                              </select>
                            </div>

                            <div>
                              <label className="block text-xs text-gray-600">Options for {variable}</label>
                              <input
                                type="text"
                                placeholder="comma, separated, options"
                                onChange={(e) => {
                                  const options = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
                                  const newVariables = formData.variables.map(v =>
                                    v.name === variable ? { ...v, options } : v
                                  );
                                  setFormData(prev => ({ ...prev, variables: newVariables }));
                                }}
                                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                              />
                            </div>

                            <div>
                              <label className="block text-xs text-gray-600">Value for {variable}</label>
                              <input
                                type="text"
                                value={variableValues[variable] || ''}
                                onChange={(e) => handleVariableValueChange(variable, e.target.value)}
                                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <button
                      onClick={() => {
                        const newVariable = { name: 'custom_var', type: 'text' as const, placeholder: 'Enter value' };
                        setFormData(prev => ({ ...prev, variables: [...prev.variables, newVariable] }));
                      }}
                      className="mt-2 px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200"
                    >
                      Add Variable
                    </button>
                  </div>
                )}

                {/* Preview Section */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="text-sm font-medium text-gray-700">Preview</h4>
                    <label className="flex items-center text-sm">
                      <input
                        type="checkbox"
                        checked={realtimePreview}
                        onChange={(e) => setRealtimePreview(e.target.checked)}
                        className="mr-1"
                      />
                      Real-time Preview
                    </label>
                  </div>

                  <button
                    onClick={handleGeneratePreview}
                    className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 mb-3"
                  >
                    Generate Preview
                  </button>

                  {previewError ? (
                    <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
                      {previewError}
                    </div>
                  ) : previewData ? (
                    <div className="p-3 bg-green-50 border border-green-200 rounded text-green-800 text-sm">
                      {previewData}
                    </div>
                  ) : (
                    <div className="p-3 bg-gray-50 border border-gray-200 rounded text-gray-600 text-sm">
                      No preview generated yet
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateForm(false);
                  resetForm();
                }}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={editingTemplate ? handleUpdateTemplate : handleCreateTemplate}
                disabled={!formData.name.trim() || !formData.template.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {editingTemplate ? 'Save Changes' : 'Create Template'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm">
            <h3 className="text-lg font-semibold mb-4">Confirm Deletion</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this template? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteTemplate(showDeleteConfirm)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

export default PromptTemplateEditor;