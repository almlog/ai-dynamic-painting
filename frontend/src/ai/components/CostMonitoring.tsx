/**
 * CostMonitoring Component
 * TDD: GREEN phase - component implementation to pass tests
 */

import React, { useState, useEffect, useCallback } from 'react';

// Type definitions
interface CostBreakdown {
  videoGeneration: number;
  apiCalls: number;
  storage: number;
  processing: number;
}

interface MonthlyTrend {
  month: string;
  cost: number;
}

interface DailyCost {
  date: string;
  cost: number;
}

interface Usage {
  generationsThisMonth: number;
  totalGenerations: number;
  averageCostPerGeneration: number;
  peakUsageDay: string;
  peakUsageCost: number;
}

interface CostData {
  totalCost: number;
  currentMonth: number;
  previousMonth: number;
  dailyAverage: number;
  costBreakdown: CostBreakdown;
  monthlyTrend: MonthlyTrend[];
  dailyCosts: DailyCost[];
  usage: Usage | null;
}

interface BudgetSettings {
  monthlyBudget: number;
  dailyBudget: number;
  alertThresholds: {
    warning: number;
    critical: number;
  };
  autoStopEnabled: boolean;
  autoStopThreshold: number;
  notifications: {
    email: boolean;
    dashboard: boolean;
    webhook: boolean;
  };
}

interface CostProjections {
  endOfMonth: number;
  confidence: number;
  factors: string[];
  recommendations: string[];
}

interface CostAlert {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  dismissed: boolean;
}

// Mock API service for testing
const createMockApiService = () => ({
  getCostData: async (): Promise<CostData> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return {
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
  },

  getCostBreakdown: async (): Promise<CostBreakdown> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return {
      videoGeneration: 16.80,
      apiCalls: 4.20,
      storage: 2.15,
      processing: 1.60
    };
  },

  getBudgetSettings: async (): Promise<BudgetSettings> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return {
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
  },

  updateBudgetSettings: async (_settings: Partial<BudgetSettings>): Promise<{ success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { success: true };
  },

  getCostProjections: async (): Promise<CostProjections> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return {
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
  },

  exportCostReport: async (_params?: any): Promise<{ downloadUrl: string }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { downloadUrl: 'http://example.com/report.pdf' };
  },

  getCostAlerts: async (): Promise<CostAlert[]> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return [
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
  },

  dismissAlert: async (_alertId: string): Promise<{ success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 50));
    return { success: true };
  },

  createBudgetAlert: async (_alertConfig: any): Promise<{ id: string; success: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return { id: 'new_alert', success: true };
  }
});

const CostMonitoring: React.FC = () => {
  const [costData, setCostData] = useState<CostData | null>(null);
  const [budgetSettings, setBudgetSettings] = useState<BudgetSettings | null>(null);
  const [costProjections, setCostProjections] = useState<CostProjections | null>(null);
  const [costAlerts, setCostAlerts] = useState<CostAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingBudget, setEditingBudget] = useState(false);
  const [showDailyHistory, setShowDailyHistory] = useState(false);
  const [showExportOptions, setShowExportOptions] = useState(false);
  const [showCreateAlert, setShowCreateAlert] = useState(false);
  const [reportPeriod, setReportPeriod] = useState('last_30_days');
  const [message, setMessage] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  
  const [budgetForm, setBudgetForm] = useState({
    monthlyBudget: 25.00,
    dailyBudget: 1.00,
    autoStopEnabled: true,
    autoStopThreshold: 0.95
  });

  const [alertForm, setAlertForm] = useState({
    type: 'warning',
    threshold: 0.85,
    message: ''
  });

  const apiService = createMockApiService();

  const loadCostData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [costDataResult, budgetResult, projectionsResult, alertsResult] = await Promise.all([
        apiService.getCostData(),
        apiService.getBudgetSettings(),
        apiService.getCostProjections(),
        apiService.getCostAlerts()
      ]);
      
      setCostData(costDataResult);
      setBudgetSettings(budgetResult);
      setCostProjections(projectionsResult);
      setCostAlerts(alertsResult);
      setLastUpdated(new Date());
      
      // Set form values from budget settings
      setBudgetForm({
        monthlyBudget: budgetResult.monthlyBudget,
        dailyBudget: budgetResult.dailyBudget,
        autoStopEnabled: budgetResult.autoStopEnabled,
        autoStopThreshold: budgetResult.autoStopThreshold
      });
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load cost data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCostData();
  }, [loadCostData]);

  const handleRefresh = useCallback(() => {
    loadCostData();
  }, [loadCostData]);

  const handleRetry = useCallback(() => {
    loadCostData();
  }, [loadCostData]);

  const handleEditBudget = useCallback(() => {
    setEditingBudget(true);
  }, []);

  const handleSaveBudget = useCallback(async () => {
    try {
      await apiService.updateBudgetSettings({
        monthlyBudget: budgetForm.monthlyBudget,
        dailyBudget: budgetForm.dailyBudget,
        autoStopEnabled: budgetForm.autoStopEnabled,
        autoStopThreshold: budgetForm.autoStopThreshold
      });
      
      setEditingBudget(false);
      setMessage('Budget settings updated successfully');
      await loadCostData();
      
    } catch (err) {
      setMessage(`Error updating budget: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, [budgetForm, loadCostData]);

  const handleDismissAlert = useCallback(async (alertId: string) => {
    try {
      await apiService.dismissAlert(alertId);
      setCostAlerts(prev => prev.filter(alert => alert.id !== alertId));
      setMessage('Alert dismissed');
    } catch (err) {
      setMessage(`Error dismissing alert: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, []);

  const handleCreateAlert = useCallback(async () => {
    try {
      await apiService.createBudgetAlert({
        type: alertForm.type,
        threshold: alertForm.threshold,
        message: alertForm.message
      });
      
      setShowCreateAlert(false);
      setMessage('Budget alert created successfully');
      await loadCostData();
      
    } catch (err) {
      setMessage(`Error creating alert: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, [alertForm, loadCostData]);

  const handleExportReport = useCallback(async (format = 'pdf') => {
    try {
      const params = { 
        period: reportPeriod,
        format 
      };
      
      const result = await apiService.exportCostReport(params);
      setMessage('Report exported successfully');
      console.log('Export URL:', result.downloadUrl);
    } catch (err) {
      setMessage(`Export failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, [reportPeriod]);

  const getBudgetUtilization = useCallback(() => {
    if (!costData || !budgetSettings) return 0;
    return Math.round((costData.currentMonth / budgetSettings.monthlyBudget) * 100);
  }, [costData, budgetSettings]);

  const getBudgetStatus = useCallback(() => {
    const utilization = getBudgetUtilization();
    if (utilization >= 100) return 'exceeded';
    if (utilization >= 90) return 'critical';
    if (utilization >= 75) return 'warning';
    return 'normal';
  }, [getBudgetUtilization]);

  if (loading) {
    return (
      <div role="main" className="cost-monitoring-dashboard">
        <div className="loading">Loading cost monitoring...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div role="main" className="cost-monitoring-dashboard">
        <div className="error">
          <p>Failed to load cost data: {error}</p>
          <button onClick={handleRetry}>Retry</button>
        </div>
      </div>
    );
  }

  if (!costData || costData.totalCost === 0) {
    return (
      <div role="main" className="cost-monitoring-dashboard">
        <div className="empty-state">
          <p>No cost data available yet.</p>
          <button onClick={() => setMessage('Cost monitoring started')}>Start monitoring costs</button>
        </div>
      </div>
    );
  }

  const budgetUtilization = getBudgetUtilization();
  const budgetStatus = getBudgetStatus();

  return (
    <div role="main" className="cost-monitoring-dashboard">
      <header className="dashboard-header">
        <h1>Cost Monitoring Dashboard</h1>
        <p>Track and manage AI generation costs and budget utilization</p>
        
        <div className="controls">
          <div className="status-info">
            <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
            <span className="live-tracking">Live Tracking</span>
          </div>
          
          <div className="action-buttons">
            <button onClick={handleRefresh}>Refresh</button>
            <button onClick={() => setShowExportOptions(!showExportOptions)}>Export Options</button>
            <button onClick={() => handleExportReport()}>Export Report</button>
          </div>
        </div>
      </header>

      {message && (
        <div role="status" className="message" aria-live="polite">
          {message}
        </div>
      )}

      {/* Cost Summary Cards */}
      <section className="cost-summary">
        <h2>Cost Overview</h2>
        <div className="summary-cards">
          <div className="summary-card">
            <h3>Total Cost</h3>
            <p className="cost-amount">${costData.totalCost.toFixed(2)}</p>
          </div>
          <div className="summary-card">
            <h3>This Month</h3>
            <p className="cost-amount">${costData.currentMonth.toFixed(2)}</p>
          </div>
          <div className="summary-card">
            <h3>Previous Month</h3>
            <p className="cost-amount">${costData.previousMonth.toFixed(2)}</p>
          </div>
          <div className="summary-card">
            <h3>Daily Average</h3>
            <p className="cost-amount">${costData.dailyAverage.toFixed(2)}</p>
          </div>
        </div>
      </section>

      {/* Budget Management */}
      {budgetSettings && (
        <section className="budget-management">
          <h2>Budget Settings</h2>
          
          <div className="budget-overview">
            <div className="budget-info">
              <p>Monthly Budget: ${budgetSettings.monthlyBudget.toFixed(2)}</p>
              <p>Daily Budget: ${budgetSettings.dailyBudget.toFixed(2)}</p>
              {budgetSettings.autoStopEnabled && (
                <p>Auto-stop at {Math.round(budgetSettings.autoStopThreshold * 100)}%</p>
              )}
            </div>
            
            <div className="budget-utilization">
              <h3>Budget Utilization</h3>
              <div className="progress-container">
                <div 
                  role="progressbar"
                  aria-valuenow={budgetUtilization}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  className={`progress-bar ${budgetStatus}`}
                  style={{ width: `${Math.min(budgetUtilization, 100)}%` }}
                />
              </div>
              <p className={`utilization-text ${budgetStatus}`}>
                {budgetUtilization}%
              </p>
              
              {budgetStatus === 'exceeded' && (
                <p className="budget-alert critical">Budget exceeded!</p>
              )}
              {budgetStatus === 'critical' && (
                <p className="budget-alert warning">Approaching budget limit</p>
              )}
            </div>
            
            <div className="budget-actions">
              <button onClick={handleEditBudget}>Edit Budget</button>
            </div>
          </div>

          {editingBudget && (
            <div className="budget-editor">
              <h3>Edit Budget Settings</h3>
              <div className="budget-form">
                <div className="form-group">
                  <label htmlFor="monthlyBudget">Monthly Budget</label>
                  <input
                    id="monthlyBudget"
                    aria-label="Monthly Budget"
                    type="number"
                    step="0.01"
                    value={budgetForm.monthlyBudget}
                    onChange={(e) => setBudgetForm(prev => ({ 
                      ...prev, 
                      monthlyBudget: parseFloat(e.target.value) || 0 
                    }))}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="dailyBudget">Daily Budget</label>
                  <input
                    id="dailyBudget"
                    aria-label="Daily Budget"
                    type="number"
                    step="0.01"
                    value={budgetForm.dailyBudget}
                    onChange={(e) => setBudgetForm(prev => ({ 
                      ...prev, 
                      dailyBudget: parseFloat(e.target.value) || 0 
                    }))}
                  />
                </div>
                <div className="form-actions">
                  <button onClick={handleSaveBudget}>Save Budget</button>
                  <button onClick={() => setEditingBudget(false)}>Cancel</button>
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Cost Breakdown */}
      <section className="cost-breakdown">
        <h2>Cost Breakdown</h2>
        <div className="breakdown-chart">
          <div className="breakdown-item">
            <span>Video Generation: ${costData.costBreakdown.videoGeneration.toFixed(2)}</span>
          </div>
          <div className="breakdown-item">
            <span>API Calls: ${costData.costBreakdown.apiCalls.toFixed(2)}</span>
          </div>
          <div className="breakdown-item">
            <span>Storage: ${costData.costBreakdown.storage.toFixed(2)}</span>
          </div>
          <div className="breakdown-item">
            <span>Processing: ${costData.costBreakdown.processing.toFixed(2)}</span>
          </div>
        </div>
      </section>

      {/* Monthly Trend */}
      <section className="monthly-trend">
        <h2>Monthly Trend</h2>
        <div className="trend-chart">
          {costData.monthlyTrend.map((item, index) => (
            <div key={index} className="trend-item">
              <span>{item.month}: ${item.cost.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Usage Statistics */}
      {costData.usage && (
        <section className="usage-statistics">
          <h2>Usage Statistics</h2>
          <div className="usage-grid">
            <div className="usage-item">
              <p>{costData.usage.generationsThisMonth} generations this month</p>
            </div>
            <div className="usage-item">
              <p>{costData.usage.totalGenerations} total generations</p>
            </div>
            <div className="usage-item">
              <p>${costData.usage.averageCostPerGeneration.toFixed(2)} average per generation</p>
            </div>
            <div className="usage-item peak-usage">
              <h3>Peak Usage</h3>
              <p>{costData.usage.peakUsageDay}: ${costData.usage.peakUsageCost.toFixed(2)}</p>
            </div>
          </div>
          
          <div className="daily-history-toggle">
            <button onClick={() => setShowDailyHistory(!showDailyHistory)}>
              Daily History
            </button>
          </div>
          
          {showDailyHistory && (
            <div className="daily-history">
              <h3>Daily Cost History</h3>
              {costData.dailyCosts.map((day, index) => (
                <div key={index} className="daily-item">
                  <span>{day.date}: ${day.cost.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Cost Alerts */}
      {costAlerts.length > 0 && (
        <section className="cost-alerts">
          <h2>Cost Alerts</h2>
          <div className="alerts-container">
            {costAlerts.map((alert) => (
              <div key={alert.id} className={`alert alert-${alert.type}`}>
                <div className="alert-header">
                  <h3>{alert.title}</h3>
                  <span className={`alert-type ${alert.type}`}>{alert.type}</span>
                </div>
                <p className="alert-message">{alert.message}</p>
                <div className="alert-actions">
                  <button onClick={() => handleDismissAlert(alert.id)}>Dismiss</button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="alert-management">
            <button onClick={() => setShowCreateAlert(!showCreateAlert)}>Create Alert</button>
          </div>
          
          {showCreateAlert && (
            <div className="create-alert">
              <h3>Create Budget Alert</h3>
              <div className="alert-form">
                <div className="form-group">
                  <label htmlFor="alertType">Alert Type</label>
                  <select
                    id="alertType"
                    aria-label="Alert Type"
                    value={alertForm.type}
                    onChange={(e) => setAlertForm(prev => ({ ...prev, type: e.target.value }))}
                  >
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="alertThreshold">Threshold</label>
                  <input
                    id="alertThreshold"
                    aria-label="Threshold"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={alertForm.threshold}
                    onChange={(e) => setAlertForm(prev => ({ 
                      ...prev, 
                      threshold: parseFloat(e.target.value) || 0 
                    }))}
                  />
                </div>
                <div className="form-actions">
                  <button onClick={handleCreateAlert}>Create Alert</button>
                  <button onClick={() => setShowCreateAlert(false)}>Cancel</button>
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Cost Projections */}
      {costProjections && (
        <section className="cost-projections">
          <h2>Cost Projections</h2>
          
          <div className="projection-summary">
            <p>End of Month: ${costProjections.endOfMonth.toFixed(2)}</p>
            <p>Confidence: {Math.round(costProjections.confidence * 100)}%</p>
          </div>
          
          <div className="projection-details">
            <div className="projection-factors">
              <h3>Projection Factors</h3>
              <ul>
                {costProjections.factors.map((factor, index) => (
                  <li key={index}>{factor}</li>
                ))}
              </ul>
            </div>
            
            <div className="projection-recommendations">
              <h3>Recommendations</h3>
              <ul>
                {costProjections.recommendations.map((recommendation, index) => (
                  <li key={index}>{recommendation}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}

      {/* Export Options */}
      {showExportOptions && (
        <section className="export-options">
          <h2>Export Options</h2>
          
          <div className="export-controls">
            <div className="form-group">
              <label htmlFor="reportPeriod">Report Period</label>
              <select
                id="reportPeriod"
                aria-label="Report Period"
                value={reportPeriod}
                onChange={(e) => setReportPeriod(e.target.value)}
              >
                <option value="last_7_days">Last 7 Days</option>
                <option value="last_30_days">Last 30 Days</option>
                <option value="last_90_days">Last 90 Days</option>
                <option value="current_month">Current Month</option>
              </select>
            </div>
            
            <div className="export-formats">
              <button onClick={() => handleExportReport('pdf')}>PDF Report</button>
              <button onClick={() => handleExportReport('csv')}>CSV Data</button>
              <button onClick={() => handleExportReport('json')}>JSON Export</button>
            </div>
            
            <div className="export-actions">
              <button onClick={() => handleExportReport()}>Generate Report</button>
            </div>
          </div>
        </section>
      )}

      <style>{`
        .cost-monitoring-dashboard {
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
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 20px;
        }

        .status-info {
          display: flex;
          gap: 15px;
          align-items: center;
          font-size: 0.9rem;
          color: #666;
        }

        .live-tracking {
          background: #4caf50;
          color: white;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.8rem;
        }

        .action-buttons {
          display: flex;
          gap: 10px;
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

        .cost-summary, .budget-management, .cost-breakdown, .monthly-trend,
        .usage-statistics, .cost-alerts, .cost-projections, .export-options {
          margin-bottom: 30px;
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .summary-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-top: 15px;
        }

        .summary-card {
          background: #f8f9fa;
          border-radius: 6px;
          padding: 15px;
          text-align: center;
        }

        .summary-card h3 {
          margin: 0 0 10px 0;
          font-size: 1rem;
          color: #666;
        }

        .cost-amount {
          font-size: 1.8rem;
          font-weight: bold;
          color: #333;
          margin: 0;
        }

        .budget-overview {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
        }

        .budget-info p {
          margin: 8px 0;
          font-size: 1rem;
        }

        .budget-utilization {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 6px;
        }

        .progress-container {
          width: 100%;
          height: 20px;
          background: #e0e0e0;
          border-radius: 10px;
          overflow: hidden;
          margin: 10px 0;
        }

        .progress-bar {
          height: 100%;
          transition: width 0.3s ease;
        }

        .progress-bar.normal {
          background: #4caf50;
        }

        .progress-bar.warning {
          background: #ff9800;
        }

        .progress-bar.critical {
          background: #f44336;
        }

        .progress-bar.exceeded {
          background: #d32f2f;
        }

        .utilization-text {
          font-size: 1.2rem;
          font-weight: bold;
          margin: 10px 0;
        }

        .utilization-text.normal {
          color: #4caf50;
        }

        .utilization-text.warning {
          color: #ff9800;
        }

        .utilization-text.critical, .utilization-text.exceeded {
          color: #f44336;
        }

        .budget-alert {
          padding: 8px 12px;
          border-radius: 4px;
          margin-top: 10px;
          font-weight: 500;
        }

        .budget-alert.warning {
          background: #fff3cd;
          color: #856404;
          border: 1px solid #ffeaa7;
        }

        .budget-alert.critical {
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }

        .budget-editor {
          margin-top: 20px;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 6px;
        }

        .budget-form, .alert-form {
          max-width: 400px;
        }

        .form-group {
          margin-bottom: 15px;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: 500;
        }

        .form-group input, .form-group select {
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

        .breakdown-chart, .trend-chart {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-top: 15px;
        }

        .breakdown-item, .trend-item {
          background: #f8f9fa;
          padding: 12px;
          border-radius: 4px;
          text-align: center;
        }

        .usage-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-top: 15px;
        }

        .usage-item {
          background: #f8f9fa;
          padding: 12px;
          border-radius: 4px;
        }

        .usage-item p {
          margin: 0;
          font-size: 1rem;
        }

        .peak-usage {
          border-left: 4px solid #2196f3;
        }

        .peak-usage h3 {
          margin: 0 0 8px 0;
          font-size: 1rem;
          color: #2196f3;
        }

        .daily-history-toggle {
          margin-top: 15px;
        }

        .daily-history {
          margin-top: 15px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 6px;
        }

        .daily-item {
          padding: 5px 0;
          border-bottom: 1px solid #e0e0e0;
        }

        .daily-item:last-child {
          border-bottom: none;
        }

        .alerts-container {
          margin-top: 15px;
        }

        .alert {
          margin-bottom: 15px;
          padding: 15px;
          border-radius: 6px;
          border-left: 4px solid;
        }

        .alert-info {
          background: #e3f2fd;
          border-left-color: #2196f3;
        }

        .alert-warning {
          background: #fff3e0;
          border-left-color: #ff9800;
        }

        .alert-critical {
          background: #ffebee;
          border-left-color: #f44336;
        }

        .alert-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .alert-header h3 {
          margin: 0;
          font-size: 1.1rem;
        }

        .alert-type {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .alert-type.info {
          background: #2196f3;
          color: white;
        }

        .alert-type.warning {
          background: #ff9800;
          color: white;
        }

        .alert-type.critical {
          background: #f44336;
          color: white;
        }

        .alert-message {
          margin: 0 0 10px 0;
          line-height: 1.4;
        }

        .alert-actions {
          display: flex;
          gap: 10px;
        }

        .create-alert {
          margin-top: 15px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 6px;
        }

        .projection-summary {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 6px;
          margin-bottom: 15px;
        }

        .projection-summary p {
          margin: 5px 0;
          font-size: 1.1rem;
        }

        .projection-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .projection-factors, .projection-recommendations {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 6px;
        }

        .projection-factors h3, .projection-recommendations h3 {
          margin: 0 0 10px 0;
          color: #333;
        }

        .projection-factors ul, .projection-recommendations ul {
          margin: 0;
          padding-left: 20px;
        }

        .projection-factors li, .projection-recommendations li {
          margin-bottom: 8px;
          line-height: 1.4;
        }

        .export-controls {
          max-width: 500px;
        }

        .export-formats {
          display: flex;
          gap: 10px;
          margin: 15px 0;
          flex-wrap: wrap;
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
          font-size: 14px;
        }

        label {
          font-weight: 500;
        }

        @media (max-width: 768px) {
          .controls {
            flex-direction: column;
            align-items: stretch;
          }

          .budget-overview {
            grid-template-columns: 1fr;
          }

          .summary-cards, .breakdown-chart, .trend-chart, .usage-grid {
            grid-template-columns: 1fr;
          }

          .projection-details {
            grid-template-columns: 1fr;
          }

          .export-formats {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default CostMonitoring;