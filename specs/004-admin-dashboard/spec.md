# Admin Dashboard仕様書 - AI絵画品質管理システム

## 概要
AI動的絵画システムの画像生成品質を改善するための管理者用Webダッシュボード。プロンプト調整、モデル選択、パラメータチューニングをリアルタイムで行える。

## 機能要件

### 1. プロンプト管理機能
- **プロンプトエディタ**
  - リアルタイム編集
  - テンプレート保存/読み込み
  - 変数置換サポート（時間、天気、場所）
  - プレビュー機能

- **プロンプトテンプレート**
  - デフォルトテンプレート提供
  - カスタムテンプレート作成
  - バージョン管理
  - A/Bテスト設定

### 2. 画像生成制御
- **生成パラメータ調整**
  - モデル選択（gemini-1.5-flash, gemini-1.5-pro）
  - Temperature設定（0.1-2.0）
  - Top-K, Top-P調整
  - 最大トークン数設定

- **生成実行**
  - 即時生成ボタン
  - バッチ生成（複数バリエーション）
  - スケジュール生成
  - 生成履歴管理

### 3. 品質評価機能
- **画像プレビュー**
  - サムネイル一覧
  - フルサイズ表示
  - メタデータ表示
  - 比較ビュー（並べて表示）

- **評価システム**
  - 5段階評価
  - タグ付け機能
  - コメント記録
  - 自動品質スコア算出

### 4. データ分析
- **生成統計**
  - 成功/失敗率
  - API使用量
  - コスト計算
  - 時間帯別パフォーマンス

- **品質トレンド**
  - 評価スコア推移
  - プロンプト効果分析
  - パラメータ相関分析

## 技術仕様

### バックエンドAPI（FastAPI）

#### エンドポイント設計
```python
# プロンプト管理
POST   /api/admin/prompts              # プロンプト作成
GET    /api/admin/prompts              # プロンプト一覧
PUT    /api/admin/prompts/{id}         # プロンプト更新
DELETE /api/admin/prompts/{id}         # プロンプト削除

# 画像生成
POST   /api/admin/generate             # 画像生成実行
GET    /api/admin/generate/status/{id} # 生成ステータス確認
GET    /api/admin/generate/history     # 生成履歴取得

# 品質評価
POST   /api/admin/evaluations          # 評価登録
GET    /api/admin/evaluations/{id}     # 評価取得
GET    /api/admin/analytics           # 分析データ取得

# 設定管理
GET    /api/admin/settings            # 設定取得
PUT    /api/admin/settings            # 設定更新
```

### フロントエンド（React）

#### コンポーネント構成
```
AdminDashboard/
├── components/
│   ├── PromptEditor/          # プロンプト編集
│   │   ├── Editor.tsx
│   │   ├── Templates.tsx
│   │   └── Variables.tsx
│   ├── GenerationControl/     # 生成制御
│   │   ├── Parameters.tsx
│   │   ├── ModelSelector.tsx
│   │   └── GenerateButton.tsx
│   ├── Gallery/               # 画像ギャラリー
│   │   ├── ImageGrid.tsx
│   │   ├── ImageDetail.tsx
│   │   └── Comparison.tsx
│   └── Analytics/             # 分析
│       ├── Statistics.tsx
│       ├── Charts.tsx
│       └── Reports.tsx
├── services/
│   ├── adminApi.ts           # API通信
│   └── geminiService.ts      # Gemini連携
└── pages/
    └── AdminDashboard.tsx     # メインページ
```

### データモデル

```python
# プロンプトテンプレート
class PromptTemplate(BaseModel):
    id: str
    name: str
    template: str
    variables: List[str]
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

# 生成リクエスト
class GenerationRequest(BaseModel):
    prompt_template_id: str
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    top_k: int = 40
    top_p: float = 0.95
    max_tokens: int = 2048

# 生成結果
class GenerationResult(BaseModel):
    id: str
    request: GenerationRequest
    ai_instructions: str
    image_path: Optional[str]
    metadata: Dict[str, Any]
    quality_score: Optional[float]
    created_at: datetime

# 評価
class Evaluation(BaseModel):
    id: str
    generation_id: str
    rating: int  # 1-5
    tags: List[str]
    comment: Optional[str]
    created_at: datetime
```

## テスト計画（TDD）

### ユニットテスト
```python
# backend/tests/test_admin_api.py
def test_create_prompt_template():
    """プロンプトテンプレート作成テスト"""
    
def test_generate_with_parameters():
    """パラメータ指定での生成テスト"""
    
def test_evaluate_generation():
    """生成結果評価テスト"""
```

### 統合テスト
```python
# backend/tests/integration/test_admin_flow.py
def test_complete_generation_flow():
    """プロンプト作成→生成→評価の一連フロー"""
```

### E2Eテスト
```javascript
// frontend/tests/e2e/admin-dashboard.spec.js
test('管理画面での画像生成フロー', async () => {
    // 1. プロンプト入力
    // 2. パラメータ調整
    // 3. 生成実行
    // 4. 結果確認
    // 5. 評価入力
});
```

## 実装優先順位

### Phase 1（今日実装）
1. 基本的なプロンプトエディタ
2. Gemini API連携での生成実行
3. 生成結果の表示
4. 簡単な評価機能

### Phase 2（明日以降）
1. テンプレート管理
2. 詳細なパラメータ調整
3. バッチ生成
4. 分析機能

## 成功基準
- プロンプト変更で画像品質が改善される
- 5分以内に新しいプロンプトをテストできる
- 生成結果を比較評価できる
- API使用量とコストが可視化される

## セキュリティ考慮事項
- 管理画面は認証必須（初期実装では簡易認証）
- APIキーは環境変数で管理
- 生成履歴は30日で自動削除
- レート制限実装（1分10リクエストまで）