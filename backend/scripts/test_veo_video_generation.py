#!/usr/bin/env python3
"""
VEO動画生成機能テストスクリプト
/api/ai/generateエンドポイントの実際動作確認とループ動画生成テスト
"""

import os
import sys
import json
import time
import asyncio
import requests
from datetime import datetime
from pathlib import Path

# Add backend src to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_OUTPUT_DIR = backend_dir / "generated_videos" / "test_output"
VEO_ENDPOINT = f"{API_BASE_URL}/api/ai/generate"

# Test prompts for video generation
TEST_PROMPTS = [
    {
        "name": "simple_landscape",
        "prompt": "A serene mountain landscape with flowing water, perfect for loop video",
        "description": "シンプルな山の風景 - ループ動画テスト用"
    },
    {
        "name": "ocean_waves", 
        "prompt": "Gentle ocean waves on a peaceful beach, seamless loop animation",
        "description": "穏やかな海の波 - シームレスループアニメーション"
    },
    {
        "name": "forest_scene",
        "prompt": "Mystical forest with soft wind through trees, continuous loop",
        "description": "神秘的な森 - 連続ループ動画"
    }
]

class VEOVideoGenerationTester:
    """VEO動画生成テスト管理クラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """テスト出力ディレクトリの作成"""
        TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📁 テスト出力ディレクトリ: {TEST_OUTPUT_DIR}")
    
    def check_api_health(self) -> bool:
        """API サーバーの稼働確認"""
        try:
            response = self.session.get(f"{API_BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API サーバー稼働確認: {health_data.get('status', 'unknown')}")
                print(f"   バージョン: {health_data.get('version', 'unknown')}")
                print(f"   フェーズ: {health_data.get('phase', 'unknown')}")
                return True
            else:
                print(f"❌ API ヘルスチェック失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API サーバー接続エラー: {e}")
            return False
    
    def test_video_generation_endpoint(self, prompt_data: dict) -> dict:
        """動画生成エンドポイントのテスト"""
        print(f"\n🎬 動画生成テスト開始: {prompt_data['name']}")
        print(f"   プロンプト: {prompt_data['prompt'][:60]}...")
        
        # Request payload for video generation
        payload = {
            "prompt": prompt_data['prompt'],
            "output_format": "video",
            "duration_seconds": 5,  # VEO API要件: 最低5秒
            "resolution": "720p",   # 高品質: 720p
            "fps": 24,             # 標準フレームレート
            "loop_mode": True,     # ループ動画生成
            "quality": "high",     # 高品質設定
            "priority": "normal"   # 通常優先度
        }
        
        test_result = {
            "test_name": prompt_data['name'],
            "prompt": prompt_data['prompt'],
            "description": prompt_data['description'],
            "start_time": datetime.now().isoformat(),
            "success": False,
            "response_data": None,
            "error": None,
            "duration": 0,
            "task_id": None,
            "estimated_cost": None
        }
        
        try:
            start_time = time.time()
            
            # POST request to video generation endpoint
            print(f"📤 API呼び出し: {VEO_ENDPOINT}")
            response = self.session.post(
                VEO_ENDPOINT,
                json=payload,
                timeout=30,  # 30秒タイムアウト
                headers={"Content-Type": "application/json"}
            )
            
            duration = time.time() - start_time
            test_result["duration"] = round(duration, 2)
            
            print(f"📬 応答受信: {response.status_code} ({duration:.2f}秒)")
            
            if response.status_code == 200:
                response_data = response.json()
                test_result["success"] = True
                test_result["response_data"] = response_data
                test_result["task_id"] = response_data.get("task_id")
                test_result["estimated_cost"] = response_data.get("estimated_cost")
                
                print(f"✅ 動画生成タスク作成成功!")
                print(f"   タスクID: {test_result['task_id']}")
                print(f"   推定コスト: {test_result['estimated_cost']}")
                print(f"   応答時間: {duration:.2f}秒")
                
                # Save task info for monitoring
                if test_result['task_id']:
                    self.save_task_info(test_result)
                
            elif response.status_code == 400:
                error_data = response.json()
                test_result["error"] = f"リクエストエラー: {error_data.get('detail', 'Unknown error')}"
                print(f"❌ リクエストエラー (400): {test_result['error']}")
                
            elif response.status_code == 429:
                print(f"⚠️  レート制限エラー (429): API使用量上限")
                test_result["error"] = "API使用量上限に達しました"
                
            elif response.status_code == 500:
                error_data = response.json() if response.content else {}
                test_result["error"] = f"サーバーエラー: {error_data.get('detail', 'Internal server error')}"
                print(f"❌ サーバーエラー (500): {test_result['error']}")
                
            else:
                test_result["error"] = f"Unexpected status code: {response.status_code}"
                print(f"❌ 予期しないステータスコード: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   エラー詳細: {error_detail}")
                except:
                    print(f"   レスポンス: {response.text[:200]}")
            
        except requests.exceptions.Timeout:
            test_result["error"] = "リクエストタイムアウト"
            print(f"❌ リクエストタイムアウト (30秒)")
            
        except requests.exceptions.ConnectionError:
            test_result["error"] = "接続エラー - サーバーが起動していない可能性"
            print(f"❌ 接続エラー: サーバーが起動していない可能性があります")
            
        except Exception as e:
            test_result["error"] = f"予期しないエラー: {str(e)}"
            print(f"❌ 予期しないエラー: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def save_task_info(self, test_result: dict):
        """タスク情報の保存（後の監視用）"""
        task_file = TEST_OUTPUT_DIR / f"task_{test_result['task_id']}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, indent=2, ensure_ascii=False)
        print(f"💾 タスク情報保存: {task_file}")
    
    def check_task_status(self, task_id: str) -> dict:
        """タスクステータスの確認"""
        try:
            status_url = f"{API_BASE_URL}/api/ai/tasks/{task_id}/status"
            response = self.session.get(status_url, timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"📊 タスクステータス [{task_id[:8]}]: {status_data.get('status', 'unknown')}")
                return status_data
            else:
                print(f"❌ ステータス確認失敗: {response.status_code}")
                return {"status": "unknown", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ ステータス確認エラー: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_test_report(self):
        """テストレポート生成"""
        report_file = TEST_OUTPUT_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Test summary
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": round(successful_tests / total_tests * 100, 1) if total_tests > 0 else 0,
                "test_timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 テストレポート生成完了: {report_file}")
        return report
    
    def generate_recommendations(self) -> list:
        """推奨事項の生成"""
        recommendations = []
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        if len(successful_tests) > 0:
            avg_response_time = sum(r["duration"] for r in successful_tests) / len(successful_tests)
            recommendations.append(f"平均応答時間: {avg_response_time:.2f}秒 - API応答性能良好")
            
            if any("task_id" in r and r["task_id"] for r in successful_tests):
                recommendations.append("動画生成タスクが正常にスケジューリングされています")
        
        if len(failed_tests) > 0:
            common_errors = {}
            for test in failed_tests:
                error = test.get("error", "Unknown error")
                common_errors[error] = common_errors.get(error, 0) + 1
            
            for error, count in common_errors.items():
                recommendations.append(f"要対応: {error} ({count}件)")
        
        if not successful_tests:
            recommendations.append("⚠️ 全テスト失敗 - APIサーバー起動状況とVEO API設定を確認してください")
        
        return recommendations
    
    def run_all_tests(self):
        """全テストの実行"""
        print("🚀 VEO動画生成テスト開始")
        print("=" * 60)
        
        # API health check
        if not self.check_api_health():
            print("❌ APIサーバーヘルスチェック失敗 - テスト中止")
            return
        
        # Run tests for each prompt
        for prompt_data in TEST_PROMPTS:
            test_result = self.test_video_generation_endpoint(prompt_data)
            self.test_results.append(test_result)
            
            # Brief pause between tests
            time.sleep(2)
        
        # Generate final report
        print("\n" + "=" * 60)
        report = self.generate_test_report()
        
        # Display summary
        print("📊 テスト結果サマリー:")
        print(f"   総テスト数: {report['test_summary']['total_tests']}")
        print(f"   成功: {report['test_summary']['successful_tests']}")
        print(f"   失敗: {report['test_summary']['failed_tests']}")
        print(f"   成功率: {report['test_summary']['success_rate']}%")
        
        print("\n💡 推奨事項:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
        
        # Task monitoring reminder
        successful_tasks = [r for r in self.test_results if r.get("task_id")]
        if successful_tasks:
            print(f"\n⏰ 動画生成監視:")
            print(f"   {len(successful_tasks)}件のタスクが実行中です")
            print(f"   タスク完了まで数分かかる場合があります")
            for task in successful_tasks:
                print(f"   • {task['task_id'][:8]}... ({task['test_name']})")


def main():
    """メイン実行関数"""
    print("🎬 VEO動画生成エンドポイントテスト")
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 テスト対象: {VEO_ENDPOINT}")
    
    # Environment check
    print(f"\n🔧 環境確認:")
    print(f"   Python: {sys.version}")
    print(f"   作業ディレクトリ: {os.getcwd()}")
    print(f"   出力ディレクトリ: {TEST_OUTPUT_DIR}")
    
    try:
        # Run tests
        tester = VEOVideoGenerationTester()
        tester.run_all_tests()
        
        print(f"\n✅ テスト完了!")
        print(f"📁 詳細結果: {TEST_OUTPUT_DIR}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ テスト中断されました")
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()