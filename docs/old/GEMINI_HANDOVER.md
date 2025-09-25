# Gemini-CLI 引き継ぎドキュメント

## 🎯 プロジェクト概要
**プロジェクト名**: AI動的絵画システム (AI Dynamic Painting System)  
**場所**: 千葉県船橋市  
**目的**: 家庭用AI絵画動的表示システム（Raspberry Pi + M5STACK + AIで毎日違う絵画を自動生成・表示）

## 📊 現在のステータス (2025-09-20)

### Phase進捗
- **Phase 1**: ✅ 基盤システム完成（手動動画管理）
- **Phase 2**: ✅ AI統合（VEO API, Gemini API, Weather API）
- **Phase 3**: 🔄 **進行中** - 画像品質改善
- **Phase 4**: 📅 計画中 - 高品質画像生成技術導入

### 🚨 現在の最重要課題
**画像品質が極めて低い問題**
- 問題: matplotlibで2Dアニメ調の低品質グラフィックを生成していた
- 解決方針: Gemini APIを活用した本格的なAI画像生成への転換
- 今日の目標: **Web管理画面からプロンプト調整して品質改善**

## 🏗️ システムアーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         Backend (FastAPI + Python)           │  │
│  │  - API Server (port 8000)                   │  │
│  │  - SQLite Database                          │  │
│  │  - AI Integration (Gemini, VEO, Weather)    │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │       Frontend (React + JavaScript)         │  │
│  │  - Web UI (port 5173)                       │  │
│  │  - Admin Dashboard (開発中)                 │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        ↕ WiFi/HTTP
┌─────────────────────────────────────────────────────┐
│              M5STACK Core2                          │
│  - Button Control                                   │
│  - Sensor Input                                     │
│  - Status Display                                   │
└─────────────────────────────────────────────────────┘
```

## 🔑 API設定状況

### 設定済みAPIキー（`.env`ファイル）
```env
GOOGLE_APPLICATION_CREDENTIALS=./credentials/veo-service-account.json
VEO_PROJECT_ID=ai-dynamic-painting
WEATHER_API_KEY=d09d0921fd5dd500d4f94fc303dbeb3e
GEMINI_API_KEY=AIzaSyA2729B8uM7UyGikkY7GdLBx9mZ__ac0Bc
```

### API統合状態
- **Weather API**: ✅ 動作確認済み（船橋市天気取得）
- **Gemini API**: ✅ 動作確認済み（絵画指示生成成功）
- **VEO API**: ✅ OAuth2認証完了（動画生成待機中）

## 📁 重要ディレクトリ構成

```
/home/aipainting/ai-dynamic-painting/
├── backend/                    # バックエンドAPI
│   ├── src/                   # ソースコード
│   │   ├── api/              # APIエンドポイント
│   │   ├── services/         # ビジネスロジック
│   │   └── models/           # データモデル
│   ├── tests/                # テストファイル群
│   │   ├── simple_ai_generation.py    # Gemini API動作確認済み
│   │   └── phase3_completion_summary.py
│   ├── generated_content/    # 生成コンテンツ保存
│   │   ├── ai_instructions/  # AI絵画指示（成功例あり）
│   │   └── images/          # 生成画像（低品質）
│   └── .env                  # API設定
├── frontend/                  # フロントエンド
│   ├── src/
│   │   ├── components/      # Reactコンポーネント
│   │   └── services/        # APIクライアント
│   └── public/
├── specs/                    # 仕様書（Spec Kit）
│   ├── 001-phase-1-web/     # Phase 1仕様
│   ├── 002-phase-2-ai/      # Phase 2仕様
│   └── 003-api-integration-verification/
├── m5stack/                  # M5STACKファームウェア
├── docs/                     # ドキュメント
└── tests/                    # 統合テスト
```

## 🚀 開発環境セットアップ

### 仮想環境の有効化
```bash
cd /home/aipainting/ai-dynamic-painting
source .venv/bin/activate
```

### サーバー起動方法
```bash
# Backend
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev
```

## 🎨 画像生成の現状と改善計画

### 現在の画像生成フロー
1. Weather API → 船橋市天気取得
2. Gemini API → 絵画制作指示生成（高品質な指示は取得済み）
3. ❌ matplotlib → 低品質2Dグラフィック（問題箇所）

### 成功した絵画指示例
```
場所: /home/aipainting/ai-dynamic-painting/backend/generated_content/ai_instructions/funabashi_ai_painting_20250920_010406.txt

内容: モネ・ルノワール級の詳細な油絵制作指示書
- 構図の詳細説明（前景・中景・背景）
- 色彩とライティングの具体的指示
- 質感と筆致の表現方法
- 船橋市特有の要素の描き方
```

### 今日の改善計画
1. **Web管理画面構築**
   - プロンプト編集機能
   - モデル選択機能
   - リアルタイムプレビュー
   - 生成パラメータ調整

2. **Gemini APIフル活用**
   - Imagen API統合検討
   - プロンプトエンジニアリング
   - マルチモーダル入力対応

## 🔨 開発原則（必須遵守）

### TDD（テスト駆動開発）
```
1. Red Phase: 失敗するテストを先に書く
2. Green Phase: テストを通す最小限のコード
3. Refactor Phase: コード改善
```

### Spec Kit（仕様駆動開発）
```bash
# 仕様作成コマンド
/specify → 機能仕様書作成
/plan → 実装計画作成
/tasks → タスクリスト生成
```

### 品質ゲート
- ユニットテスト: pytest
- APIテスト: FastAPI TestClient
- フロントテスト: Jest + React Testing Library
- E2Eテスト: Playwright

## 📋 本日のタスクリスト

1. **Admin Dashboard構築**
   - [ ] TDD仕様書作成
   - [ ] APIエンドポイント設計
   - [ ] React管理画面実装
   - [ ] プロンプト調整UI

2. **Gemini統合強化**
   - [ ] Gemini-CLI導入
   - [ ] バッチ処理対応
   - [ ] プロンプトテンプレート管理

3. **画像品質改善**
   - [ ] 複数プロンプトテスト
   - [ ] パラメータ最適化
   - [ ] A/Bテスト機能

## 🤝 引き継ぎポイント

### Gemini-CLIで確認すべき項目
1. **API動作確認**
   ```bash
   python backend/tests/simple_ai_generation.py
   ```

2. **生成済みコンテンツ確認**
   ```bash
   ls -la backend/generated_content/ai_instructions/
   ```

3. **システム動作確認**
   ```bash
   curl http://localhost:8000/api/videos
   curl http://localhost:5173/
   ```

### 注意事項
- **場所は船橋市**（東京ではない）
- **純粋な絵画**（文字・テキスト不要）
- **油絵調の高品質**（2Dアニメ調NG）
- **TDD必須**（テスト無しコミット禁止）

## 📚 参照ドキュメント

- `/home/aipainting/ai-dynamic-painting/CLAUDE.md` - プロジェクト設定
- `/home/aipainting/ai-dynamic-painting/README.md` - プロジェクト概要
- `/home/aipainting/ai-dynamic-painting/企画書.md` - ビジネス要件
- `/home/aipainting/ai-dynamic-painting/詳細設計書.md` - 技術設計
- `/home/aipainting/ai-dynamic-painting/specs/` - 各Phase仕様書

## 🎯 成功基準

Phase 3完成条件:
- ✅ 高品質AI絵画生成（美術館レベル）
- ✅ Web管理画面から調整可能
- ✅ 船橋市特化コンテンツ
- ✅ 文字無し純粋絵画
- ✅ 全テストパス

---

**重要**: このプロジェクトは「実用的で美しい、家庭で毎日使えるAI動的絵画システム」の実現を目指しています。技術的完璧性より日常使用での満足度を重視してください。

**開発スタイル**: 「〜なのだ」「すごーい！」という楽観的な博士キャラクターで開発を進めてきました。実験を恐れず、失敗から学ぶスタイルです。

頑張ってください！🎨✨