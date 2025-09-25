/**
 * CostManagementPanel - Dedicated component for cost and budget management display
 * T6-005: REFACTOR - Extracted from VideoGenerationDashboard for better separation of concerns
 */

import React from 'react';

// Cost data interface
interface CostData {
  totalCost: number;
  remainingBudget: number;
  dailyBudgetLimit: number;
}

// Component props interface
interface CostManagementPanelProps {
  costData?: CostData;
  className?: string;
}

const CostManagementPanel: React.FC<CostManagementPanelProps> = ({
  costData = {
    totalCost: 0,
    remainingBudget: 10,
    dailyBudgetLimit: 10
  },
  className = ''
}) => {
  // Cost formatting utility
  const formatCost = (cost: number | undefined | null) => {
    if (cost === undefined || cost === null || isNaN(cost)) {
      return '$0.00';
    }
    return `$${cost.toFixed(2)}`;
  };

  // Calculate usage percentage for potential visual indicators
  const usagePercentage = costData.dailyBudgetLimit > 0 
    ? ((costData.dailyBudgetLimit - costData.remainingBudget) / costData.dailyBudgetLimit) * 100 
    : 0;

  // Determine alert level based on usage
  const getAlertLevel = () => {
    if (usagePercentage >= 90) return 'danger';
    if (usagePercentage >= 75) return 'warning';
    return 'normal';
  };

  const alertLevel = getAlertLevel();

  // Alert styling based on usage level
  const getPanelStyle = () => {
    const baseStyle = 'mb-8 p-6 border rounded-lg';
    switch (alertLevel) {
      case 'danger':
        return `${baseStyle} bg-red-50 border-red-200`;
      case 'warning':
        return `${baseStyle} bg-yellow-50 border-yellow-200`;
      default:
        return `${baseStyle} bg-blue-50 border-blue-200`;
    }
  };

  return (
    <div className={`${getPanelStyle()} ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Daily Budget</h2>
        {alertLevel !== 'normal' && (
          <div className={`px-3 py-1 rounded text-sm font-medium ${
            alertLevel === 'danger' 
              ? 'bg-red-100 text-red-800' 
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {alertLevel === 'danger' ? '⚠️ Budget Critical' : '⚠️ Budget Warning'}
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <span className="text-sm text-gray-600">Total Cost</span>
          <div className="text-2xl font-bold">{formatCost(costData.totalCost)}</div>
          <div className="text-xs text-gray-500 mt-1">
            {usagePercentage.toFixed(1)}% of budget used
          </div>
        </div>
        
        <div>
          <span className="text-sm text-gray-600">Remaining Budget</span>
          <div className={`text-2xl font-bold ${
            alertLevel === 'danger' ? 'text-red-600' : 
            alertLevel === 'warning' ? 'text-yellow-600' : 'text-gray-900'
          }`}>
            {formatCost(costData.remainingBudget)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Available for today
          </div>
        </div>
        
        <div>
          <span className="text-sm text-gray-600">Budget Limit</span>
          <div className="text-2xl font-bold">{formatCost(costData.dailyBudgetLimit)}</div>
          <div className="text-xs text-gray-500 mt-1">
            Daily maximum
          </div>
        </div>
      </div>

      {/* Usage Progress Bar */}
      {usagePercentage > 0 && (
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Budget Usage</span>
            <span>{usagePercentage.toFixed(1)}%</span>
          </div>
          <div className="bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                alertLevel === 'danger' ? 'bg-red-500' :
                alertLevel === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
              }`}
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CostManagementPanel;