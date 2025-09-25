/**
 * AIGenerationDashboard - Main dashboard for AI video generation management
 * T4B-002: GREEN phase - Real API integration (no mock data)
 */

import React, { useState, useEffect, useMemo } from 'react';
// T4B-002: Import API client from T4B-001
import { apiClient, isGenerationComplete, isGenerationFailed, isGenerationInProgress } from '../../services/api';
import type { GenerationRequest, GenerationResult } from '../../services/api';

// T4B-002: Extended type for UI compatibility with API types
interface Generation extends GenerationResult {
  // UI-specific properties derived from API data
  prompt?: string;     // Derived from request.variables.prompt
  duration?: number;   // Derived from metadata.generation_time
  cost?: number;       // Derived from metadata (future enhancement)
  progress?: number;   // For processing status (0-100)
  downloadUrl?: string; // Derived from image_path
  quality?: string;    // Derived from request.quality
  error?: string;      // Derived from error_message
  createdAt?: string;  // Alias for created_at for backward compatibility
}

// T4B-002: Statistics derived from API data instead of mock
interface GenerationStatistics {
  totalGenerations: number;
  successfulGenerations: number;
  failedGenerations: number;
  totalCost: number;
  averageCost: number;
  popularThemes: string[];
  popularStyles: string[];
  successRate: number;
}

// T4B-002: Form interface aligned with API GenerationRequest
interface NewGenerationForm {
  prompt_template_id: string;
  prompt: string;
  quality: 'standard' | 'hd';
  aspect_ratio: '1:1' | '16:9' | '9:16';
  style_preset?: 'anime' | 'photographic' | 'digital-art';
  negative_prompt?: string;
  seed?: number;
}

// T4B-002: Real API service using T4B-001 implementation
const realApiService = {
  async getGenerationHistory(): Promise<Generation[]> {
    try {
      return await apiClient.getGenerationHistory();
    } catch (error) {
      console.error('Failed to get generation history:', error);
      throw error;
    }
  },
  
  async createGeneration(data: NewGenerationForm): Promise<{ generation_id: string; status: string }> {
    try {
      const request: GenerationRequest = {
        prompt_template_id: data.prompt_template_id,
        model: 'gemini-1.5-flash',
        quality: data.quality,
        aspect_ratio: data.aspect_ratio,
        temperature: 0.7,
        top_k: 40,
        top_p: 0.95,
        max_tokens: 2048,
        variables: { prompt: data.prompt },
        style_preset: data.style_preset,
        negative_prompt: data.negative_prompt,
        seed: data.seed
      };
      
      return await apiClient.generateImage(request);
    } catch (error) {
      console.error('Failed to create generation:', error);
      throw error;
    }
  },
  
  async getGenerationStatus(id: string): Promise<Generation> {
    try {
      return await apiClient.getGenerationStatus(id);
    } catch (error) {
      console.error('Failed to get generation status:', error);
      throw error;
    }
  },
  
  // Transform API data to UI-compatible format
  transformGeneration(apiResult: GenerationResult): Generation {
    return {
      ...apiResult,
      prompt: apiResult.request?.variables?.prompt || 'Generated Image',
      duration: apiResult.metadata?.generation_time || 0,
      cost: 0, // TODO: Cost calculation needs backend API enhancement
      progress: isGenerationInProgress(apiResult.status) ? 50 : isGenerationComplete(apiResult.status) ? 100 : 0,
      downloadUrl: apiResult.image_path,
      quality: apiResult.request?.quality || 'standard',
      error: apiResult.error_message,
      createdAt: apiResult.created_at
    };
  },
  
  // Calculate statistics from generation data
  calculateStatistics(generations: Generation[]): GenerationStatistics {
    const total = generations.length;
    const successful = generations.filter(g => isGenerationComplete(g.status)).length;
    const failed = generations.filter(g => isGenerationFailed(g.status)).length;
    
    const totalCost = generations.reduce((sum, g) => sum + (g.cost || 0), 0);
    const averageCost = total > 0 ? totalCost / total : 0;
    
    // Extract themes and styles from request data
    const themes = new Set<string>();
    const styles = new Set<string>();
    
    generations.forEach(g => {
      if (g.request?.style_preset) {
        styles.add(g.request.style_preset);
      }
      // Extract themes from prompts (simple keyword extraction)
      const prompt = g.prompt?.toLowerCase() || '';
      if (prompt.includes('nature') || prompt.includes('landscape')) themes.add('nature');
      if (prompt.includes('abstract') || prompt.includes('pattern')) themes.add('abstract');
      if (prompt.includes('portrait') || prompt.includes('person')) themes.add('portrait');
    });
    
    const successRate = total > 0 ? (successful / total) * 100 : 0;
    
    return {
      totalGenerations: total,
      successfulGenerations: successful,
      failedGenerations: failed,
      totalCost,
      averageCost,
      popularThemes: Array.from(themes).slice(0, 3),
      popularStyles: Array.from(styles).slice(0, 3),
      successRate
    };
  }
};

const AIGenerationDashboard: React.FC = () => {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [statistics, setStatistics] = useState<GenerationStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Form state (T4B-002: Updated for API integration)
  const [formData, setFormData] = useState<NewGenerationForm>({
    prompt_template_id: 'default',
    prompt: '',
    quality: 'standard',
    aspect_ratio: '1:1',
    style_preset: undefined,
    negative_prompt: undefined,
    seed: undefined
  });

  // Load data on component mount
  useEffect(() => {
    loadData();
    // T4B-003: WebSocket setup temporarily disabled for testing
    // setupWebSocket();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // T4B-002: Use real API instead of mock data with proper transformation
      const apiGenerations = await realApiService.getGenerationHistory();
      const transformedGenerations = apiGenerations.map(gen => realApiService.transformGeneration(gen));
      const statsData = realApiService.calculateStatistics(transformedGenerations);
      
      setGenerations(transformedGenerations);
      setStatistics(statsData);
    } catch (err) {
      setError('Failed to load generations. Please try again.');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    // T4B-002: Real-time updates using polling (WebSocket server not implemented yet)
    const pollProcessingGenerations = async () => {
      try {
        const processingGens = generations.filter(g => isGenerationInProgress(g.status));
        
        for (const gen of processingGens) {
          try {
            const updatedGen = await realApiService.getGenerationStatus(gen.id);
            setGenerations(prev => prev.map(g => 
              g.id === gen.id ? updatedGen : g
            ));
          } catch (error) {
            console.error(`Failed to update status for generation ${gen.id}:`, error);
          }
        }
      } catch (error) {
        console.error('Failed to poll generation statuses:', error);
      }
    };
    
    // Poll every 5 seconds for processing generations
    const pollInterval = setInterval(pollProcessingGenerations, 5000);
    
    return () => {
      clearInterval(pollInterval);
    };
  };

  // Removed unused updateGenerationStatus function for T4B-002 refactor

  const handleCreateGeneration = async () => {
    try {
      setCreateError(null);
      setIsGenerating(true);
      
      const result = await realApiService.createGeneration(formData);
      
      // Success: close form and refresh data
      setShowCreateForm(false);
      setFormData({ 
        prompt_template_id: 'default',
        prompt: '', 
        quality: 'standard',
        aspect_ratio: '1:1',
        style_preset: undefined,
        negative_prompt: undefined,
        seed: undefined
      });
      
      // Refresh generation history to show new item
      await loadData();
    } catch (err) {
      setCreateError(`Error: ${(err as Error).message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteGeneration = async (id: string) => {
    try {
      // T4B-002: Delete API not yet implemented in backend
      // await realApiService.deleteGeneration(id);
      console.warn('Delete generation not yet implemented in backend API');
      setGenerations(prev => prev.filter(gen => gen.id !== id));
      setShowDeleteConfirm(null);
    } catch (err) {
      console.error('Failed to delete generation:', err);
    }
  };

  const handleRetry = (generation: Generation) => {
    // Retry failed generation
    const retryData: NewGenerationForm = {
      prompt_template_id: 'default',
      prompt: generation.prompt || 'Generated Image',
      quality: (generation.quality === 'hd' ? 'hd' : 'standard') as 'standard' | 'hd',
      aspect_ratio: generation.request?.aspect_ratio || '1:1',
      style_preset: generation.request?.style_preset,
      negative_prompt: generation.request?.negative_prompt,
      seed: generation.request?.seed
    };
    setFormData(retryData);
    setShowCreateForm(true);
  };

  // Filter and sort generations
  const filteredGenerations = useMemo(() => {
    let filtered = generations;

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(gen => gen.status === statusFilter);
    }

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(gen => 
        gen.prompt?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply sorting
    if (sortBy === 'date') {
      filtered = [...filtered].sort((a, b) => 
        new Date(b.createdAt || b.created_at).getTime() - new Date(a.createdAt || a.created_at).getTime()
      );
    }

    return filtered;
  }, [generations, statusFilter, searchQuery, sortBy]);

  const formatCost = (cost: number | undefined) => cost ? `$${cost.toFixed(2)}` : '$0.00';

  const getStatusBadgeClass = (status: string) => {
    const baseClass = 'px-2 py-1 rounded text-sm font-medium ';
    switch (status) {
      case 'completed': return baseClass + 'bg-green-100 text-green-800';
      case 'processing': return baseClass + 'bg-blue-100 text-blue-800';
      case 'failed': return baseClass + 'bg-red-100 text-red-800';
      default: return baseClass + 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Generation Dashboard
        </h1>
        <p className="text-gray-600">
          Manage your AI video generations and monitor performance
        </p>
      </div>

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

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Generations</h3>
            <div className="text-3xl font-bold text-blue-600">{statistics.totalGenerations}</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Success Rate</h3>
            <div className="text-3xl font-bold text-green-600">{statistics.successRate.toFixed(1)}%</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Cost</h3>
            <div className="text-3xl font-bold text-purple-600">{formatCost(statistics.totalCost)}</div>
            {statistics.totalCost > 9.50 && (
              <div className="text-sm text-orange-600 mt-1">Approaching cost limit</div>
            )}
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Average Cost</h3>
            <div className="text-3xl font-bold text-indigo-600">{formatCost(statistics.averageCost)}</div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <input
            type="text"
            placeholder="Search generations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Filter by Status"
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>

          {/* Sort */}
          <button
            onClick={() => setSortBy('date')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            Sort by Date
          </button>
        </div>

        <button
          onClick={() => setShowCreateForm(true)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Create New Generation
        </button>
      </div>

      {/* Generation History */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Generation History</h2>
        </div>

        {filteredGenerations.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-gray-500 mb-4">No generations found</div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create your first AI generation
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table role="table" className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prompt
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredGenerations.map((generation) => (
                  <tr key={generation.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {generation.prompt || 'Generated Image'}
                      </div>
                      {generation.error && (
                        <div className="text-sm text-red-600">{generation.error}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={getStatusBadgeClass(generation.status)}>
                        {generation.status}
                      </span>
                      {generation.status === 'processing' && generation.progress && (
                        <div className="mt-2">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${generation.progress || 0}%` }}
                              role="progressbar"
                              aria-valuenow={generation.progress || 0}
                              aria-valuemin={0}
                              aria-valuemax={100}
                            />
                          </div>
                          <div className="text-sm text-gray-600 mt-1">{generation.progress || 0}%</div>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {generation.duration || 0}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCost(generation.cost || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        {generation.status === 'completed' && generation.downloadUrl && (
                          <a
                            href={generation.downloadUrl}
                            download
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Download
                          </a>
                        )}
                        {generation.status === 'failed' && (
                          <button
                            onClick={() => handleRetry(generation)}
                            className="text-green-600 hover:text-green-900"
                          >
                            Retry
                          </button>
                        )}
                        <button
                          onClick={() => setShowDeleteConfirm(generation.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Cost Summary */}
      {statistics && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Total Cost: {formatCost(statistics.totalCost)}</span>
            <span>Average Cost: {formatCost(statistics.averageCost)}</span>
          </div>
        </div>
      )}

      {/* Status Announcements for Screen Readers */}
      <div role="status" aria-live="polite" className="sr-only">
        {error ? `Error: ${error}` : loading ? 'Loading...' : 'Dashboard loaded'}
      </div>

      {/* Create Generation Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create AI Generation</h3>
            
            {createError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-800">
                {createError}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
                  Prompt
                </label>
                <textarea
                  id="prompt"
                  value={formData.prompt}
                  onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  required
                />
              </div>

              <div>
                <label htmlFor="aspect_ratio" className="block text-sm font-medium text-gray-700 mb-1">
                  Aspect Ratio
                </label>
                <select
                  id="aspect_ratio"
                  value={formData.aspect_ratio}
                  onChange={(e) => setFormData(prev => ({ ...prev, aspect_ratio: e.target.value as '1:1' | '16:9' | '9:16' }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="1:1">1:1 (Square)</option>
                  <option value="16:9">16:9 (Landscape)</option>
                  <option value="9:16">9:16 (Portrait)</option>
                </select>
              </div>

              <div>
                <label htmlFor="quality" className="block text-sm font-medium text-gray-700 mb-1">
                  Quality
                </label>
                <select
                  id="quality"
                  value={formData.quality}
                  onChange={(e) => setFormData(prev => ({ ...prev, quality: e.target.value as 'standard' | 'hd' }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="standard">Standard</option>
                  <option value="hd">HD (High Definition)</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateForm(false);
                  setCreateError(null);
                }}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateGeneration}
                disabled={!formData.prompt.trim() || isGenerating}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {isGenerating ? 'Generating...' : 'Start Generation'}
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
              Are you sure you want to delete this generation? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteGeneration(showDeleteConfirm)}
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

export default AIGenerationDashboard;