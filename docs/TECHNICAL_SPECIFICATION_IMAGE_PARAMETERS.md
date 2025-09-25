# 技術仕様書：AI画像生成パラメータ拡張

**バージョン:** 2.0  
**作成日:** 2025-09-22  
**最終更新:** 2025-09-22  
**担当:** Claude (博士)

---

## 📖 概要

本仕様書は、AI動的絵画システムにおける画像生成パラメータの技術的実装詳細を定義します。Google Cloud Imagen 2 APIとの統合を通じて、高品質で制御可能な画像生成機能を提供します。

---

## 🏗️ アーキテクチャ

### システム構成図

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │───▶│   Admin API     │───▶│  Gemini Service │
│  (Parameters)   │    │  (Validation)   │    │  (Imagen 2 API) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ React Component │    │ Pydantic Model  │    │ Google Cloud    │
│   State Mgmt    │    │   Validation    │    │   API Client    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### データフロー

1. **UI Input** → React Component State
2. **State** → Admin API Request (JSON)
3. **API Request** → Pydantic Validation
4. **Validated Data** → Gemini Service
5. **Service Call** → Google Cloud Imagen 2 API
6. **API Response** → Image Bytes
7. **Image Data** → File Storage + Database Record

---

## 📊 パラメータ仕様

### 1. `quality` - 生成品質

| 属性 | 値 |
|------|---|
| **型** | `str` |
| **デフォルト** | `"standard"` |
| **選択肢** | `"standard"`, `"hd"` |
| **Imagen 2 マッピング** | `sampleImageSize`: `"1K"` / `"2K"` |
| **説明** | 生成画像の解像度と品質レベル |

```python
# 実装例
image_size = "2K" if quality == "hd" else "1K"
parameters_dict["sampleImageSize"] = image_size
```

### 2. `aspect_ratio` - アスペクト比

| 属性 | 値 |
|------|---|
| **型** | `str` |
| **デフォルト** | `"1:1"` |
| **選択肢** | `"1:1"`, `"16:9"`, `"9:16"` |
| **Imagen 2 マッピング** | `aspectRatio`: そのまま |
| **説明** | 生成画像の縦横比率 |

```python
# 実装例
parameters_dict["aspectRatio"] = aspect_ratio
```

### 3. `negative_prompt` - ネガティブプロンプト

| 属性 | 値 |
|------|---|
| **型** | `Optional[str]` |
| **デフォルト** | `None` |
| **制限** | 最大500文字 |
| **Imagen 2 マッピング** | `negativePrompt`: そのまま |
| **説明** | 生成画像から除外したい要素 |

```python
# 実装例
if negative_prompt:
    parameters_dict["negativePrompt"] = negative_prompt
```

### 4. `style_preset` - スタイルプリセット

| 属性 | 値 |
|------|---|
| **型** | `Optional[str]` |
| **デフォルト** | `None` |
| **選択肢** | `"anime"`, `"photographic"`, `"digital-art"` |
| **Imagen 2 マッピング** | `stylePreset`: そのまま |
| **説明** | 事前定義されたアートスタイル |

```python
# 実装例
if style_preset:
    parameters_dict["stylePreset"] = style_preset
```

#### スタイルプリセット詳細

| プリセット | 説明 | 適用場面 |
|-----------|------|----------|
| `anime` | アニメ・マンガ風スタイル | キャラクター、イラスト |
| `photographic` | 写真リアリスティック | 風景、ポートレート |
| `digital-art` | デジタルアート風 | 抽象的、現代的表現 |

### 5. `seed` - シード値

| 属性 | 値 |
|------|---|
| **型** | `Optional[int]` |
| **デフォルト** | `None` |
| **範囲** | `0` - `2147483647` |
| **Imagen 2 マッピング** | `seed`: そのまま |
| **説明** | 再現可能な画像生成のための乱数シード |

```python
# 実装例
if seed is not None:
    parameters_dict["seed"] = seed
```

#### シード値の動作

- **None**: ランダムシード（毎回異なる画像）
- **固定値**: 同じプロンプト+シード = 同じ画像
- **範囲**: 32bit符号付き整数の正の範囲

---

## 🔧 実装詳細

### データモデル (`src/models/admin.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional

class GenerationRequest(BaseModel):
    """画像生成リクエストモデル"""
    prompt_template_id: str = Field(..., description="使用するプロンプトテンプレートID")
    model: str = Field(default="gemini-1.5-flash", description="使用モデル")
    
    # === 画像品質パラメータ ===
    quality: str = Field(
        default="standard", 
        description="生成品質 (standard, hd)"
    )
    aspect_ratio: str = Field(
        default="1:1", 
        description="アスペクト比 (1:1, 16:9, 9:16)"
    )
    negative_prompt: Optional[str] = Field(
        default=None, 
        description="ネガティブプロンプト"
    )
    style_preset: Optional[str] = Field(
        default=None, 
        description="スタイルプリセット (anime, photographic, digital-art)"
    )
    seed: Optional[int] = Field(
        default=None, 
        ge=0, 
        le=2147483647, 
        description="シード値 (reproducibility)"
    )
    
    # === その他既存パラメータ ===
    temperature: float = Field(default=0.7, ge=0.1, le=2.0)
    top_k: int = Field(default=40, ge=1, le=100)
    top_p: float = Field(default=0.95, ge=0.1, le=1.0)
    max_tokens: int = Field(default=2048, ge=100, le=8192)
    variables: Optional[Dict[str, str]] = Field(default_factory=dict)
```

### サービス層 (`src/services/gemini_service.py`)

```python
from typing import Optional
import json
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

class GeminiService:
    def generate_image(
        self, 
        prompt: str, 
        quality: str = "standard", 
        aspect_ratio: str = "1:1", 
        negative_prompt: Optional[str] = None,
        style_preset: Optional[str] = None, 
        seed: Optional[int] = None,
        sample_count: int = 1
    ) -> Optional[bytes]:
        """
        Google Cloud Imagen 2 APIを使用した画像生成
        
        Args:
            prompt: 画像生成用テキストプロンプト
            quality: 生成品質 ("standard" or "hd")
            aspect_ratio: アスペクト比 ("1:1", "16:9", "9:16")
            negative_prompt: ネガティブプロンプト
            style_preset: スタイルプリセット
            seed: 再現性確保用シード値
            sample_count: 生成画像数
            
        Returns:
            生成された画像のバイナリデータ、失敗時はNone
        """
        try:
            # APIクライアント初期化
            client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
            prediction_service_client = aiplatform.gapic.PredictionServiceClient(
                client_options=client_options
            )
            
            # エンドポイント設定
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/imagegeneration@006"
            
            # プロンプトインスタンス作成
            instance = json_format.ParseDict({"prompt": prompt}, Value())
            
            # パラメータ構築
            image_size = "2K" if quality == "hd" else "1K"
            
            parameters_dict = {
                "sampleCount": sample_count,
                "sampleImageSize": image_size,
                "aspectRatio": aspect_ratio
            }
            
            # オプションパラメータ追加
            if negative_prompt:
                parameters_dict["negativePrompt"] = negative_prompt
            if style_preset:
                parameters_dict["stylePreset"] = style_preset
            if seed is not None:
                parameters_dict["seed"] = seed
            
            parameters = json_format.ParseDict(parameters_dict, Value())
            
            # API呼び出し
            response = prediction_service_client.predict(
                endpoint=endpoint, 
                instances=[instance], 
                parameters=parameters
            )
            
            # レスポンス処理
            if not response.predictions:
                logger.error("Image generation API returned no predictions.")
                return None
            
            # Base64デコードして画像バイナリ取得
            prediction = response.predictions[0]
            if "bytesBase64Encoded" in prediction:
                import base64
                return base64.b64decode(prediction["bytesBase64Encoded"])
            
            return None
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None
```

### API層 (`src/api/routes/admin.py`)

```python
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

async def generate_with_gemini(generation_id: str, request: GenerationRequest):
    """Gemini APIで画像を生成し、結果を保存"""
    try:
        # テンプレート取得・変数置換
        template = prompt_templates[request.prompt_template_id]
        prompt = template.template
        for var, value in request.variables.items():
            prompt = prompt.replace(f"{{{var}}}", value)
        
        # 全パラメータを指定してGemini API呼び出し
        image_bytes = gemini_service.generate_image(
            prompt=prompt,
            quality=request.quality,
            aspect_ratio=request.aspect_ratio,
            negative_prompt=request.negative_prompt,
            style_preset=request.style_preset,
            seed=request.seed
        )
        
        if image_bytes:
            # 画像保存処理
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backend_root = Path(__file__).resolve().parent.parent.parent.parent
            output_dir = backend_root / "generated_content" / "images"
            output_dir.mkdir(parents=True, exist_ok=True)
            image_path = output_dir / f"admin_generated_{generation_id[:8]}_{timestamp}.png"
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            # 成功結果更新
            generation_results[generation_id].status = GenerationStatus.COMPLETED
            generation_results[generation_id].completed_at = datetime.now()
            generation_results[generation_id].image_path = str(image_path)
        else:
            # 失敗結果更新
            generation_results[generation_id].status = GenerationStatus.FAILED
            generation_results[generation_id].error_message = "Image generation failed"
            generation_results[generation_id].completed_at = datetime.now()
            
    except Exception as e:
        generation_results[generation_id].status = GenerationStatus.FAILED
        generation_results[generation_id].error_message = str(e)
```

---

## 🧪 テスト仕様

### テスト戦略

1. **単体テスト**: 各パラメータ個別の動作確認
2. **統合テスト**: API→サービス→外部API連携確認
3. **モックテスト**: 外部依存排除での自動テスト
4. **エンドツーエンドテスト**: UI→API→画像生成の全工程

### パラメータ別テストケース

```python
# style_preset テスト
def test_generate_with_style_preset_parameter():
    """スタイルプリセットパラメータ指定での画像生成テスト"""
    generation_request = {
        "prompt_template_id": "test-template-001",
        "style_preset": "anime",
        "variables": {"time_of_day": "夕方", "weather": "快晴", "temperature": "20"}
    }
    
    response = client.post("/api/admin/generate", json=generation_request)
    assert response.status_code == 202
    
    generation_id = response.json()["generation_id"]
    status_response = client.get(f"/api/admin/generate/status/{generation_id}")
    status_data = status_response.json()
    
    assert "style_preset" in status_data["request"]
    assert status_data["request"]["style_preset"] == "anime"

# seed テスト
def test_generate_with_seed_parameter():
    """シードパラメータ指定での画像生成テスト"""
    generation_request = {
        "prompt_template_id": "test-template-001",
        "seed": 12345,
        "variables": {"time_of_day": "早朝", "weather": "霧", "temperature": "10"}
    }
    
    response = client.post("/api/admin/generate", json=generation_request)
    assert response.status_code == 202
    
    generation_id = response.json()["generation_id"]
    status_response = client.get(f"/api/admin/generate/status/{generation_id}")
    status_data = status_response.json()
    
    assert "seed" in status_data["request"]
    assert status_data["request"]["seed"] == 12345
```

### モック設定

```python
@pytest.fixture(autouse=True)
def mock_gemini_service(monkeypatch):
    """GeminiService.generate_imageをモックし、APIキーを不要にする"""
    def mock_generate_image(*args, **kwargs):
        return b'dummy_image_bytes'
    
    monkeypatch.setattr(
        "src.services.gemini_service.GeminiService.generate_image",
        mock_generate_image
    )
```

---

## 📈 パフォーマンス仕様

### レスポンス時間目標

| 操作 | 目標時間 | 測定方法 |
|------|----------|----------|
| パラメータ検証 | < 10ms | Pydantic validation |
| API呼び出し準備 | < 50ms | Request preparation |
| Imagen 2 API | < 30s | External API call |
| 画像保存 | < 500ms | File I/O operation |
| 全体レスポンス | < 35s | End-to-end measurement |

### スケーラビリティ

- **同時リクエスト**: 最大10並列
- **キューイング**: バックグラウンドタスク使用
- **ファイルストレージ**: ローカル/クラウドストレージ対応
- **データベース**: SQLite (開発), PostgreSQL (本番)

---

## 🔒 セキュリティ仕様

### 入力検証

```python
# Pydanticによる自動検証
class GenerationRequest(BaseModel):
    quality: str = Field(default="standard", regex="^(standard|hd)$")
    aspect_ratio: str = Field(default="1:1", regex="^(1:1|16:9|9:16)$")
    style_preset: Optional[str] = Field(default=None, regex="^(anime|photographic|digital-art)$")
    seed: Optional[int] = Field(default=None, ge=0, le=2147483647)
    negative_prompt: Optional[str] = Field(default=None, max_length=500)
```

### APIキー管理

```python
# 環境変数による秘匿情報管理
import os
from google.auth import default

class GeminiService:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        # サービスアカウント認証
        credentials, project = default()
        self.credentials = credentials
```

---

## 🔮 将来拡張計画

### Phase C対応予定パラメータ

1. **`image_count`**: 生成画像数 (1-4)
2. **`guidance_scale`**: プロンプト遵守強度 (1.0-20.0)
3. **`safety_filter`**: 安全フィルター設定
4. **`custom_model`**: カスタムファインチューンモデル対応

### UI/UX改善

1. **プリセット管理**: よく使用するパラメータ組み合わせの保存
2. **バッチ生成**: 複数パラメータでの一括生成
3. **A/Bテスト**: パラメータ比較機能
4. **履歴管理**: 生成履歴の詳細分析

---

## 📚 参考文献

- [Google Cloud Imagen 2 API Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)

---

**文書管理**
- **作成者**: Claude (博士)
- **レビュー者**: 未実施
- **承認者**: 未実施
- **次回見直し**: Phase C開始時