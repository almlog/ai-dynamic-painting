"""
🔧 T6-013 REFACTOR Phase: CostTracker Implementation
VEO APIコスト追跡・予算管理サービスの実装

高品質なVEO API使用量追跡システムによる予算管理・コスト分析機能を提供
"""
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("ai_system.cost_tracker")

# Constants
DEFAULT_LOGGER_NAME = "ai_system.cost_tracker"
MIN_COST_AMOUNT = Decimal('0.01')  # 最小記録可能コスト金額


# Database integration placeholder for testing
class database:
    """Database integration module for cost tracking"""
    
    @staticmethod
    def get_session():
        """Get database session - placeholder for testing"""
        pass


# Exception Classes
class CostExceededError(Exception):
    """
    日次予算制限超過エラー
    
    厳格予算執行モード使用時に、コスト記録が日次予算を超過する場合に発生
    """
    pass


class InvalidCostDataError(Exception):
    """
    不正コストデータエラー
    
    コスト記録に無効なデータ（負の値、空文字列など）が含まれる場合に発生
    """
    pass


# Data Models
@dataclass
class CostRecord:
    """
    VEO APIコスト記録データモデル
    
    各API呼び出しのコスト情報とメタデータを格納するデータクラス
    
    Args:
        service_name: VEOサービス名 (例: 'veo_video_generation')
        cost_amount: API呼び出しコスト (Decimal精度)
        timestamp: 記録作成時刻
        request_details: リクエスト詳細情報 (プロンプト、パラメータ等)
        id: データベース識別子 (Optional)
    
    Raises:
        InvalidCostDataError: 不正なデータが設定された場合
    """
    
    service_name: str
    cost_amount: Decimal
    timestamp: datetime
    request_details: Dict[str, Any]
    id: Optional[int] = None
    
    def __post_init__(self) -> None:
        """
        初期化後のデータバリデーション
        
        Raises:
            InvalidCostDataError: バリデーション失敗時
        """
        if not self.service_name or not self.service_name.strip():
            raise InvalidCostDataError("Service name cannot be empty")
        
        if self.cost_amount <= 0:
            raise InvalidCostDataError("Cost amount must be positive")
        
        if not isinstance(self.timestamp, datetime):
            raise InvalidCostDataError("Timestamp must be datetime object")


class CostTracker:
    """
    VEO API Cost Tracking and Budget Management Service
    
    Features:
    - Record API usage costs with detailed metadata
    - Track daily/monthly spending against budgets
    - Generate cost reports and analytics
    - Database persistence for cost records
    """
    
    def __init__(self, daily_budget: Decimal, strict_budget_enforcement: bool = False, 
                 db_session: Optional[Any] = None) -> None:
        """
        CostTracker初期化
        
        VEO APIコスト追跡システムを予算制限とデータベース設定で初期化
        
        Args:
            daily_budget: 日次予算上限 (Decimal精度)
            strict_budget_enforcement: 厳格予算執行モード。Trueの場合、
                                     予算超過時にCostExceededErrorを発生
            db_session: データベースセッション (Optional)
                       Noneの場合はin-memoryフォールバックを使用
        
        Raises:
            InvalidCostDataError: daily_budgetが0以下の場合
        """
        # Input validation
        if daily_budget <= 0:
            raise InvalidCostDataError("Daily budget must be positive")
        
        # Budget configuration
        self.daily_budget = daily_budget
        self.strict_budget_enforcement = strict_budget_enforcement
        
        # In-memory storage (fallback when no database)
        self.cost_records: List[CostRecord] = []
        
        # Database connection
        self.db_connection = db_session or database.get_session()
        
        logger.info(f"CostTracker initialized with daily budget: ${daily_budget}")
    
    async def record_api_cost(self, service_name: str, cost_amount: Decimal, 
                             request_details: Dict[str, Any]) -> None:
        """
        Record VEO API usage cost with metadata
        
        Args:
            service_name: Name of the VEO service (e.g., 'veo_video_generation')
            cost_amount: Cost of the API call
            request_details: Dictionary with call details (prompt, duration, etc.)
            
        Raises:
            InvalidCostDataError: If input data is invalid
            CostExceededError: If strict budget enforcement is enabled and exceeded
        """
        # Input validation
        if not service_name or not service_name.strip():
            raise InvalidCostDataError("Service name cannot be empty")
        
        if cost_amount <= 0:
            raise InvalidCostDataError("Cost amount must be positive")
        
        # Budget check for strict enforcement
        if self.strict_budget_enforcement:
            current_daily_cost = await self.get_daily_cost(date.today())
            if current_daily_cost + cost_amount > self.daily_budget:
                raise CostExceededError(
                    f"Daily budget exceeded. Current: ${current_daily_cost}, "
                    f"Budget: ${self.daily_budget}, Attempted: ${cost_amount}"
                )
        
        # Create cost record
        cost_record = CostRecord(
            service_name=service_name.strip(),
            cost_amount=cost_amount,
            timestamp=datetime.now(),
            request_details=request_details or {}
        )
        
        # Store in memory (fallback)
        self.cost_records.append(cost_record)
        
        # Database persistence
        if self.db_connection:
            try:
                self.db_connection.add(cost_record)
                self.db_connection.commit()
                logger.debug("Cost record saved to database")
            except Exception as e:
                logger.warning(f"Failed to save to database: {e}")
        
        logger.info(f"Recorded API cost: ${cost_amount} for {service_name}")
    
    async def get_cost_records(self, start_date: Optional[date] = None, 
                              end_date: Optional[date] = None) -> List[CostRecord]:
        """
        Get cost records within date range
        
        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            
        Returns:
            List of CostRecord objects
        """
        # Database query when available
        if self.db_connection:
            try:
                query_obj = self.db_connection.query(CostRecord)
                
                # Apply date filters if provided
                if start_date:
                    query_obj = query_obj.filter(CostRecord.timestamp >= start_date)
                if end_date:
                    query_obj = query_obj.filter(CostRecord.timestamp <= end_date)
                
                records = query_obj.all()
                return records
                    
            except Exception as e:
                logger.warning(f"Database query failed, using in-memory fallback: {e}")
        
        # Fallback to in-memory storage
        records = self.cost_records.copy()
        
        if start_date or end_date:
            filtered_records = []
            for record in records:
                record_date = record.timestamp.date()
                
                # Check start date
                if start_date and record_date < start_date:
                    continue
                    
                # Check end date
                if end_date and record_date > end_date:
                    continue
                
                filtered_records.append(record)
            
            records = filtered_records
        
        return records
    
    async def get_total_cost(self) -> Decimal:
        """Get total cost across all records"""
        return sum(record.cost_amount for record in self.cost_records)
    
    async def get_daily_cost(self, target_date: date) -> Decimal:
        """
        Get total cost for a specific day
        
        Args:
            target_date: Date to calculate costs for
            
        Returns:
            Total cost for the specified date
        """
        daily_records = await self.get_cost_records(
            start_date=target_date,
            end_date=target_date
        )
        
        return sum(record.cost_amount for record in daily_records)
    
    async def get_monthly_cost(self, year: int, month: int) -> Decimal:
        """
        Get total cost for a specific month
        
        Args:
            year: Target year
            month: Target month (1-12)
            
        Returns:
            Total cost for the specified month
        """
        # Calculate month boundaries
        start_date = date(year, month, 1)
        
        # Handle month-end calculation
        if month == 12:
            end_date = date(year + 1, 1, 1) - date.resolution
        else:
            end_date = date(year, month + 1, 1) - date.resolution
        
        monthly_records = await self.get_cost_records(
            start_date=start_date,
            end_date=end_date
        )
        
        return sum(record.cost_amount for record in monthly_records)
    
    async def is_budget_exceeded(self) -> bool:
        """
        Check if today's spending has exceeded the daily budget
        
        Returns:
            True if budget exceeded, False otherwise
        """
        today_cost = await self.get_daily_cost(date.today())
        return today_cost > self.daily_budget
    
    async def get_budget_usage_rate(self) -> Decimal:
        """
        Get current budget usage rate as a decimal (1.0 = 100%)
        
        Returns:
            Usage rate (e.g., 1.30 for 130% usage)
        """
        today_cost = await self.get_daily_cost(date.today())
        if self.daily_budget == 0:
            return Decimal('0')
        
        return today_cost / self.daily_budget
    
    async def generate_cost_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Generate comprehensive cost analysis report
        
        Args:
            start_date: Report period start date
            end_date: Report period end date
            
        Returns:
            Dictionary with detailed cost analysis
        """
        records = await self.get_cost_records(start_date, end_date)
        
        # Calculate total cost
        total_cost = sum(record.cost_amount for record in records)
        
        # Service breakdown
        service_breakdown = {}
        for record in records:
            service = record.service_name
            if service not in service_breakdown:
                service_breakdown[service] = Decimal('0')
            service_breakdown[service] += record.cost_amount
        
        # Budget analysis (for today if single day report)
        if start_date == end_date == date.today():
            budget_usage_percentage = float((total_cost / self.daily_budget) * 100)
            remaining_budget = self.daily_budget - total_cost
        else:
            # Multi-day report - no budget analysis
            budget_usage_percentage = None
            remaining_budget = None
        
        return {
            'total_cost': total_cost,
            'service_breakdown': service_breakdown,
            'budget_usage_percentage': budget_usage_percentage,
            'remaining_budget': remaining_budget,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'record_count': len(records)
        }