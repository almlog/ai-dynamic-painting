"""
Integration tests for AI Cost Management System
Tests comprehensive cost tracking, budget enforcement, and alert systems
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any


class MockCostTracker:
    """Mock cost tracking service for integration testing"""
    
    def __init__(self):
        self.usage_history = []
        self.current_usage = 0.0
        self.budget_limit = 10.0  # $10 daily budget
        self.alert_threshold = 0.8  # 80% budget threshold
        self.is_tracking = False
        
    def start_tracking(self):
        """Start cost tracking session"""
        self.is_tracking = True
        self.session_start = datetime.now()
        
    def stop_tracking(self):
        """Stop cost tracking session"""
        self.is_tracking = False
        session_duration = datetime.now() - self.session_start
        return {
            'session_duration': session_duration.total_seconds(),
            'total_cost': self.current_usage,
            'operations_count': len(self.usage_history)
        }
        
    def record_operation(self, operation_type: str, cost: float, metadata: Dict = None):
        """Record a cost operation"""
        if not self.is_tracking:
            raise RuntimeError("Cost tracking not started")
            
        operation = {
            'timestamp': datetime.now(),
            'type': operation_type,
            'cost': cost,
            'metadata': metadata or {},
            'running_total': self.current_usage + cost
        }
        
        self.usage_history.append(operation)
        self.current_usage += cost
        
        # Check for budget alerts
        if self.current_usage >= self.budget_limit * self.alert_threshold:
            return {
                'alert': True,
                'alert_type': 'budget_threshold',
                'usage_percentage': (self.current_usage / self.budget_limit) * 100,
                'remaining_budget': self.budget_limit - self.current_usage
            }
        
        return {'alert': False, 'current_usage': self.current_usage}
        
    def get_daily_usage(self, date: datetime = None) -> Dict:
        """Get usage summary for specific date"""
        target_date = date or datetime.now()
        daily_operations = [
            op for op in self.usage_history 
            if op['timestamp'].date() == target_date.date()
        ]
        
        return {
            'date': target_date.date(),
            'total_cost': sum(op['cost'] for op in daily_operations),
            'operations_count': len(daily_operations),
            'budget_utilization': (sum(op['cost'] for op in daily_operations) / self.budget_limit) * 100,
            'operations': daily_operations
        }


class MockBudgetManager:
    """Mock budget management service"""
    
    def __init__(self):
        self.budgets = {
            'daily': 10.0,
            'weekly': 60.0,
            'monthly': 200.0
        }
        self.current_usage = {
            'daily': 0.0,
            'weekly': 0.0, 
            'monthly': 0.0
        }
        self.alerts_enabled = True
        
    def check_budget_status(self, period: str = 'daily') -> Dict:
        """Check current budget status"""
        if period not in self.budgets:
            raise ValueError(f"Invalid period: {period}")
            
        usage = self.current_usage[period]
        limit = self.budgets[period]
        utilization = (usage / limit) * 100
        
        return {
            'period': period,
            'usage': usage,
            'limit': limit,
            'utilization_percentage': utilization,
            'remaining': limit - usage,
            'status': 'ok' if utilization < 80 else 'warning' if utilization < 100 else 'exceeded'
        }
        
    def enforce_budget(self, requested_cost: float, period: str = 'daily') -> Dict:
        """Enforce budget limits before operation"""
        current_status = self.check_budget_status(period)
        
        if current_status['remaining'] < requested_cost:
            return {
                'allowed': False,
                'reason': 'insufficient_budget',
                'current_usage': current_status['usage'],
                'remaining': current_status['remaining'],
                'requested': requested_cost
            }
            
        return {
            'allowed': True,
            'projected_usage': current_status['usage'] + requested_cost,
            'projected_utilization': ((current_status['usage'] + requested_cost) / current_status['limit']) * 100
        }
        
    def update_usage(self, cost: float, period: str = 'daily'):
        """Update usage for specific period"""
        if period in self.current_usage:
            self.current_usage[period] += cost


class MockAlertSystem:
    """Mock alert system for cost notifications"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = [
            {'threshold': 0.5, 'message': '50% budget used'},
            {'threshold': 0.8, 'message': '80% budget warning'},
            {'threshold': 1.0, 'message': 'Budget exceeded!'}
        ]
        
    def check_alerts(self, usage_percentage: float) -> List[Dict]:
        """Check if any alerts should be triggered"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if usage_percentage >= rule['threshold'] * 100:
                alert = {
                    'timestamp': datetime.now(),
                    'level': 'warning' if rule['threshold'] < 1.0 else 'critical',
                    'message': rule['message'],
                    'usage_percentage': usage_percentage,
                    'threshold': rule['threshold']
                }
                triggered_alerts.append(alert)
                
        return triggered_alerts
        
    def send_alert(self, alert: Dict) -> bool:
        """Send alert notification"""
        self.alerts.append(alert)
        return True  # Assume successful send
        
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from recent time period"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alerts 
            if alert['timestamp'] > cutoff
        ]


@pytest.fixture
def cost_tracker():
    """Create cost tracker instance for testing"""
    return MockCostTracker()


@pytest.fixture  
def budget_manager():
    """Create budget manager instance for testing"""
    return MockBudgetManager()


@pytest.fixture
def alert_system():
    """Create alert system instance for testing"""
    return MockAlertSystem()


@pytest.fixture
def integrated_cost_system(cost_tracker, budget_manager, alert_system):
    """Create integrated cost management system"""
    return {
        'tracker': cost_tracker,
        'budget': budget_manager,
        'alerts': alert_system
    }


class TestAICostManagementIntegration:
    """Integration tests for AI cost management system"""
    
    def test_basic_cost_tracking_flow(self, integrated_cost_system):
        """Test basic cost tracking workflow"""
        tracker = integrated_cost_system['tracker']
        
        # Start tracking
        tracker.start_tracking()
        assert tracker.is_tracking is True
        
        # Record some operations
        result1 = tracker.record_operation('video_generation', 0.25, {'duration': 30})
        assert result1['alert'] is False
        assert result1['current_usage'] == 0.25
        
        result2 = tracker.record_operation('prompt_enhancement', 0.05, {'tokens': 1000})
        assert result2['current_usage'] == 0.30
        
        # Stop tracking
        summary = tracker.stop_tracking()
        assert summary['total_cost'] == 0.30
        assert summary['operations_count'] == 2
        
    def test_budget_enforcement_integration(self, integrated_cost_system):
        """Test budget enforcement with cost tracking"""
        tracker = integrated_cost_system['tracker']
        budget = integrated_cost_system['budget']
        
        tracker.start_tracking()
        
        # Test operation within budget
        enforcement_result = budget.enforce_budget(2.0)
        assert enforcement_result['allowed'] is True
        
        # Record the operation
        tracker.record_operation('large_video_generation', 2.0)
        budget.update_usage(2.0)
        
        # Check budget status
        status = budget.check_budget_status()
        assert status['usage'] == 2.0
        assert status['utilization_percentage'] == 20.0
        
        # Test operation that would exceed budget
        enforcement_result = budget.enforce_budget(9.0)  # Would exceed $10 limit
        assert enforcement_result['allowed'] is False
        assert enforcement_result['reason'] == 'insufficient_budget'
        
    def test_alert_system_integration(self, integrated_cost_system):
        """Test alert system integration with cost tracking"""
        tracker = integrated_cost_system['tracker']
        budget = integrated_cost_system['budget']
        alerts = integrated_cost_system['alerts']
        
        tracker.start_tracking()
        
        # Gradually increase usage to trigger alerts
        operations = [
            ('video_gen_1', 3.0),  # 30% usage
            ('video_gen_2', 2.5),  # 55% usage (should trigger 50% alert)
            ('video_gen_3', 2.0),  # 75% usage
            ('video_gen_4', 1.5),  # 90% usage (should trigger 80% alert)
        ]
        
        alert_count = 0
        for op_name, cost in operations:
            # Check budget before operation
            enforcement = budget.enforce_budget(cost)
            if enforcement['allowed']:
                # Record operation
                tracker.record_operation(op_name, cost)
                budget.update_usage(cost)
                
                # Check for alerts
                status = budget.check_budget_status()
                triggered_alerts = alerts.check_alerts(status['utilization_percentage'])
                
                # Send alerts
                for alert in triggered_alerts:
                    alerts.send_alert(alert)
                    alert_count += 1
        
        # Verify alerts were triggered
        recent_alerts = alerts.get_recent_alerts()
        assert len(recent_alerts) >= 2  # At least 50% and 80% alerts
        
    def test_daily_usage_reporting(self, integrated_cost_system):
        """Test daily usage reporting integration"""
        tracker = integrated_cost_system['tracker']
        
        tracker.start_tracking()
        
        # Simulate various operations throughout the day
        operations = [
            ('morning_generation', 1.5, {'time': 'morning'}),
            ('afternoon_enhancement', 0.8, {'time': 'afternoon'}),
            ('evening_generation', 2.2, {'time': 'evening'})
        ]
        
        for op_name, cost, metadata in operations:
            tracker.record_operation(op_name, cost, metadata)
            
        # Get daily usage report
        daily_report = tracker.get_daily_usage()
        
        assert daily_report['total_cost'] == 4.5
        assert daily_report['operations_count'] == 3
        assert daily_report['budget_utilization'] == 45.0  # 4.5/10 * 100
        assert len(daily_report['operations']) == 3
        
    def test_multi_period_budget_tracking(self, budget_manager):
        """Test budget tracking across multiple periods"""
        # Set usage for different periods
        budget_manager.update_usage(5.0, 'daily')    # 50% of daily
        budget_manager.update_usage(25.0, 'weekly')  # ~42% of weekly  
        budget_manager.update_usage(80.0, 'monthly') # 40% of monthly
        
        # Check status for each period
        daily_status = budget_manager.check_budget_status('daily')
        weekly_status = budget_manager.check_budget_status('weekly')
        monthly_status = budget_manager.check_budget_status('monthly')
        
        assert daily_status['utilization_percentage'] == 50.0
        assert daily_status['status'] == 'ok'
        
        assert weekly_status['utilization_percentage'] == pytest.approx(41.67, rel=1e-2)
        assert weekly_status['status'] == 'ok'
        
        assert monthly_status['utilization_percentage'] == 40.0
        assert monthly_status['status'] == 'ok'
        
    def test_cost_optimization_scenarios(self, integrated_cost_system):
        """Test cost optimization integration scenarios"""
        tracker = integrated_cost_system['tracker']
        budget = integrated_cost_system['budget']
        
        tracker.start_tracking()
        
        # Scenario 1: Cost-efficient small operations
        small_ops = [('small_gen_{}'.format(i), 0.1) for i in range(20)]
        for op_name, cost in small_ops:
            tracker.record_operation(op_name, cost)
            budget.update_usage(cost)
            
        daily_report = tracker.get_daily_usage()
        assert daily_report['total_cost'] == pytest.approx(2.0, rel=1e-2)  # 20 * 0.1
        assert daily_report['operations_count'] == 20
        
        # Scenario 2: Verify cost efficiency
        avg_cost_per_op = daily_report['total_cost'] / daily_report['operations_count']
        assert avg_cost_per_op == pytest.approx(0.1, rel=1e-2)  # Efficient operations
        
        # Scenario 3: Budget still has room
        status = budget.check_budget_status()
        assert status['remaining'] == pytest.approx(8.0, rel=1e-2)
        assert status['status'] == 'ok'
        
    def test_error_handling_and_recovery(self, integrated_cost_system):
        """Test error handling in cost management integration"""
        tracker = integrated_cost_system['tracker']
        budget = integrated_cost_system['budget']
        
        # Test recording without starting tracking
        with pytest.raises(RuntimeError):
            tracker.record_operation('invalid_op', 1.0)
            
        # Test invalid budget period
        with pytest.raises(ValueError):
            budget.check_budget_status('invalid_period')
            
        # Test recovery after error
        tracker.start_tracking()  # Proper initialization
        result = tracker.record_operation('recovery_op', 0.5)
        assert result['alert'] is False
        assert result['current_usage'] == 0.5
        
    def test_comprehensive_cost_management_workflow(self, integrated_cost_system):
        """Test complete cost management workflow integration"""
        tracker = integrated_cost_system['tracker']
        budget = integrated_cost_system['budget'] 
        alerts = integrated_cost_system['alerts']
        
        # Initialize system
        tracker.start_tracking()
        
        # Simulate realistic daily usage pattern
        workflow_operations = [
            # Morning batch
            ('morning_weather_check', 0.02, {'type': 'api_call'}),
            ('morning_prompt_gen', 0.15, {'type': 'prompt_generation'}),
            ('morning_video_gen', 1.8, {'type': 'video_generation', 'duration': 45}),
            
            # Afternoon optimization
            ('afternoon_context_opt', 0.08, {'type': 'context_optimization'}),
            ('afternoon_video_gen', 2.1, {'type': 'video_generation', 'duration': 60}),
            
            # Evening learning
            ('evening_preference_learn', 0.12, {'type': 'learning_update'}),
            ('evening_video_gen', 1.9, {'type': 'video_generation', 'duration': 50}),
        ]
        
        total_operations = 0
        total_cost = 0.0
        
        for op_name, cost, metadata in workflow_operations:
            # Pre-operation budget check
            enforcement = budget.enforce_budget(cost)
            
            if enforcement['allowed']:
                # Execute operation
                result = tracker.record_operation(op_name, cost, metadata)
                budget.update_usage(cost)
                total_operations += 1
                total_cost += cost
                
                # Check and handle alerts
                status = budget.check_budget_status()
                triggered_alerts = alerts.check_alerts(status['utilization_percentage'])
                
                for alert in triggered_alerts:
                    alerts.send_alert(alert)
            else:
                # Log budget rejection
                print(f"Operation {op_name} rejected: {enforcement['reason']}")
                
        # Final system validation
        final_summary = tracker.stop_tracking()
        final_status = budget.check_budget_status()
        recent_alerts = alerts.get_recent_alerts()
        
        # Assertions for complete workflow
        assert final_summary['operations_count'] == total_operations
        assert final_summary['total_cost'] == pytest.approx(total_cost, rel=1e-2)
        assert final_status['usage'] == pytest.approx(total_cost, rel=1e-2)
        assert final_status['utilization_percentage'] <= 100.0  # Should not exceed budget
        
        # Verify realistic usage pattern
        assert 6.0 <= total_cost <= 8.0  # Realistic daily AI usage
        assert total_operations == 7  # All operations should succeed
        assert len(recent_alerts) >= 1  # Should trigger at least one alert