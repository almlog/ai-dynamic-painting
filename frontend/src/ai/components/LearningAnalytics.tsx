/**
 * LearningAnalytics Component
 * TDD: GREEN phase - component implementation to pass tests
 */

import React, { useState, useEffect, useCallback } from 'react';

// Type definitions
interface UserPreferences {
  favoriteThemes: string[];
  preferredStyles: string[];
  optimalTimingPatterns: {
    morning: { theme: string; style: string };
    afternoon: { theme: string; style: string };
    evening: { theme: string; style: string };
  };
  averageViewingDuration: number;
  engagementScore: number;
  lastUpdated: string;
}

interface ContentPerformance {
  id: string;
  theme: string;
  style: string;
  viewCount: number;
  averageViewTime: number;
  userRating: number;
  engagementMetrics: {
    skipRate: number;
    replayRate: number;
    shareRate: number;
  };
}

interface LearningInsights {
  strongPreferences: string[];
  improvementAreas: string[];
  recommendations: string[];
}

interface InteractionPatterns {
  hourlyActivity: Record<string, number>;
  devicePreferences: {
    mobile: number;
    desktop: number;
    tablet: number;
  };
  sessionDuration: {
    average: number;
    median: number;
    longest: number;
  };
}

interface LearningData {
  userPreferences: UserPreferences | null;
  contentPerformance: ContentPerformance[];
  learningInsights: LearningInsights;
  interactionPatterns: InteractionPatterns | null;
}

interface Recommendation {
  type: string;
  priority: string;
  title: string;
  description: string;
  impact: string;
  actions: string[];
}

// Mock API service for testing
const createMockApiService = () => ({
  getLearningData: async (params?: any): Promise<LearningData> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
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
  },
  
  getPreferenceInsights: async (): Promise<UserPreferences> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return {
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
    };
  },
  
  getUserInteractionPatterns: async (): Promise<InteractionPatterns> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return {
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
    };
  },
  
  getContentPerformanceMetrics: async (): Promise<ContentPerformance[]> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return [
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
    ];
  },
  
  getLearningRecommendations: async (): Promise<Recommendation[]> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return [
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
  },
  
  updatePreferences: async (preferences: Partial<UserPreferences>): Promise<{ success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { success: true };
  },
  
  exportLearningData: async (): Promise<{ downloadUrl: string }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { downloadUrl: 'http://example.com/export.json' };
  },
  
  triggerLearningUpdate: async (): Promise<{ status: string }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { status: 'started' };
  }
});

const LearningAnalytics: React.FC = () => {
  const [learningData, setLearningData] = useState<LearningData | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingPreferences, setEditingPreferences] = useState(false);
  const [timeRange, setTimeRange] = useState('last_30_days');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [themeFilter, setThemeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('viewCount');
  const [showDetails, setShowDetails] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [preferenceForm, setPreferenceForm] = useState({
    favoriteThemes: '',
    preferredStyles: '',
    engagementThreshold: 80
  });

  const apiService = createMockApiService();

  const loadLearningData = useCallback(async (params?: any) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiService.getLearningData(params);
      setLearningData(data);
      
      const recs = await apiService.getLearningRecommendations();
      setRecommendations(recs);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load learning data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLearningData();
  }, [loadLearningData]);

  const handleTimeRangeChange = useCallback(async (newTimeRange: string) => {
    setTimeRange(newTimeRange);
    
    if (newTimeRange !== 'custom') {
      await loadLearningData({ timeRange: newTimeRange });
    }
  }, [loadLearningData]);

  const handleCustomDateRangeApply = useCallback(async () => {
    if (customStartDate && customEndDate) {
      await loadLearningData({
        timeRange: 'custom',
        startDate: customStartDate,
        endDate: customEndDate
      });
    }
  }, [customStartDate, customEndDate, loadLearningData]);

  const handleRefresh = useCallback(() => {
    loadLearningData({
      timeRange: timeRange !== 'custom' ? timeRange : 'custom',
      ...(timeRange === 'custom' && { startDate: customStartDate, endDate: customEndDate })
    });
  }, [timeRange, customStartDate, customEndDate, loadLearningData]);

  const handleExportData = useCallback(async () => {
    try {
      const result = await apiService.exportLearningData();
      setMessage('Data exported successfully');
      // In a real app, would trigger download
      console.log('Export URL:', result.downloadUrl);
    } catch (err) {
      setMessage(`Export failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, []);

  const handleTriggerLearningUpdate = useCallback(async () => {
    try {
      await apiService.triggerLearningUpdate();
      setMessage('Learning update started');
    } catch (err) {
      setMessage(`Update failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, []);

  const handleEditPreferences = useCallback(() => {
    if (learningData?.userPreferences) {
      setPreferenceForm({
        favoriteThemes: learningData.userPreferences.favoriteThemes.join(','),
        preferredStyles: learningData.userPreferences.preferredStyles.join(','),
        engagementThreshold: learningData.userPreferences.engagementScore
      });
    }
    setEditingPreferences(true);
  }, [learningData]);

  const handleSavePreferences = useCallback(async () => {
    try {
      const preferences = {
        favoriteThemes: preferenceForm.favoriteThemes.split(',').map(s => s.trim()).filter(Boolean),
        preferredStyles: preferenceForm.preferredStyles.split(',').map(s => s.trim()).filter(Boolean),
        engagementScore: preferenceForm.engagementThreshold
      };
      
      await apiService.updatePreferences(preferences);
      setEditingPreferences(false);
      setMessage('Preferences updated successfully');
      await loadLearningData();
      
    } catch (err) {
      setMessage(`Error updating preferences: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, [preferenceForm, loadLearningData]);

  const handleRetry = useCallback(() => {
    loadLearningData();
  }, [loadLearningData]);

  const filteredContent = learningData?.contentPerformance.filter(item => 
    themeFilter === 'all' || item.theme === themeFilter
  ) || [];

  const sortedContent = [...filteredContent].sort((a, b) => {
    switch (sortBy) {
      case 'rating':
        return b.userRating - a.userRating;
      case 'viewCount':
        return b.viewCount - a.viewCount;
      case 'viewTime':
        return b.averageViewTime - a.averageViewTime;
      default:
        return 0;
    }
  });

  const getPeakActivity = () => {
    if (!learningData?.interactionPatterns?.hourlyActivity) return null;
    
    const activity = learningData.interactionPatterns.hourlyActivity;
    const peak = Object.entries(activity).reduce((max, [hour, count]) => 
      count > max.count ? { hour, count } : max, { hour: '00', count: 0 });
    
    return `${peak.hour}:00 (${peak.count} interactions)`;
  };

  if (loading) {
    return (
      <div role="main" className="learning-analytics-dashboard">
        <div className="loading">Loading learning analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div role="main" className="learning-analytics-dashboard">
        <div className="error">
          <p>Failed to load learning data: {error}</p>
          <button onClick={handleRetry}>Retry</button>
        </div>
      </div>
    );
  }

  if (!learningData?.userPreferences && (!learningData?.contentPerformance || learningData.contentPerformance.length === 0)) {
    return (
      <div role="main" className="learning-analytics-dashboard">
        <div className="empty-state">
          <p>No learning data available yet.</p>
          <button onClick={() => setMessage('Data collection started')}>Start collecting data</button>
        </div>
      </div>
    );
  }

  return (
    <div role="main" className="learning-analytics-dashboard">
      <header className="dashboard-header">
        <h1>Learning Analytics Dashboard</h1>
        <p>Analyze user preferences and content performance to optimize AI generation</p>
        
        <div className="controls">
          <div className="time-range-controls">
            <label htmlFor="timeRange">Time Range</label>
            <select 
              id="timeRange"
              aria-label="Time Range"
              value={timeRange} 
              onChange={(e) => handleTimeRangeChange(e.target.value)}
            >
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="last_90_days">Last 90 Days</option>
              <option value="custom">Custom Range</option>
            </select>
            
            {timeRange === 'custom' && (
              <div className="custom-date-range">
                <label htmlFor="startDate">Start Date</label>
                <input
                  id="startDate"
                  aria-label="Start Date"
                  type="date"
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                />
                <label htmlFor="endDate">End Date</label>
                <input
                  id="endDate"
                  aria-label="End Date"
                  type="date"
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                />
                <button onClick={handleCustomDateRangeApply}>Apply Date Range</button>
              </div>
            )}
          </div>
          
          <div className="action-buttons">
            <button onClick={handleRefresh}>Refresh</button>
            <button onClick={handleExportData}>Export Data</button>
            <button onClick={handleTriggerLearningUpdate}>Update Learning Model</button>
          </div>
        </div>
      </header>

      {message && (
        <div role="status" className="message" aria-live="polite">
          {message}
        </div>
      )}

      {learningData?.userPreferences && (
        <section className="preference-summary">
          <h2>User Preferences Summary</h2>
          <div className="preference-cards">
            <div className="preference-card">
              <h3>Favorite Themes</h3>
              <p>{learningData.userPreferences.favoriteThemes.join(', ')}</p>
            </div>
            <div className="preference-card">
              <h3>Preferred Styles</h3>
              <p>{learningData.userPreferences.preferredStyles.join(', ')}</p>
            </div>
            <div className="preference-card">
              <h3>Engagement Score</h3>
              <p>{learningData.userPreferences.engagementScore}%</p>
            </div>
            <div className="preference-card">
              <h3>Average Viewing Duration</h3>
              <p>{learningData.userPreferences.averageViewingDuration} seconds</p>
            </div>
          </div>
          
          <div className="preference-actions">
            <button onClick={handleEditPreferences}>Edit Preferences</button>
          </div>
        </section>
      )}

      {editingPreferences && (
        <section className="preference-editor">
          <h2>Edit User Preferences</h2>
          <div className="preference-form">
            <div className="form-group">
              <label htmlFor="favoriteThemes">Favorite Themes</label>
              <input
                id="favoriteThemes"
                aria-label="Favorite Themes"
                type="text"
                value={preferenceForm.favoriteThemes}
                onChange={(e) => setPreferenceForm(prev => ({ ...prev, favoriteThemes: e.target.value }))}
                placeholder="nature, abstract, urban"
              />
            </div>
            <div className="form-group">
              <label htmlFor="preferredStyles">Preferred Styles</label>
              <input
                id="preferredStyles"
                aria-label="Preferred Styles"
                type="text"
                value={preferenceForm.preferredStyles}
                onChange={(e) => setPreferenceForm(prev => ({ ...prev, preferredStyles: e.target.value }))}
                placeholder="cinematic, dynamic, peaceful"
              />
            </div>
            <div className="form-actions">
              <button onClick={handleSavePreferences}>Save Preferences</button>
              <button onClick={() => setEditingPreferences(false)}>Cancel</button>
            </div>
          </div>
        </section>
      )}

      {learningData?.interactionPatterns && (
        <section className="interaction-patterns">
          <h2>User Interaction Patterns</h2>
          
          <div className="pattern-cards">
            <div className="pattern-card">
              <h3>Hourly Activity Patterns</h3>
              <p>Peak Activity: {getPeakActivity()}</p>
            </div>
            
            <div className="pattern-card">
              <h3>Device Preferences</h3>
              <div className="device-breakdown">
                <p>Mobile: {Math.round(learningData.interactionPatterns.devicePreferences.mobile * 100)}%</p>
                <p>Desktop: {Math.round(learningData.interactionPatterns.devicePreferences.desktop * 100)}%</p>
                <p>Tablet: {Math.round(learningData.interactionPatterns.devicePreferences.tablet * 100)}%</p>
              </div>
            </div>
            
            <div className="pattern-card">
              <h3>Session Duration</h3>
              <div className="session-stats">
                <p>Average: {learningData.interactionPatterns.sessionDuration.average} min</p>
                <p>Median: {learningData.interactionPatterns.sessionDuration.median} min</p>
                <p>Longest: {learningData.interactionPatterns.sessionDuration.longest} min</p>
              </div>
            </div>
          </div>
        </section>
      )}

      <section className="content-performance">
        <h2>Content Performance</h2>
        
        <div className="content-controls">
          <div className="filter-controls">
            <label htmlFor="themeFilter">Filter by Theme</label>
            <select
              id="themeFilter"
              aria-label="Filter by Theme"
              value={themeFilter}
              onChange={(e) => setThemeFilter(e.target.value)}
            >
              <option value="all">All Themes</option>
              <option value="nature">Nature</option>
              <option value="abstract">Abstract</option>
              <option value="urban">Urban</option>
            </select>
          </div>
          
          <div className="sort-controls">
            <button 
              onClick={() => setSortBy('rating')}
              className={sortBy === 'rating' ? 'active' : ''}
            >
              Sort by Rating
            </button>
            <button 
              onClick={() => setSortBy('viewCount')}
              className={sortBy === 'viewCount' ? 'active' : ''}
            >
              Sort by Views
            </button>
            <button 
              onClick={() => setSortBy('viewTime')}
              className={sortBy === 'viewTime' ? 'active' : ''}
            >
              Sort by View Time
            </button>
          </div>
        </div>

        <div className="content-table-container">
          <table role="table" className="content-performance-table">
            <thead>
              <tr role="row">
                <th>Content</th>
                <th>Views</th>
                <th>Avg View Time</th>
                <th>Rating</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedContent.map((content) => (
                <tr key={content.id} role="row">
                  <td>{content.theme} - {content.style}</td>
                  <td>{content.viewCount} views</td>
                  <td>{content.averageViewTime}s</td>
                  <td>{content.userRating}/5</td>
                  <td>
                    <button onClick={() => setShowDetails(showDetails === content.id ? null : content.id)}>
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {showDetails && (
          <div className="content-details">
            {(() => {
              const content = sortedContent.find(c => c.id === showDetails);
              if (!content) return null;
              
              return (
                <div className="detail-card">
                  <h4>Performance Details: {content.theme} - {content.style}</h4>
                  <div className="metrics">
                    <p>Skip Rate: {Math.round(content.engagementMetrics.skipRate * 100)}%</p>
                    <p>Replay Rate: {Math.round(content.engagementMetrics.replayRate * 100)}%</p>
                    <p>Share Rate: {Math.round(content.engagementMetrics.shareRate * 100)}%</p>
                  </div>
                </div>
              );
            })()}
          </div>
        )}
      </section>

      {learningData?.learningInsights && (
        <section className="learning-insights">
          <h2>Learning Insights</h2>
          
          <div className="insights-grid">
            <div className="insight-category">
              <h3>Strong Preferences</h3>
              <ul>
                {learningData.learningInsights.strongPreferences.map((insight, index) => (
                  <li key={index}>{insight}</li>
                ))}
              </ul>
            </div>
            
            <div className="insight-category">
              <h3>Improvement Areas</h3>
              <ul>
                {learningData.learningInsights.improvementAreas.map((area, index) => (
                  <li key={index}>{area}</li>
                ))}
              </ul>
            </div>
            
            <div className="insight-category">
              <h3>AI Recommendations</h3>
              <ul>
                {learningData.learningInsights.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}

      {recommendations.length > 0 && (
        <section className="learning-recommendations">
          <h2>Learning Recommendations</h2>
          
          <div className="recommendations-grid">
            {recommendations.map((recommendation, index) => (
              <div key={index} className="recommendation-card">
                <div className="recommendation-header">
                  <h3>{recommendation.title}</h3>
                  <span className={`priority priority-${recommendation.priority}`}>
                    {recommendation.priority}
                  </span>
                </div>
                
                <p className="recommendation-description">
                  {recommendation.description}
                </p>
                
                <p className="recommendation-impact">
                  {recommendation.impact}
                </p>
                
                <div className="recommendation-actions">
                  <h4>Actions:</h4>
                  <ul>
                    {recommendation.actions.map((action, actionIndex) => (
                      <li key={actionIndex}>{action}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <style jsx>{`
        .learning-analytics-dashboard {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .dashboard-header {
          margin-bottom: 30px;
        }

        .dashboard-header h1 {
          font-size: 2rem;
          margin-bottom: 10px;
          color: #333;
        }

        .dashboard-header p {
          color: #666;
          margin-bottom: 20px;
        }

        .controls {
          display: flex;
          gap: 20px;
          align-items: center;
          flex-wrap: wrap;
        }

        .time-range-controls, .action-buttons {
          display: flex;
          gap: 10px;
          align-items: center;
        }

        .custom-date-range {
          display: flex;
          gap: 10px;
          align-items: center;
          margin-left: 10px;
        }

        .message {
          background: #e8f5e8;
          border: 1px solid #4caf50;
          color: #2e7d32;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .loading, .error, .empty-state {
          text-align: center;
          padding: 40px;
        }

        .error p {
          color: #d32f2f;
          margin-bottom: 10px;
        }

        .preference-summary, .interaction-patterns, .content-performance, 
        .learning-insights, .learning-recommendations, .preference-editor {
          margin-bottom: 30px;
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .preference-cards, .pattern-cards, .insights-grid, .recommendations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-top: 15px;
        }

        .preference-card, .pattern-card, .insight-category, .recommendation-card {
          background: #f8f9fa;
          border-radius: 6px;
          padding: 15px;
        }

        .preference-card h3, .pattern-card h3, .insight-category h3 {
          margin: 0 0 10px 0;
          font-size: 1.1rem;
          color: #333;
        }

        .preference-actions {
          margin-top: 15px;
        }

        .preference-form {
          max-width: 500px;
        }

        .form-group {
          margin-bottom: 15px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: 500;
        }

        .form-group input {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .form-actions {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }

        .device-breakdown p, .session-stats p {
          margin: 5px 0;
        }

        .content-controls {
          display: flex;
          gap: 20px;
          margin-bottom: 15px;
          align-items: center;
          flex-wrap: wrap;
        }

        .filter-controls, .sort-controls {
          display: flex;
          gap: 10px;
          align-items: center;
        }

        .sort-controls button {
          padding: 5px 10px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
        }

        .sort-controls button.active {
          background: #2196f3;
          color: white;
          border-color: #2196f3;
        }

        .content-performance-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 15px;
        }

        .content-performance-table th,
        .content-performance-table td {
          padding: 10px;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }

        .content-performance-table th {
          background: #f5f5f5;
          font-weight: 600;
        }

        .content-details {
          margin-top: 15px;
        }

        .detail-card {
          background: #f0f7ff;
          border: 1px solid #2196f3;
          border-radius: 6px;
          padding: 15px;
        }

        .detail-card h4 {
          margin: 0 0 10px 0;
          color: #1976d2;
        }

        .metrics {
          display: flex;
          gap: 20px;
          flex-wrap: wrap;
        }

        .metrics p {
          margin: 0;
          padding: 5px 10px;
          background: white;
          border-radius: 4px;
          border: 1px solid #e0e0e0;
        }

        .insight-category ul {
          margin: 0;
          padding-left: 20px;
        }

        .insight-category li {
          margin-bottom: 8px;
          line-height: 1.4;
        }

        .recommendation-card {
          border-left: 4px solid #2196f3;
        }

        .recommendation-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 10px;
        }

        .recommendation-header h3 {
          margin: 0;
          color: #333;
        }

        .priority {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .priority-high {
          background: #ffebee;
          color: #c62828;
        }

        .priority-medium {
          background: #fff3e0;
          color: #ef6c00;
        }

        .priority-low {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .recommendation-description {
          color: #666;
          margin-bottom: 10px;
          line-height: 1.4;
        }

        .recommendation-impact {
          color: #2196f3;
          font-weight: 500;
          margin-bottom: 15px;
        }

        .recommendation-actions h4 {
          margin: 0 0 8px 0;
          font-size: 0.9rem;
          color: #333;
        }

        .recommendation-actions ul {
          margin: 0;
          padding-left: 20px;
        }

        .recommendation-actions li {
          margin-bottom: 5px;
          font-size: 0.9rem;
          line-height: 1.3;
        }

        button {
          padding: 8px 16px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        button:hover {
          background: #f5f5f5;
        }

        button:active {
          background: #e0e0e0;
        }

        select, input {
          padding: 6px 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        label {
          font-weight: 500;
          margin-right: 8px;
        }

        @media (max-width: 768px) {
          .controls {
            flex-direction: column;
            align-items: stretch;
          }
          
          .content-controls {
            flex-direction: column;
            align-items: stretch;
          }
          
          .preference-cards, .pattern-cards, .insights-grid, .recommendations-grid {
            grid-template-columns: 1fr;
          }
          
          .metrics {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default LearningAnalytics;