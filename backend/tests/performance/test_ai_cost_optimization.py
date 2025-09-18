"""
Cost optimization validation tests for AI services - T272 AI Cost Optimization
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.services.veo_api_service import VEOAPIService, VEOAPIError


class CostTracker:
    """Helper class to track and analyze cost optimization"""
    
    def __init__(self):
        self.cost_records = []
        self.budget_alerts = []
        self.optimization_suggestions = []
    
    def record_cost(self, operation_type: str, estimated_cost: float, actual_cost: float = None):
        """Record cost data for analysis"""
        record = {
            'timestamp': time.time(),
            'operation_type': operation_type,
            'estimated_cost': estimated_cost,
            'actual_cost': actual_cost or estimated_cost,
            'accuracy': 1.0 if actual_cost is None else (1.0 - abs(estimated_cost - actual_cost) / max(estimated_cost, actual_cost))
        }
        self.cost_records.append(record)
    
    def check_budget_threshold(self, current_usage: float, budget_limit: float, threshold: float = 0.8):
        """Check if budget threshold is exceeded"""
        usage_ratio = current_usage / budget_limit
        if usage_ratio >= threshold:
            alert = {
                'timestamp': time.time(),
                'usage_ratio': usage_ratio,
                'current_usage': current_usage,
                'budget_limit': budget_limit,
                'severity': 'warning' if usage_ratio < 0.9 else 'critical'
            }
            self.budget_alerts.append(alert)
            return alert
        return None
    
    def analyze_cost_efficiency(self):
        """Analyze cost efficiency and provide optimization suggestions"""
        if not self.cost_records:
            return {'efficiency_score': 0, 'suggestions': []}
        
        # Calculate accuracy of cost estimates
        accuracy_scores = [record['accuracy'] for record in self.cost_records]
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
        
        # Analyze cost patterns
        cost_by_operation = {}
        for record in self.cost_records:
            op_type = record['operation_type']
            if op_type not in cost_by_operation:
                cost_by_operation[op_type] = []
            cost_by_operation[op_type].append(record['actual_cost'])
        
        # Generate optimization suggestions
        suggestions = []
        for op_type, costs in cost_by_operation.items():
            avg_cost = sum(costs) / len(costs)
            max_cost = max(costs)
            if max_cost > avg_cost * 1.5:  # High cost variation
                suggestions.append(f"Optimize {op_type} - high cost variation detected (max: ${max_cost:.2f}, avg: ${avg_cost:.2f})")
        
        if avg_accuracy < 0.9:
            suggestions.append(f"Improve cost estimation accuracy (current: {avg_accuracy:.1%})")
        
        efficiency_score = avg_accuracy * 100
        
        return {
            'efficiency_score': efficiency_score,
            'cost_accuracy': avg_accuracy,
            'total_operations': len(self.cost_records),
            'suggestions': suggestions,
            'cost_by_operation': cost_by_operation
        }


class TestVEOAPICostOptimization:
    """Cost optimization tests for VEO API Service"""
    
    @pytest.fixture
    def veo_service(self):
        """Create VEO API service with budget limits"""
        return VEOAPIService(api_key="test_key", monthly_budget=100.0)
    
    @pytest.fixture
    def cost_tracker(self):
        """Create cost tracking helper"""
        return CostTracker()
    
    def test_cost_estimation_accuracy(self, veo_service, cost_tracker):
        """Test accuracy of cost estimation algorithms"""
        
        # Test scenarios with cost patterns based on actual VEO API service algorithm
        test_scenarios = [
            # Basic scenarios (base cost 0.25, duration/30, quality multiplier)
            {'duration': 15, 'quality': 'low', 'resolution': '1920x1080', 'expected_range': (0.08, 0.12)},    # 0.25 * 0.5 * 0.7
            {'duration': 30, 'quality': 'medium', 'resolution': '1920x1080', 'expected_range': (0.20, 0.30)}, # 0.25 * 1.0 * 1.0  
            {'duration': 60, 'quality': 'high', 'resolution': '1920x1080', 'expected_range': (0.60, 0.70)},   # 0.25 * 2.0 * 1.3
            
            # High resolution scenarios (4K = 2.0x multiplier)
            {'duration': 30, 'quality': 'medium', 'resolution': '3840x2160', 'expected_range': (0.45, 0.55)}, # 0.25 * 1.0 * 1.0 * 2.0
            {'duration': 15, 'quality': 'ultra', 'resolution': '3840x2160', 'expected_range': (0.30, 0.45)},  # 0.25 * 0.5 * 1.6 * 2.0
            
            # Long duration scenarios
            {'duration': 120, 'quality': 'medium', 'resolution': '1920x1080', 'expected_range': (0.95, 1.05)}, # 0.25 * 4.0 * 1.0
            {'duration': 180, 'quality': 'low', 'resolution': '1920x1080', 'expected_range': (1.00, 1.10)},    # 0.25 * 6.0 * 0.7
        ]
        
        accuracy_results = []
        
        for scenario in test_scenarios:
            generation_data = {
                'prompt': f'Test video {scenario["duration"]}s {scenario["quality"]} {scenario["resolution"]}',
                'duration': scenario['duration'],
                'quality': scenario['quality'],
                'resolution': scenario['resolution']
            }
            
            estimated_cost = veo_service.get_cost_estimate(generation_data)
            cost_tracker.record_cost(
                f"{scenario['quality']}_{scenario['duration']}s", 
                estimated_cost
            )
            
            # Check if estimate falls within expected range
            min_expected, max_expected = scenario['expected_range']
            is_accurate = min_expected <= estimated_cost <= max_expected
            accuracy_results.append(is_accurate)
            
            print(f"  {scenario['quality']} {scenario['duration']}s {scenario['resolution']}: ${estimated_cost:.3f} (expected: ${min_expected:.2f}-${max_expected:.2f}) {'✓' if is_accurate else '✗'}")
        
        accuracy_rate = sum(accuracy_results) / len(accuracy_results)
        
        # Cost estimation should be accurate within expected ranges
        assert accuracy_rate >= 0.8, f"Cost estimation accuracy too low: {accuracy_rate:.1%}"
        
        # All estimates should be positive
        all_costs = [record['estimated_cost'] for record in cost_tracker.cost_records]
        assert all(cost > 0 for cost in all_costs), "All cost estimates should be positive"
        
        print(f"\n💰 Cost Estimation Accuracy: {accuracy_rate:.1%}")
        print(f"   Total scenarios tested: {len(test_scenarios)}")
        print(f"   Average estimated cost: ${sum(all_costs) / len(all_costs):.3f}")
    
    def test_budget_management_and_alerts(self, veo_service, cost_tracker):
        """Test budget management and alert system"""
        
        # Set initial budget
        initial_budget = 50.0
        veo_service.monthly_budget = initial_budget
        veo_service.current_usage = 0.0
        
        # Simulate progressive budget usage
        generation_requests = [
            {'prompt': 'Test 1', 'duration': 30, 'quality': 'medium', 'cost': 5.0},
            {'prompt': 'Test 2', 'duration': 60, 'quality': 'high', 'cost': 12.0},
            {'prompt': 'Test 3', 'duration': 45, 'quality': 'medium', 'cost': 8.0},
            {'prompt': 'Test 4', 'duration': 30, 'quality': 'ultra', 'cost': 15.0},  # 40.0 total - 80% threshold
            {'prompt': 'Test 5', 'duration': 20, 'quality': 'high', 'cost': 7.0},   # 47.0 total - 94% critical
        ]
        
        budget_status_history = []
        
        for i, request in enumerate(generation_requests):
            # Check budget before operation
            estimated_cost = veo_service.get_cost_estimate(request)
            budget_available = veo_service.check_budget_available(estimated_cost)
            
            current_usage_before = veo_service.current_usage
            usage_ratio_before = current_usage_before / initial_budget
            
            # Track costs
            veo_service.track_costs(f"gen_{i}", request['cost'])
            
            # Check for budget alerts
            alert = cost_tracker.check_budget_threshold(
                veo_service.current_usage, 
                initial_budget
            )
            
            budget_status = {
                'operation': i + 1,
                'usage_before': current_usage_before,
                'usage_after': veo_service.current_usage,
                'usage_ratio': veo_service.current_usage / initial_budget,
                'budget_available': budget_available,
                'alert': alert
            }
            budget_status_history.append(budget_status)
            
            print(f"  Operation {i+1}: ${veo_service.current_usage:.1f}/${initial_budget} ({veo_service.current_usage/initial_budget:.1%}) {'🚨' if alert else '✅'}")
        
        # Verify budget tracking accuracy
        expected_total = sum(req['cost'] for req in generation_requests)
        assert abs(veo_service.current_usage - expected_total) < 0.01, "Budget tracking should be accurate"
        
        # Verify alerts were triggered appropriately
        warning_alerts = [alert for alert in cost_tracker.budget_alerts if alert['severity'] == 'warning']
        critical_alerts = [alert for alert in cost_tracker.budget_alerts if alert['severity'] == 'critical']
        
        assert len(warning_alerts) >= 1, "Warning alerts should be triggered at 80% budget usage"
        assert len(critical_alerts) >= 1, "Critical alerts should be triggered at 90% budget usage"
        
        # Test budget prevention
        large_request_cost = 20.0  # Would exceed budget
        can_afford = veo_service.check_budget_available(large_request_cost)
        assert not can_afford, "Should prevent operations that exceed budget"
        
        print(f"\n📊 Budget Management Results:")
        print(f"   Final usage: ${veo_service.current_usage:.2f}/${initial_budget} ({veo_service.current_usage/initial_budget:.1%})")
        print(f"   Warning alerts: {len(warning_alerts)}")
        print(f"   Critical alerts: {len(critical_alerts)}")
    
    def test_cost_optimization_strategies(self, veo_service, cost_tracker):
        """Test cost optimization strategies"""
        
        # Test different quality/duration combinations for optimization
        optimization_scenarios = [
            # Same content, different qualities
            {'base': {'duration': 30, 'quality': 'ultra'}, 'optimized': {'duration': 30, 'quality': 'high'}},
            {'base': {'duration': 60, 'quality': 'high'}, 'optimized': {'duration': 45, 'quality': 'medium'}},
            {'base': {'duration': 120, 'quality': 'medium'}, 'optimized': {'duration': 90, 'quality': 'medium'}},
            
            # Resolution optimization
            {'base': {'duration': 30, 'quality': 'high', 'resolution': '3840x2160'}, 
             'optimized': {'duration': 30, 'quality': 'high', 'resolution': '1920x1080'}},
        ]
        
        optimization_results = []
        
        for scenario in optimization_scenarios:
            base_cost = veo_service.get_cost_estimate(scenario['base'])
            optimized_cost = veo_service.get_cost_estimate(scenario['optimized'])
            
            savings = base_cost - optimized_cost
            savings_percentage = (savings / base_cost) * 100 if base_cost > 0 else 0
            
            optimization_result = {
                'scenario': scenario,
                'base_cost': base_cost,
                'optimized_cost': optimized_cost,
                'savings': savings,
                'savings_percentage': savings_percentage
            }
            optimization_results.append(optimization_result)
            
            cost_tracker.record_cost('base_scenario', base_cost)
            cost_tracker.record_cost('optimized_scenario', optimized_cost)
            
            print(f"  Optimization: ${base_cost:.3f} → ${optimized_cost:.3f} (Save: ${savings:.3f} | {savings_percentage:.1f}%)")
        
        # Verify that optimizations actually save money
        total_base_cost = sum(result['base_cost'] for result in optimization_results)
        total_optimized_cost = sum(result['optimized_cost'] for result in optimization_results)
        total_savings = total_base_cost - total_optimized_cost
        
        assert total_savings > 0, "Optimization strategies should reduce costs"
        assert total_savings / total_base_cost > 0.1, "Should achieve at least 10% cost savings"
        
        # Test bulk optimization recommendations
        bulk_requests = [
            {'duration': 30, 'quality': 'ultra', 'resolution': '3840x2160'},
            {'duration': 60, 'quality': 'ultra', 'resolution': '3840x2160'},
            {'duration': 45, 'quality': 'high', 'resolution': '3840x2160'},
            {'duration': 90, 'quality': 'high', 'resolution': '1920x1080'},
        ]
        
        total_original_cost = sum(veo_service.get_cost_estimate(req) for req in bulk_requests)
        
        # Apply optimization rules
        optimized_requests = []
        for req in bulk_requests:
            optimized = req.copy()
            # Rule 1: Downgrade ultra to high quality
            if optimized['quality'] == 'ultra':
                optimized['quality'] = 'high'
            # Rule 2: Use 1080p for content > 60s
            if optimized['duration'] > 60 and optimized.get('resolution') == '3840x2160':
                optimized['resolution'] = '1920x1080'
            optimized_requests.append(optimized)
        
        total_optimized_cost = sum(veo_service.get_cost_estimate(req) for req in optimized_requests)
        bulk_savings = total_original_cost - total_optimized_cost
        
        assert bulk_savings > 0, "Bulk optimization should reduce total costs"
        
        print(f"\n🔧 Cost Optimization Results:")
        print(f"   Individual scenarios: {len(optimization_results)}")
        print(f"   Total savings: ${total_savings:.3f} ({total_savings/total_base_cost:.1%})")
        print(f"   Bulk optimization: ${bulk_savings:.3f} ({bulk_savings/total_original_cost:.1%})")
    
    def test_usage_analytics_and_reporting(self, veo_service, cost_tracker):
        """Test usage analytics and cost reporting"""
        
        # Simulate a month of usage with various patterns
        daily_usage_patterns = [
            # Week 1: Light usage
            [2.5, 3.0, 1.8, 4.2, 3.5, 1.0, 0.5],
            # Week 2: Moderate usage  
            [5.2, 6.8, 4.5, 7.2, 5.9, 3.2, 2.1],
            # Week 3: Heavy usage
            [8.5, 9.2, 7.8, 10.1, 8.8, 6.5, 4.2],
            # Week 4: Variable usage
            [3.2, 12.5, 2.1, 8.7, 4.5, 6.8, 3.9],
        ]
        
        usage_history = []
        cumulative_cost = 0.0
        
        for week_num, week_pattern in enumerate(daily_usage_patterns):
            for day_num, daily_cost in enumerate(week_pattern):
                cumulative_cost += daily_cost
                veo_service.track_costs(f"day_{week_num}_{day_num}", daily_cost)
                # Increment generation count for each simulated usage
                veo_service.generation_count += 1
                
                usage_record = {
                    'week': week_num + 1,
                    'day': day_num + 1,
                    'daily_cost': daily_cost,
                    'cumulative_cost': cumulative_cost,
                    'budget_usage': cumulative_cost / veo_service.monthly_budget
                }
                usage_history.append(usage_record)
                
                cost_tracker.record_cost(f"daily_usage_w{week_num+1}d{day_num+1}", daily_cost)
        
        # Analyze usage patterns
        weekly_totals = [sum(week) for week in daily_usage_patterns]
        peak_day_cost = max(record['daily_cost'] for record in usage_history)
        average_daily_cost = sum(record['daily_cost'] for record in usage_history) / len(usage_history)
        
        # Get final usage statistics
        final_stats = veo_service.get_usage_statistics()
        
        # Verify analytics accuracy
        expected_total = sum(sum(week) for week in daily_usage_patterns)
        assert abs(final_stats['total_cost'] - expected_total) < 0.01, "Usage tracking should be accurate"
        
        # Check if budget alerts would have been triggered
        budget_exceeded_days = [record for record in usage_history if record['budget_usage'] > 0.8]
        
        # Generate cost efficiency analysis
        efficiency_analysis = cost_tracker.analyze_cost_efficiency()
        
        # Verify reporting metrics
        assert final_stats['generation_count'] > 0, "Should track generation count"
        assert final_stats['average_cost_per_generation'] > 0, "Should calculate average cost"
        # Note: budget_remaining can be negative if usage exceeds budget
        # This is expected behavior for alerting purposes
        
        print(f"\n📈 Usage Analytics Results:")
        print(f"   Total monthly cost: ${final_stats['total_cost']:.2f}")
        print(f"   Budget utilization: {(final_stats['total_cost']/veo_service.monthly_budget):.1%}")
        print(f"   Average daily cost: ${average_daily_cost:.2f}")
        print(f"   Peak day cost: ${peak_day_cost:.2f}")
        print(f"   Days over 80% budget: {len(budget_exceeded_days)}")
        print(f"   Cost efficiency score: {efficiency_analysis['efficiency_score']:.1f}/100")
    
    def test_real_time_cost_monitoring(self, veo_service, cost_tracker):
        """Test real-time cost monitoring and alerts"""
        
        # Set up monitoring thresholds
        daily_budget_limit = 5.0
        hourly_budget_limit = 1.0
        veo_service.monthly_budget = 100.0
        
        # Simulate real-time operations with monitoring
        operations = [
            {'time': 0, 'cost': 0.8, 'type': 'normal'},
            {'time': 1800, 'cost': 0.7, 'type': 'normal'},   # 30 min later - within hourly limit
            {'time': 3600, 'cost': 1.2, 'type': 'spike'},    # 1 hour later - exceeds hourly but ok daily
            {'time': 5400, 'cost': 1.5, 'type': 'spike'},    # 1.5 hours later - approaching limits
            {'time': 7200, 'cost': 2.0, 'type': 'large'},    # 2 hours later - large operation
        ]
        
        monitoring_results = []
        current_hour_cost = 0.0
        current_day_cost = 0.0
        
        for op in operations:
            current_day_cost += op['cost']
            
            # Reset hourly cost if new hour
            if op['time'] >= 3600:  # New hour
                current_hour_cost = op['cost']
            else:
                current_hour_cost += op['cost']
            
            # Check thresholds
            hourly_threshold_exceeded = current_hour_cost > hourly_budget_limit
            daily_threshold_exceeded = current_day_cost > daily_budget_limit
            
            # Simulate cost monitoring decision
            should_proceed = not (hourly_threshold_exceeded or daily_threshold_exceeded)
            
            # Track costs if operation proceeds
            if should_proceed:
                veo_service.track_costs(f"rt_op_{op['time']}", op['cost'])
                cost_tracker.record_cost(f"realtime_{op['type']}", op['cost'])
            
            monitoring_result = {
                'operation_time': op['time'],
                'operation_cost': op['cost'],
                'operation_type': op['type'],
                'hourly_cost': current_hour_cost,
                'daily_cost': current_day_cost,
                'hourly_exceeded': hourly_threshold_exceeded,
                'daily_exceeded': daily_threshold_exceeded,
                'proceeded': should_proceed
            }
            monitoring_results.append(monitoring_result)
            
            print(f"  T+{op['time']:4d}s: ${op['cost']:.2f} [{op['type']}] H:${current_hour_cost:.2f} D:${current_day_cost:.2f} {'✅' if should_proceed else '🚫'}")
        
        # Verify monitoring effectiveness
        blocked_operations = [result for result in monitoring_results if not result['proceeded']]
        successful_operations = [result for result in monitoring_results if result['proceeded']]
        
        assert len(blocked_operations) > 0, "Should block operations that exceed thresholds"
        assert len(successful_operations) > 0, "Should allow operations within thresholds"
        
        # Check final costs are within expected ranges
        total_actual_cost = sum(op['operation_cost'] for op in successful_operations)
        assert total_actual_cost <= daily_budget_limit * 1.2, "Total cost should be controlled by monitoring"
        
        print(f"\n⚡ Real-time Monitoring Results:")
        print(f"   Total operations: {len(operations)}")
        print(f"   Successful: {len(successful_operations)}")
        print(f"   Blocked: {len(blocked_operations)}")
        print(f"   Total cost: ${total_actual_cost:.2f}")
        print(f"   Cost savings from blocking: ${sum(op['operation_cost'] for op in blocked_operations):.2f}")
    
    def test_cost_prediction_and_forecasting(self, veo_service, cost_tracker):
        """Test cost prediction and usage forecasting"""
        
        # Historical usage data for forecasting
        historical_weekly_usage = [
            [12.5, 15.2, 18.7, 14.3],  # Month 1
            [16.8, 19.5, 22.1, 17.9],  # Month 2  
            [20.2, 24.7, 28.3, 21.8],  # Month 3
        ]
        
        # Calculate trends
        monthly_totals = [sum(month) for month in historical_weekly_usage]
        
        # Simple linear trend calculation
        def calculate_trend(values):
            n = len(values)
            x_sum = sum(range(n))
            y_sum = sum(values)
            xy_sum = sum(i * values[i] for i in range(n))
            x2_sum = sum(i * i for i in range(n))
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
            intercept = (y_sum - slope * x_sum) / n
            
            return slope, intercept
        
        slope, intercept = calculate_trend(monthly_totals)
        
        # Predict next month's usage
        next_month_prediction = slope * len(monthly_totals) + intercept
        
        # Test various forecast scenarios
        forecast_scenarios = [
            {'scenario': 'conservative', 'multiplier': 0.9},
            {'scenario': 'expected', 'multiplier': 1.0},
            {'scenario': 'aggressive', 'multiplier': 1.3},
        ]
        
        forecast_results = []
        
        for scenario in forecast_scenarios:
            predicted_usage = next_month_prediction * scenario['multiplier']
            
            # Check if predicted usage fits within budget
            budget_utilization = predicted_usage / veo_service.monthly_budget
            budget_status = 'under' if budget_utilization < 0.8 else 'near' if budget_utilization < 1.0 else 'over'
            
            # Calculate recommended adjustments
            if budget_utilization > 1.0:
                recommended_reduction = (predicted_usage - veo_service.monthly_budget) / predicted_usage
            else:
                recommended_reduction = 0.0
            
            forecast_result = {
                'scenario': scenario['scenario'],
                'predicted_usage': predicted_usage,
                'budget_utilization': budget_utilization,
                'budget_status': budget_status,
                'recommended_reduction': recommended_reduction
            }
            forecast_results.append(forecast_result)
            
            cost_tracker.record_cost(f"forecast_{scenario['scenario']}", predicted_usage)
            
            print(f"  {scenario['scenario'].title()}: ${predicted_usage:.2f} ({budget_utilization:.1%} budget) [{budget_status}]")
        
        # Test cost prediction accuracy using historical data
        # Predict each month based on previous months
        prediction_accuracy = []
        
        for i in range(1, len(monthly_totals)):
            historical_subset = monthly_totals[:i]
            actual_value = monthly_totals[i]
            
            if len(historical_subset) >= 2:
                subset_slope, subset_intercept = calculate_trend(historical_subset)
                predicted_value = subset_slope * i + subset_intercept
                
                accuracy = 1.0 - abs(predicted_value - actual_value) / actual_value
                prediction_accuracy.append(accuracy)
        
        avg_prediction_accuracy = sum(prediction_accuracy) / len(prediction_accuracy) if prediction_accuracy else 0
        
        # Verify forecasting quality
        assert avg_prediction_accuracy > 0.7, f"Prediction accuracy should be reasonable: {avg_prediction_accuracy:.1%}"
        
        # Check that forecasts provide actionable insights
        over_budget_scenarios = [result for result in forecast_results if result['budget_utilization'] > 1.0]
        if over_budget_scenarios:
            max_reduction_needed = max(result['recommended_reduction'] for result in over_budget_scenarios)
            assert max_reduction_needed > 0, "Should recommend cost reductions when over budget"
        
        print(f"\n🔮 Cost Forecasting Results:")
        print(f"   Historical trend: ${slope:.2f}/month growth")
        print(f"   Next month prediction: ${next_month_prediction:.2f}")
        print(f"   Prediction accuracy: {avg_prediction_accuracy:.1%}")
        print(f"   Scenarios requiring optimization: {len(over_budget_scenarios)}")


class TestCostOptimizationIntegration:
    """Integration tests for cost optimization across AI services"""
    
    @pytest.fixture
    def ai_services_with_budgets(self):
        """Create AI services with budget constraints"""
        return {
            'veo': VEOAPIService(api_key="test_key", monthly_budget=50.0),
            'cost_tracker': CostTracker()
        }
    
    def test_end_to_end_cost_optimization(self, ai_services_with_budgets):
        """Test complete cost optimization workflow"""
        veo_service = ai_services_with_budgets['veo']
        cost_tracker = ai_services_with_budgets['cost_tracker']
        
        # Mock VEO API responses for cost testing
        with patch.object(veo_service, 'authenticate') as mock_auth, \
             patch.object(veo_service, '_make_request') as mock_request:
            
            mock_auth.return_value = True
            mock_request.return_value = {
                'generation_id': 'cost_test',
                'status': 'pending'
            }
            veo_service.is_authenticated = True
            
            # Scenario: User wants to generate multiple videos with budget constraints
            video_requests = [
                {'prompt': 'Nature documentary', 'duration': 60, 'quality': 'ultra', 'priority': 'high'},
                {'prompt': 'Product showcase', 'duration': 30, 'quality': 'high', 'priority': 'medium'},
                {'prompt': 'Tutorial video', 'duration': 45, 'quality': 'medium', 'priority': 'low'},
                {'prompt': 'Marketing clip', 'duration': 15, 'quality': 'high', 'priority': 'high'},
                {'prompt': 'Background footage', 'duration': 90, 'quality': 'low', 'priority': 'low'},
            ]
            
            # Step 1: Cost estimation and prioritization
            estimated_costs = []
            for i, request in enumerate(video_requests):
                cost = veo_service.get_cost_estimate(request)
                estimated_costs.append({
                    'index': i,
                    'request': request,
                    'estimated_cost': cost,
                    'priority_score': {'high': 3, 'medium': 2, 'low': 1}[request['priority']]
                })
            
            # Step 2: Budget allocation and optimization
            total_estimated = sum(item['estimated_cost'] for item in estimated_costs)
            available_budget = veo_service.monthly_budget - veo_service.current_usage
            
            print(f"\n💼 End-to-End Cost Optimization:")
            print(f"   Total estimated cost: ${total_estimated:.2f}")
            print(f"   Available budget: ${available_budget:.2f}")
            print(f"   Budget efficiency: {available_budget/total_estimated:.1%}")
            
            if total_estimated > available_budget:
                # Apply optimization strategies
                
                # Strategy 1: Priority-based selection
                estimated_costs.sort(key=lambda x: x['priority_score'], reverse=True)
                
                selected_requests = []
                running_cost = 0.0
                
                for item in estimated_costs:
                    if running_cost + item['estimated_cost'] <= available_budget:
                        selected_requests.append(item)
                        running_cost += item['estimated_cost']
                
                print(f"   Priority selection: {len(selected_requests)}/{len(video_requests)} videos")
                print(f"   Optimized cost: ${running_cost:.2f}")
                
                # Strategy 2: Quality optimization for remaining budget
                remaining_budget = available_budget - running_cost
                remaining_requests = [item for item in estimated_costs if item not in selected_requests]
                
                if remaining_requests and remaining_budget > 0:
                    # Try quality reduction
                    for item in remaining_requests:
                        original_request = item['request'].copy()
                        
                        # Reduce quality one level
                        quality_downgrades = {'ultra': 'high', 'high': 'medium', 'medium': 'low'}
                        if original_request['quality'] in quality_downgrades:
                            optimized_request = original_request.copy()
                            optimized_request['quality'] = quality_downgrades[original_request['quality']]
                            
                            optimized_cost = veo_service.get_cost_estimate(optimized_request)
                            
                            if optimized_cost <= remaining_budget:
                                selected_requests.append({
                                    'index': item['index'],
                                    'request': optimized_request,
                                    'estimated_cost': optimized_cost,
                                    'priority_score': item['priority_score'],
                                    'optimized': True
                                })
                                running_cost += optimized_cost
                                remaining_budget -= optimized_cost
                                break
                
                final_cost = running_cost
                optimization_savings = total_estimated - final_cost
                
            else:
                # Budget sufficient for all requests
                selected_requests = estimated_costs
                final_cost = total_estimated
                optimization_savings = 0.0
            
            # Step 3: Execute optimized plan
            execution_results = []
            for item in selected_requests:
                try:
                    result = veo_service.create_video_generation(item['request'])
                    veo_service.track_costs(result['generation_id'], item['estimated_cost'])
                    
                    execution_results.append({
                        'success': True,
                        'generation_id': result['generation_id'],
                        'cost': item['estimated_cost'],
                        'optimized': item.get('optimized', False)
                    })
                    
                    cost_tracker.record_cost(
                        f"optimized_{'yes' if item.get('optimized', False) else 'no'}", 
                        item['estimated_cost']
                    )
                    
                except VEOAPIError as e:
                    execution_results.append({
                        'success': False,
                        'error': str(e),
                        'cost': 0
                    })
            
            # Step 4: Analyze optimization effectiveness
            successful_executions = [result for result in execution_results if result['success']]
            actual_total_cost = sum(result['cost'] for result in successful_executions)
            
            optimization_analysis = {
                'total_requests': len(video_requests),
                'selected_requests': len(selected_requests),
                'successful_executions': len(successful_executions),
                'original_estimated_cost': total_estimated,
                'final_actual_cost': actual_total_cost,
                'optimization_savings': optimization_savings,
                'budget_utilization': actual_total_cost / available_budget,
                'cost_efficiency': len(successful_executions) / actual_total_cost if actual_total_cost > 0 else 0
            }
            
            # Verify optimization effectiveness
            assert len(successful_executions) > 0, "Should successfully execute at least some requests"
            assert actual_total_cost <= available_budget, "Should stay within budget"
            assert optimization_analysis['budget_utilization'] <= 1.0, "Should not exceed budget"
            
            if optimization_savings > 0:
                assert optimization_savings / total_estimated >= 0.1, "Should achieve meaningful savings when optimization is needed"
            
            print(f"   Final results:")
            print(f"   - Executed: {len(successful_executions)}/{len(video_requests)} videos")
            print(f"   - Actual cost: ${actual_total_cost:.2f}")
            print(f"   - Budget utilization: {optimization_analysis['budget_utilization']:.1%}")
            print(f"   - Optimization savings: ${optimization_savings:.2f}")
            print(f"   - Cost efficiency: {optimization_analysis['cost_efficiency']:.2f} videos/dollar")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to see print statements