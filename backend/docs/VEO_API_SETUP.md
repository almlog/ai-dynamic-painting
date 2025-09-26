# VEO API セットアップガイド

VEO API（Google Cloud Vertex AI Video Generation）の技術的接続確立手順

## 📋 前提条件

1. **Google Cloud アカウント**が必要
2. **Google Cloud プロジェクト**の作成
3. **請求先アカウント**の設定（VEO API使用料金のため）

## 🔑 認証設定手順

### オプション 1: サービスアカウント認証（本番環境推奨）

#### 1. Google Cloud Console でサービスアカウント作成

```bash
# Google Cloud Console にアクセス
# https://console.cloud.google.com/

# プロジェクト選択: ai-dynamic-painting
# IAMと管理 → サービスアカウント → 作成
```

#### 2. 必要な権限を付与

サービスアカウントに以下のロールを付与：
- `Vertex AI User` - VEO API実行用
- `Storage Object Viewer` - モデルアーティファクト読み取り用
- `Service Usage Consumer` - API使用状況確認用

#### 3. JSON キーファイル作成・ダウンロード

```bash
# サービスアカウント詳細ページで「キー」タブ
# 「キーを追加」→ JSON形式でダウンロード
# ファイルを以下のパスに配置
cp ~/Downloads/service-account-key.json ./backend/credentials/veo-service-account.json
```

#### 4. 環境変数設定

```bash
# .envファイルで以下を設定
GOOGLE_APPLICATION_CREDENTIALS=./credentials/veo-service-account.json
GOOGLE_CLOUD_PROJECT=ai-dynamic-painting
GOOGLE_CLOUD_LOCATION=us-central1
```

### オプション 2: Application Default Credentials（開発環境推奨）

#### 1. gcloud CLI インストール

```bash
# Raspberry Pi / Linux
curl https://sdk.cloud.google.com | bash
source ~/.bashrc
```

#### 2. gcloud 初期化

```bash
# Google Cloud にログイン
gcloud auth login

# プロジェクト設定
gcloud config set project ai-dynamic-painting

# Application Default Credentials設定
gcloud auth application-default login
```

#### 3. 認証確認

```bash
# 認証状態確認
gcloud auth list

# プロジェクト確認
gcloud config get-value project
```

## 🔌 API有効化

必要なAPIを有効化：

```bash
# Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Compute Engine API（Vertex AIで使用）
gcloud services enable compute.googleapis.com

# Cloud Storage API（モデルアーティファクト用）
gcloud services enable storage.googleapis.com

# Service Usage API（使用状況監視用）
gcloud services enable serviceusage.googleapis.com
```

## 🧪 接続テスト実行

認証設定完了後、接続テストを実行：

```bash
# 仮想環境アクティベート
source .venv/bin/activate

# VEO API接続テスト実行
python backend/scripts/test_veo_connection.py
```

### 期待される出力（成功時）

```
============================================================
VEO API Connection Test Script
============================================================

📦 Step 1: Checking environment...
✅ Service account key found: ./credentials/veo-service-account.json
📍 Project ID: ai-dynamic-painting
📍 Location: us-central1

📦 Step 2: Testing library imports...
✅ google-cloud-aiplatform successfully imported
   Version: 1.38.1

📦 Step 3: Testing Vertex AI connection...
✅ Vertex AI client initialized successfully
✅ Found 3 image/video generation models:
   - imagen-3.0-generate-001 (ID: projects/ai-dynamic-painting/locations/us-central1/models/imagen-3.0-generate-001)
   - veo-2-1024p-preview (ID: projects/ai-dynamic-painting/locations/us-central1/models/veo-2-1024p-preview)

✅ Connection to Vertex AI successful!
   Authentication is working correctly

============================================================
Test Summary
============================================================
✅ SUCCESS: VEO API connection test passed!

Next steps:
1. Enable required APIs if not already enabled
2. Create a VEO/Imagen model or use pre-trained models
3. Implement the VEO client wrapper in the application
```

## 💰 コスト管理

### VEO API料金体系（概算）

- **VEO-2 Video Generation**: ~$0.50 per 5-30秒動画
- **Imagen-3 Image Generation**: ~$0.10 per 1024x1024画像
- **API呼び出し**: 大抵無料（リスト取得など）

### 予算管理設定

```bash
# .envでの予算制限設定
DAILY_BUDGET_LIMIT=10.00     # 1日$10制限
MONTHLY_BUDGET_LIMIT=100.00  # 月$100制限
VEO_COST_PER_GENERATION=0.50 # 1回あたり概算コスト
```

### 予算アラート設定

```bash
# Google Cloud Console での予算アラート
# 請求 → 予算とアラート → 予算作成
# 閾値: $5, $10, $20でアラート設定
```

## 🔒 セキュリティ考慮事項

### 認証情報の保護

```bash
# .gitignoreに追加済み（確認用）
echo "credentials/" >> .gitignore
echo ".env" >> .gitignore

# 環境変数ファイルの権限設定
chmod 600 backend/.env
chmod 600 backend/credentials/veo-service-account.json
```

### アクセス制限

- サービスアカウントには**最小限の権限**のみ付与
- 定期的なキーローテーション（90日推奨）
- 不要なAPIの無効化

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 認証エラー
```
❌ Authentication error: Could not automatically determine credentials
```

**解決方法:**
1. `GOOGLE_APPLICATION_CREDENTIALS` 環境変数の確認
2. サービスアカウントキーファイルの存在確認
3. gcloud ADC認証の実行

#### プロジェクトアクセスエラー
```
❌ Google API error: Project not found or insufficient permissions
```

**解決方法:**
1. プロジェクトIDの確認
2. プロジェクトの請求先アカウント設定確認
3. サービスアカウント権限の確認

#### API無効化エラー
```
❌ Google API error: Vertex AI API has not been used in this project
```

**解決方法:**
```bash
gcloud services enable aiplatform.googleapis.com
```

#### クォータ超過エラー
```
❌ Google API error: Quota exceeded for quota metric
```

**解決方法:**
1. Google Cloud Console でクォータ確認
2. 必要に応じてクォータ増加リクエスト
3. 使用量の監視・最適化

## 📚 次のステップ

VEO API接続確認後:

1. **VEO クライアントラッパー実装** (`backend/src/ai/services/veo_client.py`)
2. **動画生成API エンドポイント実装** (`backend/src/api/routes/veo_generation.py`)
3. **フロントエンド統合** (VEO生成リクエストUI)
4. **M5STACKハードウェア統合** (センサー→VEO生成トリガー)

---

**⚠️ 重要**: 本番運用前は必ずコスト監視・予算制限を設定してください。VEO APIは従量課金制のため、予期しない高額請求を避けるための対策が重要です。