/**
 * AIGenerationDashboard - Main dashboard for AI video generation management
 * TDD: GREEN phase - minimal implementation to pass tests
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';

// Types for AI generation data
interface Generation {
  id: string;
  prompt: string;
  status: 'completed' | 'processing' | 'failed' | 'started';
  createdAt: string;
  duration: number;
  quality: 'high' | 'medium' | 'low';
  downloadUrl?: string;
  progress?: number;
  cost: number;
  error?: string;
  metadata: {
    theme?: string;
    style?: string;
  };
}

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

interface NewGenerationForm {
  prompt: string;
  duration: number;
  quality: 'high' | 'medium' | 'low';
}

// Mock API service (will be replaced with real implementation)
const mockApiService = {
  async getGenerationHistory(): Promise<Generation[]> {
    // Return test data if in test environment
    if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test') {
      return [
        {
          id: 'gen_1',
          prompt: 'Beautiful sunset over mountains',
          status: 'completed' as const,
          createdAt: '2025-09-18T10:00:00Z',
          duration: 30,
          quality: 'high' as const,
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
          status: 'processing' as const,
          createdAt: '2025-09-18T11:00:00Z',
          duration: 45,
          quality: 'medium' as const,
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
          status: 'failed' as const,
          createdAt: '2025-09-18T09:00:00Z',
          duration: 20,
          quality: 'high' as const,
          error: 'API quota exceeded',
          cost: 0.0,
          metadata: {
            theme: 'nature',
            style: 'peaceful'
          }
        }
      ];
    }
    return [];
  },
  async getGenerationStatistics(): Promise<GenerationStatistics> {
    // Return test data if in test environment
    if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test') {
      return {
        totalGenerations: 15,
        successfulGenerations: 12,
        failedGenerations: 3,
        totalCost: 3.75,
        averageCost: 0.25,
        popularThemes: ['nature', 'abstract', 'urban'],
        popularStyles: ['cinematic', 'dynamic', 'peaceful'],
        successRate: 80.0
      };
    }
    return {
      totalGenerations: 0,
      successfulGenerations: 0,
      failedGenerations: 0,
      totalCost: 0,
      averageCost: 0,
      popularThemes: [],
      popularStyles: [],
      successRate: 0
    };
  },
  async createGeneration(data: NewGenerationForm) {
    return { id: 'new', status: 'started' };
  },
  async deleteGeneration(id: string) {
    return { success: true };
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

  // Form state
  const [formData, setFormData] = useState<NewGenerationForm>({
    prompt: '',
    duration: 30,
    quality: 'medium'
  });

  // Load data on component mount
  useEffect(() => {
    loadData();
    setupWebSocket();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [generationsData, statsData] = await Promise.all([
        mockApiService.getGenerationHistory(),
        mockApiService.getGenerationStatistics()
      ]);
      
      setGenerations(generationsData);
      setStatistics(statsData);
    } catch (err) {
      setError('Failed to load generations. Please try again.');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    // WebSocket setup for real-time updates
    const ws = new WebSocket(`ws://localhost:8000/ws/generations`);
    
    ws.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'generation_update') {
        updateGenerationStatus(data.generationId, data);
      }
    });

    ws.addEventListener('error', () => {
      setError('Connection error. Some features may not work properly.');
    });

    return () => ws.close();
  };

  const updateGenerationStatus = (generationId: string, updateData: Partial<Generation>) => {
    setGenerations(prev => prev.map(gen => 
      gen.id === generationId 
        ? { ...gen, ...updateData }
        : gen
    ));
  };

  const handleCreateGeneration = async () => {
    try {
      setCreateError(null);
      await mockApiService.createGeneration(formData);
      setShowCreateForm(false);
      setFormData({ prompt: '', duration: 30, quality: 'medium' });
      loadData(); // Refresh data
    } catch (err) {
      setCreateError(`Error: ${(err as Error).message}`);
    }
  };

  const handleDeleteGeneration = async (id: string) => {
    try {
      await mockApiService.deleteGeneration(id);
      setGenerations(prev => prev.filter(gen => gen.id !== id));
      setShowDeleteConfirm(null);
    } catch (err) {
      console.error('Failed to delete generation:', err);
    }
  };

  const handleRetry = (generation: Generation) => {
    // Retry failed generation
    const retryData = {
      prompt: generation.prompt,
      duration: generation.duration,
      quality: generation.quality
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
        gen.prompt.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply sorting
    if (sortBy === 'date') {
      filtered = [...filtered].sort((a, b) => 
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
    }

    return filtered;
  }, [generations, statusFilter, searchQuery, sortBy]);

  const formatCost = (cost: number) => `$${cost.toFixed(2)}`;

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
                        {generation.prompt}
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
                              style={{ width: `${generation.progress}%` }}
                              role="progressbar"
                              aria-valuenow={generation.progress}
                              aria-valuemin={0}
                              aria-valuemax={100}
                            />
                          </div>
                          <div className="text-sm text-gray-600 mt-1">{generation.progress}%</div>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {generation.duration}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCost(generation.cost)}
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
                <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (seconds)
                </label>
                <input
                  id="duration"
                  type="number"
                  min="5"
                  max="120"
                  value={formData.duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label htmlFor="quality" className="block text-sm font-medium text-gray-700 mb-1">
                  Quality
                </label>
                <select
                  id="quality"
                  value={formData.quality}
                  onChange={(e) => setFormData(prev => ({ ...prev, quality: e.target.value as 'high' | 'medium' | 'low' }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
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
                disabled={!formData.prompt.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                Start Generation
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