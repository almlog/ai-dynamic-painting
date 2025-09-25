"""
Admin Dashboard API テストスイート
TDD: Red Phase - 失敗するテストを先に書く
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app
from src.models.admin import PromptTemplate, GenerationRequest, GenerationResult, Evaluation

client = TestClient(app)

# --- Mocks ---
@pytest.fixture(autouse=True)
def mock_gemini_service(monkeypatch):
    """GeminiService.generate_imageをモックし、APIキーを不要にする"""
    def mock_generate_image(*args, **kwargs):
        # ダミーの画像バイト列を返す
        return b'dummy_image_bytes'
    
    monkeypatch.setattr(
        "src.services.gemini_service.GeminiService.generate_image",
        mock_generate_image
    )

# --- Test Classes ---



class TestPromptManagement:
    """プロンプト管理機能のテスト"""
    
    def test_create_prompt_template(self):
        """プロンプトテンプレート作成テスト"""
        # Arrange
        template_data = {
            "name": "船橋市夜景テンプレート",
            "template": """
千葉県船橋市の{time_of_day}の風景を油絵で描いてください。
天気: {weather}
気温: {temperature}°C

【スタイル】
- 印象派風油絵
- 暖かみのある色調
- 文字無し純粋絵画
            """.strip(),
            "variables": ["time_of_day", "weather", "temperature"],
            "parameters": {
                "model": "gemini-1.5-flash",
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.95
            }
        }
        
        # Act
        response = client.post("/api/admin/prompts", json=template_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == template_data["name"]
        assert data["id"] is not None
        assert "created_at" in data
    
    def test_list_prompt_templates(self):
        """プロンプトテンプレート一覧取得テスト"""
        # Act
        response = client.get("/api/admin/prompts")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_prompt_template(self):
        """プロンプトテンプレート更新テスト"""
        # Arrange - まず作成
        template_data = {
            "name": "更新テスト用テンプレート",
            "template": "初期テンプレート",
            "variables": [],
            "parameters": {}
        }
        create_response = client.post("/api/admin/prompts", json=template_data)
        template_id = create_response.json()["id"]
        
        # Act - 更新
        update_data = {
            "name": "更新後テンプレート",
            "template": "更新後の内容"
        }
        response = client.put(f"/api/admin/prompts/{template_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["template"] == update_data["template"]
    
    def test_delete_prompt_template(self):
        """プロンプトテンプレート削除テスト"""
        # Arrange - まず作成
        template_data = {
            "name": "削除テスト用",
            "template": "削除される",
            "variables": [],
            "parameters": {}
        }
        create_response = client.post("/api/admin/prompts", json=template_data)
        template_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"/api/admin/prompts/{template_id}")
        
        # Assert
        assert response.status_code == 204
        
        # 削除確認
        get_response = client.get(f"/api/admin/prompts/{template_id}")
        assert get_response.status_code == 404


class TestImageGeneration:
    """画像生成機能のテスト"""
    
    def test_generate_with_parameters(self):
        """パラメータ指定での画像生成テスト"""
        # Arrange
        generation_request = {
            "prompt_template_id": "test-template-001",
            "model": "gemini-1.5-flash",
            "temperature": 0.8,
            "top_k": 50,
            "top_p": 0.9,
            "max_tokens": 2048,
            "variables": {
                "time_of_day": "夜",
                "weather": "晴れ",
                "temperature": "22"
            }
        }
        
        # Act
        response = client.post("/api/admin/generate", json=generation_request)
        
        # Assert
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "generation_id" in data
        assert "status" in data
        assert data["status"] == "processing"
    
    def test_get_generation_status(self):
        """生成ステータス確認テスト"""
        # Arrange - まず生成開始
        generation_request = {
            "prompt_template_id": "test-template-001",
            "model": "gemini-1.5-flash"
        }
        generate_response = client.post("/api/admin/generate", json=generation_request)
        generation_id = generate_response.json()["generation_id"]
        
        # Act
        response = client.get(f"/api/admin/generate/status/{generation_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["generation_id"] == generation_id
        assert "status" in data
        assert data["status"] in ["processing", "completed", "failed"]

    def test_generate_with_quality_parameter(self):
        """品質パラメータ指定での画像生成テスト"""
        # Arrange
        generation_request = {
            "prompt_template_id": "test-template-001",
            "quality": "hd",
            "variables": {
                "time_of_day": "朝",
                "weather": "曇り",
                "temperature": "15"
            }
        }
        
        # Act
        response = client.post("/api/admin/generate", json=generation_request)
        
        # Assert
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "generation_id" in data
        assert data["status"] == "processing"

    def test_generate_with_aspect_ratio_parameter(self):
        """アスペクト比パラメータ指定での画像生成テスト"""
        # Arrange
        generation_request = {
            "prompt_template_id": "test-template-001",
            "aspect_ratio": "16:9",
            "variables": {
                "time_of_day": "昼",
                "weather": "雨",
                "temperature": "25"
            }
        }
        
        # Act
        response = client.post("/api/admin/generate", json=generation_request)
        
        # Assert
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "generation_id" in data
        assert data["status"] == "processing"

    def test_generate_with_negative_prompt_parameter(self):
        """ネガティブプロンプトパラメータ指定での画像生成テスト"""
        # Arrange
        generation_request = {
            "prompt_template_id": "test-template-001",
            "negative_prompt": "text, watermark, people",
            "variables": {
                "time_of_day": "深夜",
                "weather": "雪",
                "temperature": "-5"
            }
        }
        
        # Act
        response = client.post("/api/admin/generate", json=generation_request)
        
        # Assert
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "generation_id" in data
        assert data["status"] == "processing"

    def test_generate_with_style_preset_parameter(self):
        """スタイルプリセットパラメータ指定での画像生成テスト"""
        # Arrange
        generation_request = {
            "prompt_template_id": "test-template-001",
            "style_preset": "anime",
            "variables": {
                "time_of_day": "夕方",
                "weather": "快晴",
                "temperature": "20"
            }
        }
        
        # Act
        response = client.post("/api/admin/generate", json=generation_request)
        
        # Assert - まず生成が成功すること
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "generation_id" in data
        assert data["status"] == "processing"
        
        # Arrange - 生成結果を取得してstyle_presetが保存されていることを確認
        generation_id = data["generation_id"]
        
        # Act - ステータス確認でリクエスト詳細を取得
        status_response = client.get(f"/api/admin/generate/status/{generation_id}")
        
        # Assert - style_presetが含まれていることを確認
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "style_preset" in status_data["request"]
        assert status_data["request"]["style_preset"] == "anime"

    def test_generate_with_seed_parameter(self):
        """シードパラメータ指定での画像生成テスト"""
        # Arrange
        generation_request = {
            "prompt_template_id": "test-template-001",
            "seed": 12345,
            "variables": {
                "time_of_day": "早朝",
                "weather": "霧",
                "temperature": "10"
            }
        }
        
        # Act
        response = client.post("/api/admin/generate", json=generation_request)
        
        # Assert - まず生成が成功すること
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "generation_id" in data
        assert data["status"] == "processing"
        
        # Arrange - 生成結果を取得してseedが保存されていることを確認
        generation_id = data["generation_id"]
        
        # Act - ステータス確認でリクエスト詳細を取得
        status_response = client.get(f"/api/admin/generate/status/{generation_id}")
        
        # Assert - seedが含まれていることを確認
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "seed" in status_data["request"]
        assert status_data["request"]["seed"] == 12345

    
    def test_get_generation_history(self):
        """生成履歴取得テスト"""
        # Act
        response = client.get("/api/admin/generate/history")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            assert "id" in item
            assert "created_at" in item
            assert "request" in item
            assert "prompt_template_id" in item["request"]


class TestEvaluation:
    """品質評価機能のテスト"""
    
    def test_evaluate_generation(self):
        """生成結果評価テスト"""
        # Arrange
        evaluation_data = {
            "generation_id": "test-generation-001",
            "rating": 4,
            "tags": ["高品質", "船橋市らしい", "夜景"],
            "comment": "印象派風の表現が美しい"
        }
        
        # Act
        response = client.post("/api/admin/evaluations", json=evaluation_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["generation_id"] == evaluation_data["generation_id"]
        assert data["rating"] == evaluation_data["rating"]
        assert set(data["tags"]) == set(evaluation_data["tags"])
    
    def test_get_evaluation(self):
        """評価取得テスト"""
        # Arrange - まず評価作成
        evaluation_data = {
            "generation_id": "test-generation-002",
            "rating": 5,
            "tags": ["優秀"],
            "comment": "完璧"
        }
        create_response = client.post("/api/admin/evaluations", json=evaluation_data)
        evaluation_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/admin/evaluations/{evaluation_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == evaluation_id
        assert data["rating"] == 5


class TestAnalytics:
    """分析機能のテスト"""
    
    def test_get_analytics_data(self):
        """分析データ取得テスト"""
        # Act
        response = client.get("/api/admin/analytics")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_generations" in data
        assert "success_rate" in data
        assert "average_rating" in data
        assert "api_usage" in data


class TestSettings:
    """設定管理のテスト"""
    
    def test_get_settings(self):
        """設定取得テスト"""
        # Act
        response = client.get("/api/admin/settings")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "default_model" in data
        assert "rate_limit" in data
        assert "retention_days" in data
    
    def test_update_settings(self):
        """設定更新テスト"""
        # Arrange
        settings_data = {
            "default_model": "gemini-1.5-pro",
            "rate_limit": 10,
            "retention_days": 30
        }
        
        # Act
        response = client.put("/api/admin/settings", json=settings_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["default_model"] == settings_data["default_model"]


class TestIntegration:
    """統合テスト"""
    
    def test_complete_generation_flow(self):
        """プロンプト作成→生成→評価の完全フロー"""
        # Step 1: プロンプトテンプレート作成
        template_data = {
            "name": "統合テスト用テンプレート",
            "template": "船橋市の{time_of_day}の風景",
            "variables": ["time_of_day"],
            "parameters": {
                "model": "gemini-1.5-flash",
                "temperature": 0.7
            }
        }
        template_response = client.post("/api/admin/prompts", json=template_data)
        assert template_response.status_code == 201
        template_id = template_response.json()["id"]
        
        # Step 2: 画像生成実行
        generation_request = {
            "prompt_template_id": template_id,
            "variables": {
                "time_of_day": "夕暮れ"
            }
        }
        generate_response = client.post("/api/admin/generate", json=generation_request)
        assert generate_response.status_code == 202
        generation_id = generate_response.json()["generation_id"]
        
        # Step 3: ステータス確認
        status_response = client.get(f"/api/admin/generate/status/{generation_id}")
        assert status_response.status_code == 200
        
        # Step 4: 評価登録
        evaluation_data = {
            "generation_id": generation_id,
            "rating": 4,
            "tags": ["良好"],
            "comment": "統合テスト成功"
        }
        eval_response = client.post("/api/admin/evaluations", json=evaluation_data)
        assert eval_response.status_code == 201
        
        # Step 5: 分析データ確認
        analytics_response = client.get("/api/admin/analytics")
        assert analytics_response.status_code == 200
        analytics_data = analytics_response.json()
        assert analytics_data["total_generations"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])