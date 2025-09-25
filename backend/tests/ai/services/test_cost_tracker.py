"""
🔴 T6-013 RED Phase: CostTracker Testing Suite
VEO APIコスト追跡・予算管理サービスのテスト実装
"""
import pytest
import asyncio
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, List, Optional

# TDD RED Phase: Import will fail until implementation exists
try:
    from src.ai.services.cost_tracker import (
        CostTracker,
        CostRecord,
        CostExceededError,
        InvalidCostDataError
    )
except ImportError:
    # Expected to fail in RED phase
    pass


class TestCostTracker:
    """CostTracker Testing Suite with VEO API Cost Management"""

    def test_cost_tracker_initialization(self):
        """
        🔴 RED: CostTracker初期化テスト
        - 日次予算設定の確認
        - データベースコネクション設定の確認
        """
        daily_budget = Decimal('50.00')
        tracker = CostTracker(daily_budget=daily_budget)
        
        assert tracker.daily_budget == daily_budget
        assert hasattr(tracker, 'db_connection')
        assert hasattr(tracker, 'cost_records')

    @pytest.mark.asyncio
    async def test_record_api_cost_basic(self):
        """
        🔴 RED: API呼び出しコスト記録の基本テスト
        VEO APIコールのコストを正しく記録・加算できることを検証
        """
        tracker = CostTracker(daily_budget=Decimal('100.00'))
        
        # VEO API呼び出しコストの記録
        await tracker.record_api_cost(
            service_name='veo_video_generation',
            cost_amount=Decimal('2.50'),
            request_details={
                'prompt': 'Beautiful sunset video',
                'duration': 8,
                'resolution': '1920x1080'
            }
        )
        
        # コスト記録の確認
        cost_records = await tracker.get_cost_records()
        assert len(cost_records) == 1
        assert cost_records[0].service_name == 'veo_video_generation'
        assert cost_records[0].cost_amount == Decimal('2.50')
        assert cost_records[0].request_details['prompt'] == 'Beautiful sunset video'

    @pytest.mark.asyncio
    async def test_record_multiple_api_costs_accumulation(self):
        """
        🔴 RED: 複数API呼び出しコスト累積テスト
        複数のVEO API呼び出しコストが正しく累積されることを検証
        """
        tracker = CostTracker(daily_budget=Decimal('100.00'))
        
        # 複数回のAPI呼び出しコスト記録
        await tracker.record_api_cost('veo_video_generation', Decimal('2.50'), {})
        await tracker.record_api_cost('veo_video_generation', Decimal('3.75'), {})
        await tracker.record_api_cost('veo_image_to_video', Decimal('1.25'), {})
        
        # 累積コストの確認
        total_cost = await tracker.get_total_cost()
        assert total_cost == Decimal('7.50')  # 2.50 + 3.75 + 1.25

    @pytest.mark.asyncio
    async def test_get_daily_cost_calculation(self):
        """
        🔴 RED: 日別コスト計算テスト
        指定した期間（今日一日）の合計コストを正しく取得できることを検証
        """
        tracker = CostTracker(daily_budget=Decimal('50.00'))
        target_date = date.today()
        
        # 今日の複数API呼び出しコスト記録
        await tracker.record_api_cost('veo_video_generation', Decimal('5.00'), {})
        await tracker.record_api_cost('veo_video_generation', Decimal('3.50'), {})
        
        # 日別コスト取得
        daily_cost = await tracker.get_daily_cost(target_date)
        assert daily_cost == Decimal('8.50')

    @pytest.mark.asyncio
    async def test_get_monthly_cost_aggregation(self):
        """
        🔴 RED: 月別コスト集計テスト
        月単位でのコスト集計が正しく動作することを検証
        """
        tracker = CostTracker(daily_budget=Decimal('50.00'))
        target_month = datetime.now().replace(day=1).date()
        
        # 月内の複数日にわたるAPI呼び出し記録
        await tracker.record_api_cost('veo_video_generation', Decimal('10.00'), {})
        await tracker.record_api_cost('veo_image_to_video', Decimal('5.00'), {})
        
        monthly_cost = await tracker.get_monthly_cost(target_month.year, target_month.month)
        assert monthly_cost == Decimal('15.00')

    @pytest.mark.asyncio
    async def test_is_budget_exceeded_detection(self):
        """
        🔴 RED: 予算超過判定テスト
        設定された日次予算を超えた場合にis_budget_exceededがTrueを返すことを検証
        """
        daily_budget = Decimal('10.00')
        tracker = CostTracker(daily_budget=daily_budget)
        
        # 予算内での使用
        await tracker.record_api_cost('veo_video_generation', Decimal('8.00'), {})
        assert await tracker.is_budget_exceeded() == False
        
        # 予算超過
        await tracker.record_api_cost('veo_video_generation', Decimal('5.00'), {})
        assert await tracker.is_budget_exceeded() == True
        
        # 予算使用率の確認
        usage_rate = await tracker.get_budget_usage_rate()
        assert usage_rate == Decimal('1.30')  # 130% (13.00 / 10.00)

    @pytest.mark.asyncio
    async def test_cost_exceeded_error_handling(self):
        """
        🔴 RED: コスト超過エラーハンドリングテスト
        予算超過時の適切なエラー発生確認
        """
        tracker = CostTracker(
            daily_budget=Decimal('20.00'),
            strict_budget_enforcement=True
        )
        
        # 予算ギリギリまで使用
        await tracker.record_api_cost('veo_video_generation', Decimal('18.00'), {})
        
        # 予算超過する追加コストでエラー発生を確認
        with pytest.raises(CostExceededError) as exc_info:
            await tracker.record_api_cost('veo_video_generation', Decimal('5.00'), {})
        
        assert "Daily budget exceeded" in str(exc_info.value)
        assert "Current: $18.00, Budget: $20.00, Attempted: $5.00" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_cost_data_validation(self):
        """
        🔴 RED: 不正コストデータバリデーションテスト
        負の値や不正な値での例外発生確認
        """
        tracker = CostTracker(daily_budget=Decimal('50.00'))
        
        # 負のコスト値でのエラー
        with pytest.raises(InvalidCostDataError):
            await tracker.record_api_cost('veo_video_generation', Decimal('-1.00'), {})
        
        # ゼロコストでのエラー
        with pytest.raises(InvalidCostDataError):
            await tracker.record_api_cost('veo_video_generation', Decimal('0.00'), {})
        
        # サービス名が空での エラー
        with pytest.raises(InvalidCostDataError):
            await tracker.record_api_cost('', Decimal('5.00'), {})

    @patch('src.ai.services.cost_tracker.database')
    @pytest.mark.asyncio
    async def test_cost_record_database_persistence(self, mock_database):
        """
        🔴 RED: コスト記録データベース永続化テスト
        コスト記録がデータベースに正しく保存されることを検証（DB層はモック）
        """
        # データベース操作のモック設定 (AsyncMock警告を避けるためMagicMockを使用)
        mock_db_session = MagicMock()
        mock_database.get_session.return_value = mock_db_session
        
        tracker = CostTracker(daily_budget=Decimal('100.00'))
        
        # API呼び出しコスト記録
        cost_details = {
            'prompt': 'Amazing landscape video',
            'duration': 8,
            'model_version': 'veo-001-preview'
        }
        
        await tracker.record_api_cost(
            'veo_video_generation',
            Decimal('4.50'),
            cost_details
        )
        
        # データベース保存の確認
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        
        # 保存されたデータの検証
        saved_record = mock_db_session.add.call_args[0][0]
        assert saved_record.service_name == 'veo_video_generation'
        assert saved_record.cost_amount == Decimal('4.50')
        assert saved_record.request_details == cost_details
        assert saved_record.timestamp is not None

    @patch('src.ai.services.cost_tracker.database')
    @pytest.mark.asyncio
    async def test_cost_records_database_retrieval(self, mock_database):
        """
        🔴 RED: コスト記録データベース取得テスト
        データベースからのコスト記録取得が正しく動作することを検証
        """
        # データベースクエリ結果のモック設定
        mock_cost_record_1 = MagicMock()
        mock_cost_record_1.service_name = 'veo_video_generation'
        mock_cost_record_1.cost_amount = Decimal('3.00')
        mock_cost_record_1.timestamp = datetime.now()
        
        mock_cost_record_2 = MagicMock()
        mock_cost_record_2.service_name = 'veo_image_to_video'
        mock_cost_record_2.cost_amount = Decimal('2.00')
        mock_cost_record_2.timestamp = datetime.now()
        
        expected_records = [mock_cost_record_1, mock_cost_record_2]
        
        # MagicMock チェーンを設定 (フィルタなしの場合: query().all() のみ)
        mock_db_session = MagicMock()
        
        # query().all() のシンプルなチェーン
        mock_query_chain = MagicMock()
        mock_query_chain.all.return_value = expected_records
        mock_db_session.query.return_value = mock_query_chain
        
        mock_database.get_session.return_value = mock_db_session
        
        # db_sessionを直接注入してCostTracker作成
        tracker = CostTracker(daily_budget=Decimal('50.00'), db_session=mock_db_session)
        
        # データベースからのコスト記録取得（フィルタリングなしでDBの基本動作をテスト）
        cost_records = await tracker.get_cost_records()
        
        # 取得結果の検証
        assert len(cost_records) == 2
        assert cost_records[0].service_name == 'veo_video_generation'
        assert cost_records[0].cost_amount == Decimal('3.00')
        assert cost_records[1].service_name == 'veo_image_to_video'
        assert cost_records[1].cost_amount == Decimal('2.00')
        
        # モックメソッドの呼び出し確認
        mock_db_session.query.assert_called_once_with(CostRecord)
        # query().all() が呼ばれることを確認
        mock_query_chain.all.assert_called_once()

    @pytest.mark.asyncio
    async def test_cost_analytics_and_reporting(self):
        """
        🔴 RED: コスト分析・レポート機能テスト
        詳細なコスト分析情報の取得テスト
        """
        tracker = CostTracker(daily_budget=Decimal('100.00'))
        
        # 複数サービスのコスト記録
        await tracker.record_api_cost('veo_video_generation', Decimal('25.00'), {})
        await tracker.record_api_cost('veo_image_to_video', Decimal('15.00'), {})
        await tracker.record_api_cost('veo_video_generation', Decimal('20.00'), {})
        
        # コスト分析レポートの取得
        cost_report = await tracker.generate_cost_report(
            start_date=date.today(),
            end_date=date.today()
        )
        
        # レポート内容の検証
        assert cost_report['total_cost'] == Decimal('60.00')
        assert cost_report['service_breakdown']['veo_video_generation'] == Decimal('45.00')
        assert cost_report['service_breakdown']['veo_image_to_video'] == Decimal('15.00')
        assert cost_report['budget_usage_percentage'] == 60.0  # 60% of $100
        assert cost_report['remaining_budget'] == Decimal('40.00')

    def test_cost_record_data_model(self):
        """
        🔴 RED: CostRecordデータモデルテスト
        コスト記録のデータ構造確認
        """
        cost_record = CostRecord(
            id=1,
            service_name='veo_video_generation',
            cost_amount=Decimal('5.75'),
            timestamp=datetime.now(),
            request_details={
                'prompt': 'Test video generation',
                'duration': 8,
                'resolution': '1920x1080',
                'style': 'cinematic'
            }
        )
        
        assert cost_record.service_name == 'veo_video_generation'
        assert cost_record.cost_amount == Decimal('5.75')
        assert isinstance(cost_record.timestamp, datetime)
        assert cost_record.request_details['prompt'] == 'Test video generation'
        assert cost_record.request_details['duration'] == 8