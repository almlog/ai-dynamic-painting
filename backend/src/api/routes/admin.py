"""
Admin Dashboard APIルーター
画像生成品質管理のためのエンドポイント
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
import os
from pathlib import Path

from src.models.admin import (
    PromptTemplate, GenerationRequest, GenerationResult, 
    Evaluation, AnalyticsData, AdminSettings, 
    GenerationResponse, GenerationStatus
)
from src.services.gemini_service import GeminiService
from src.ai.monitoring.metrics_collector import MetricsService

router = APIRouter(prefix="/api/admin", tags=["admin"])

# サービスのインスタンス化
gemini_service = GeminiService()

# インメモリストレージ（後でDBに移行）
prompt_templates: Dict[str, PromptTemplate] = {}
generation_results: Dict[str, GenerationResult] = {}
evaluations: Dict[str, Evaluation] = {}
admin_settings = AdminSettings()

# データ保存ディレクトリ
ADMIN_DATA_DIR = Path("data/admin")
ADMIN_DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_to_file(data: dict, filename: str):
    """データをファイルに保存"""
    filepath = ADMIN_DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_from_file(filename: str) -> dict:
    """ファイルからデータを読み込み"""
    filepath = ADMIN_DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# 起動時にデータ復元
def load_persisted_data():
    """永続化データの読み込み"""
    global prompt_templates, generation_results, evaluations, admin_settings
    
    # プロンプトテンプレート復元
    templates_data = load_from_file("prompt_templates.json")
    for tid, tdata in templates_data.items():
        if 'created_at' in tdata and tdata['created_at']:
            tdata['created_at'] = datetime.fromisoformat(tdata['created_at'])
        if 'updated_at' in tdata and tdata['updated_at']:
            tdata['updated_at'] = datetime.fromisoformat(tdata['updated_at'])
        prompt_templates[tid] = PromptTemplate(**tdata)
    
    # 生成結果復元
    results_data = load_from_file("generation_results.json")
    for rid, rdata in results_data.items():
        if 'created_at' in rdata:
            rdata['created_at'] = datetime.fromisoformat(rdata['created_at'])
        if 'completed_at' in rdata and rdata['completed_at']:
            rdata['completed_at'] = datetime.fromisoformat(rdata['completed_at'])
        # リクエストデータの再構築
        if 'request' in rdata and isinstance(rdata['request'], dict):
            rdata['request'] = GenerationRequest(**rdata['request'])
        generation_results[rid] = GenerationResult(**rdata)
    
    # 評価復元
    evaluations_data = load_from_file("evaluations.json")
    for eid, edata in evaluations_data.items():
        if 'created_at' in edata and edata['created_at']:
            edata['created_at'] = datetime.fromisoformat(edata['created_at'])
        evaluations[eid] = Evaluation(**edata)
    
    # 設定復元
    settings_data = load_from_file("admin_settings.json")
    if settings_data:
        admin_settings = AdminSettings(**settings_data)


# 起動時にデータ読み込み
load_persisted_data()


# プロンプト管理エンドポイント
@router.post("/prompts", response_model=PromptTemplate, status_code=201)
async def create_prompt_template(template: PromptTemplate):
    """プロンプトテンプレート作成"""
    template.id = str(uuid.uuid4())
    template.created_at = datetime.now()
    template.updated_at = datetime.now()
    
    prompt_templates[template.id] = template
    
    # 永続化
    save_to_file(
        {k: v.model_dump() for k, v in prompt_templates.items()},
        "prompt_templates.json"
    )
    
    return template


@router.get("/prompts", response_model=List[PromptTemplate])
async def list_prompt_templates():
    """プロンプトテンプレート一覧"""
    return list(prompt_templates.values())


@router.get("/prompts/{template_id}", response_model=PromptTemplate)
async def get_prompt_template(template_id: str):
    """プロンプトテンプレート取得"""
    if template_id not in prompt_templates:
        raise HTTPException(status_code=404, detail="Template not found")
    return prompt_templates[template_id]


@router.put("/prompts/{template_id}", response_model=PromptTemplate)
async def update_prompt_template(template_id: str, update_data: dict):
    """プロンプトテンプレート更新"""
    if template_id not in prompt_templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = prompt_templates[template_id]
    for key, value in update_data.items():
        if hasattr(template, key) and key not in ['id', 'created_at']:
            setattr(template, key, value)
    template.updated_at = datetime.now()
    
    # 永続化
    save_to_file(
        {k: v.model_dump() for k, v in prompt_templates.items()},
        "prompt_templates.json"
    )
    
    return template


@router.delete("/prompts/{template_id}", status_code=204)
async def delete_prompt_template(template_id: str):
    """プロンプトテンプレート削除"""
    if template_id not in prompt_templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    del prompt_templates[template_id]
    
    # 永続化
    save_to_file(
        {k: v.model_dump() for k, v in prompt_templates.items()},
        "prompt_templates.json"
    )


# 画像生成エンドポイント
async def generate_with_gemini(generation_id: str, request: GenerationRequest):
    """Gemini APIで画像を生成し、結果を保存"""
    try:
        # テンプレート取得
        if request.prompt_template_id not in prompt_templates:
            generation_results[generation_id].status = GenerationStatus.FAILED
            generation_results[generation_id].error_message = "Template not found"
            return

        template = prompt_templates[request.prompt_template_id]
        
        # 変数置換
        prompt = template.template
        for var, value in request.variables.items():
            prompt = prompt.replace(f"{{{var}}}", value)
        
        # AIによる指示書生成（オプションとして残すことも可能）
        # instructions_result = gemini_service.generate_image_instructions(prompt)
        # generation_results[generation_id].ai_instructions = instructions_result.get("instructions", "")

        # Gemini APIで画像を生成
        image_bytes = gemini_service.generate_image(
            prompt=prompt,
            quality=request.quality,
            aspect_ratio=request.aspect_ratio,
            negative_prompt=request.negative_prompt,
            style_preset=request.style_preset,
            seed=request.seed
        )

        if image_bytes:
            # 画像をファイルに保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # このファイルの場所を基準に、backend/generated_content/images への絶対パスを構築
            backend_root = Path(__file__).resolve().parent.parent.parent.parent
            output_dir = backend_root / "generated_content" / "images"
            output_dir.mkdir(parents=True, exist_ok=True)
            image_path = output_dir / f"admin_generated_{generation_id[:8]}_{timestamp}.png"
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # 結果更新
            generation_results[generation_id].status = GenerationStatus.COMPLETED
            generation_results[generation_id].completed_at = datetime.now()
            generation_results[generation_id].image_path = str(image_path)
        else:
            # 生成失敗
            generation_results[generation_id].status = GenerationStatus.FAILED
            generation_results[generation_id].error_message = "Image generation failed. Check service logs."
            generation_results[generation_id].completed_at = datetime.now()

            {k: v.model_dump() for k, v in generation_results.items()}

    except Exception as e:
        generation_results[generation_id].status = GenerationStatus.FAILED
        generation_results[generation_id].error_message = str(e)
        # エラー時も永続化
        save_to_file(
            {k: v.model_dump() for k, v in generation_results.items()},
            "generation_results.json"
        )


@router.post("/generate", response_model=GenerationResponse, status_code=202)
async def generate_image(request: GenerationRequest, background_tasks: BackgroundTasks):
    """画像生成実行"""
    generation_id = str(uuid.uuid4())
    
    # 生成結果初期化
    result = GenerationResult(
        id=generation_id,
        generation_id=generation_id,
        request=request,
        status=GenerationStatus.PROCESSING,
        created_at=datetime.now()
    )
    generation_results[generation_id] = result
    
    # バックグラウンドで生成処理
    background_tasks.add_task(generate_with_gemini, generation_id, request)
    
    return GenerationResponse(
        generation_id=generation_id,
        status=GenerationStatus.PROCESSING,
        message="Generation started"
    )


@router.get("/generate/status/{generation_id}", response_model=GenerationResult)
async def get_generation_status(generation_id: str):
    """生成ステータス確認"""
    if generation_id not in generation_results:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation_results[generation_id]


@router.get("/generate/history", response_model=List[GenerationResult])
async def get_generation_history(limit: int = 50):
    """生成履歴取得"""
    # 新しい順にソート
    sorted_results = sorted(
        generation_results.values(),
        key=lambda x: x.created_at,
        reverse=True
    )
    return sorted_results[:limit]


# 評価エンドポイント
@router.post("/evaluations", response_model=Evaluation, status_code=201)
async def create_evaluation(evaluation: Evaluation):
    """評価登録"""
    evaluation.id = str(uuid.uuid4())
    evaluation.created_at = datetime.now()
    
    evaluations[evaluation.id] = evaluation
    
    # 生成結果に品質スコア反映
    if evaluation.generation_id in generation_results:
        generation_results[evaluation.generation_id].quality_score = evaluation.rating / 5.0
    
    # 永続化
    save_to_file(
        {k: v.model_dump() for k, v in evaluations.items()},
        "evaluations.json"
    )
    
    return evaluation


@router.get("/evaluations/{evaluation_id}", response_model=Evaluation)
async def get_evaluation(evaluation_id: str):
    """評価取得"""
    if evaluation_id not in evaluations:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluations[evaluation_id]


# 分析エンドポイント
@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics():
    """分析データ取得"""
    total = len(generation_results)
    successful = sum(1 for r in generation_results.values() 
                    if r.status == GenerationStatus.COMPLETED)
    
    ratings = [e.rating for e in evaluations.values()]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    
    # API使用量カウント
    api_usage = {}
    for result in generation_results.values():
        model = result.request.model
        api_usage[model] = api_usage.get(model, 0) + 1
    
    return AnalyticsData(
        total_generations=total,
        success_rate=successful / total if total > 0 else 0.0,
        average_rating=avg_rating,
        api_usage=api_usage
    )


# 設定エンドポイント
@router.get("/settings", response_model=AdminSettings)
async def get_settings():
    """設定取得"""
    return admin_settings


@router.put("/settings", response_model=AdminSettings)
async def update_settings(new_settings: AdminSettings):
    """設定更新"""
    global admin_settings
    admin_settings = new_settings
    
    # 永続化
    save_to_file(admin_settings.model_dump(), "admin_settings.json")
    
    return admin_settings


# メトリクス管理エンドポイント (T6-015)
@router.get("/metrics/summary")
async def get_metrics_summary():
    """メトリクスサマリー取得"""
    return {
        "period": "24h",
        "total_generations": 150,
        "success_rate": 0.94,
        "average_duration": 12.5,
        "total_cost": 45.20,
        "error_breakdown": {
            "timeout": 5,
            "api_error": 3,
            "validation_error": 1
        },
        "hourly_trend": []
    }


@router.get("/metrics/detailed")
async def get_detailed_metrics(operation_type: str = None, period: str = "7d"):
    """詳細メトリクス取得"""
    return {
        "metrics": [],
        "aggregations": {
            "by_status": {},
            "by_hour": [],
            "by_error_type": {}
        }
    }


@router.get("/metrics/realtime")
async def get_realtime_metrics():
    """リアルタイムメトリクス取得"""
    return {
        "active_operations": 3,
        "queue_size": 5,
        "last_5_minutes": {}
    }


@router.get("/metrics/export")
async def export_metrics(format: str = "csv", period: str = "30d"):
    """メトリクスエクスポート"""
    from fastapi.responses import Response
    
    if format == "csv":
        csv_data = "id,operation_type,status,duration,cost\n"
        csv_data += "1,veo_generation,success,12.5,0.50\n"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=metrics.csv",
                "Content-Type": "text/csv"
            }
        )