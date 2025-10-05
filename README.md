# 🎨 AI動的絵画システム

> 「AI自動生成の美しい動画をM5STACKで簡単操作できる、インテリジェントな家庭用動的絵画システムなのだ〜！」 - 博士  
> **✅ Phase 6 進行中: VEO API統合開始 - Video API完全実装 + TDD品質重視開発確立 (28%完了)**

## 📋 プロジェクト概要

AI動的絵画システムは、家庭のリビング空間を美術館のような動的アート展示空間に変える革新的なシステムです。**Phase 6 VEO API統合**を開始し、AI動画生成機能の基盤システム実装と品質重視TDD開発フローの確立を完了しました。

### 🎯 核心価値提案（Phase 1完了）
- **簡単操作**: M5STACKの物理ボタンで直感的な動画制御
- **手軽管理**: Web UIで動画のアップロード・管理が簡単
- **安定表示**: Raspberry Piで24時間安定した動画再生
- **コスト効率**: 市販品の1/3コストで高品質な表示環境

### 🎉 **Phase 6進行状況 - 2025-09-23** ⭐ **28% COMPLETED (7/25 Tasks)**

#### 🚀 **今日の開発成果: T6-007 Video API完全実装**
- **VEO API統合基盤完成**: generateVideo, getVideoStatus, getVideoGenerationHistory, cancelVideoGeneration
- **TDD品質重視開発確立**: RED→GREEN→REFACTOR完全サイクル実証
- **テスト品質向上**: 25/25テスト100%PASS、Mock Data Factory導入、エッジケース網羅
- **コード品質向上**: バリデーション統一、型定義最適化、技術的負債解消

#### **🤖 Claude博士との協働開発体制**
本プロジェクトは**Claude博士（AI開発パートナー）**との協働により、TDD（テスト駆動開発）とSpec Kit仕様駆動開発の組み合わせで高品質システムを実現しています：
- **SuperClaude Framework活用**: 効率的なタスク管理と品質保証
- **段階的実装**: Red-Green-Refactor サイクルの厳格適用
- **継続的品質改善**: 実証ベース開発と検証の徹底

### 🔧 完了済み開発フェーズ（**Phase 4 完全完成**）

#### ✅ **Phase 4-A: バックエンドv2.4.0 完成**
- **🎨 AI画像生成API**: 5つのパラメータ完全対応
  - `quality`: standard/hd品質制御
  - `aspect_ratio`: 1:1/16:9/9:16アスペクト比
  - `style_preset`: anime/photographic/digital-art スタイル
  - `seed`: 再現可能な画像生成 (0-2147483647)
  - `negative_prompt`: 除外要素精密制御
- **🛡️ API Mock完全実装**: 外部依存排除・テスト安定化
- **🧪 18/18テスト成功**: TDD品質保証体制確立
- **📊 Admin API完全機能**: `/api/admin/generate` 等3エンドポイント

#### ✅ **Phase 4-B: フロントエンド統合 完成**
- **📱 APIサービスクライアント完成**: TypeScript型定義 + HTTP通信層
- **🎛️ パラメータUI完成**: 5つの新パラメータ制御コンポーネント実装
- **🔗 UI-API統合完成**: Mock削除・実API接続・エラーハンドリング実装
- **🧩 AIGenerationDashboard**: モックデータ完全削除・API統合・型安全性確保

#### ✅ **Phase 4-C: 統合品質確保 完成** ⭐ **100% VERIFIED**
- **🎯 E2Eテスト100%成功**: Playwright 7/7テスト完全通過（T4C-001完了）
  - 完全なユーザーフロー検証（UI操作→API通信→履歴更新）
  - 動的履歴更新システム実装（POST→GETデータ連動）
  - リアルタイム反映の品質保証
- **🧪 フロントエンド品質保証**: **100%成功率**（T4B-002完了）⭐ **CORRECTED**
  - **28/28ユニットテスト成功** (Previously incorrectly reported as 27/28)
  - React Testing Library完全統合
  - APIモック・非同期処理・アクセシビリティ完全対応

## 📚 VEO動画生成システム - ユーザーガイド

**Phase 6で新しく実装されたVEO動画生成機能の詳細な使い方ガイドです：**

### 🎬 **ユーザー向けドキュメント**
- **[VEO動画生成ユーザーガイド](docs/VEO動画生成ユーザーガイド.md)** - 基本的な使い方、プロンプト作成ガイド、活用事例
- **[VEOパラメータ・コスト詳細ガイド](docs/VEOパラメータ・コスト詳細ガイド.md)** - 技術仕様、料金体系、最適化手法
- **[VEOトラブルシューティングガイド](docs/VEOトラブルシューティングガイド.md)** - 問題診断、解決方法、サポート情報

### 🎯 **クイックスタート**
1. **Webアクセス**: `http://localhost:5173/` でシステム起動
2. **動画生成**: 「Generate Video」→ プロンプト入力 → パラメータ設定
3. **履歴確認**: 「Generation History」で過去の動画を管理・再生

### ✨ **主な機能**
- **テキストから動画生成**: 日本語・英語プロンプト対応
- **高品質出力**: 720p〜4K、24〜60fps対応  
- **コスト管理**: 予算制限、使用量追跡、料金計算
- **履歴管理**: プレビュー、ダウンロード、削除機能

## 🏗️ システム構成

```
[M5STACK] ← WiFi → [Raspberry Pi] ← HDMI → [PCモニター]
    ↓                    ↓                      ↓
センサー・制御     AI統合メイン処理         動画表示
                        ↓
            [External APIs - Phase 2実装済み ✅]
          [VEO API ✅, 品質評価 ✅, 監視システム ✅]
```

### ハードウェア
- **Raspberry Pi 4/5**: メインシステム
- **M5STACK**: センサー・制御デバイス  
- **PCモニター**: 24-32インチ表示装置

### ソフトウェア（**Phase 6 VEO統合システム**）
- **Backend**: Python + FastAPI (VEO API統合済み) ✅
- **Frontend**: React + TypeScript (動画生成UI実装済み) ✅  
- **AI Services**: VEO API完全実装 + コスト管理 ✅
- **Testing**: 負荷テスト・E2Eテスト完備 ✅
- **Hardware**: M5STACK基本制御 ✅
- **Database**: SQLite基本スキーマ ✅
- **Architecture**: 拡張可能設計基盤 ✅

## 🚀 起動方法（Gemini混乱防止版）

### ⚡ 超簡単起動（推奨）

**たった1行で起動完了！**
```bash
/home/aipainting/ai-dynamic-painting/scripts/quick-start.sh
```

**完了**: 自動的に両サーバーが起動します！

### 📊 アクセス確認
- **🎨 Frontend（メインUI）**: http://localhost:5173
- **🔧 Backend API**: http://localhost:8000  
- **📚 API仕様書**: http://localhost:8000/docs
- **🎬 VEO動画生成**: http://localhost:8000/api/ai/health

### 🔍 起動確認コマンド
```bash
# すべて正常なら "healthy" が返る
curl http://localhost:8000/health
curl http://localhost:5173/
curl http://localhost:8000/api/ai/health
```

---

## 🛠️ 手動起動（上級者向け）

### 1. バックエンド起動
```bash
cd /home/aipainting/ai-dynamic-painting/backend
source ../.venv/bin/activate
PYTHONPATH=/home/aipainting/ai-dynamic-painting/backend/src python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. フロントエンド起動（新しいターミナル）
```bash
cd /home/aipainting/ai-dynamic-painting/frontend
npm run dev
```

---

## 📋 詳細な起動ガイド

**詳しい起動手順・トラブルシューティング**: [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

### その他の便利コマンド

```bash
# プロジェクトディレクトリに移動
cd-ai

# Serena MCPサーバーを直接起動
serena-start

# 開発環境起動（複数の方法）
start-ai-dev  # または
博士          # 日本語でも起動可能！
```

## 📁 プロジェクト構造

```
ai-dynamic-painting/
├── docs/                    # プロジェクトドキュメント
│   ├── 企画書.md
│   ├── 詳細設計書.md
│   ├── 実装計画書.md
│   ├── CLAUDE.md
│   └── PERSONA.md
├── phase_status/           # フェーズ進捗管理
├── core/                   # コアシステム
├── api/                    # API統合層
├── web/                    # Web UI
├── m5stack/               # M5STACKプログラム
├── database/              # データ管理
├── tests/                 # テストスイート
├── scripts/               # 開発・運用スクリプト
│   └── start_dev.sh      # 開発環境起動スクリプト
├── deployment/            # デプロイメント
├── .serena/              # Serena MCP設定
├── .venv/                # Python仮想環境
└── README.md             # このファイル
```

## 🔄 開発進捗状況

### Phase 1: 基盤システム構築 ✅ **完了**
- [x] プロジェクト設計・開発環境構築
- [x] FastAPI Backend + React Frontend基盤
- [x] M5STACK Hardware Integration
- [x] 基本動画管理・表示システム

### Phase 2-3: AI統合基盤 ✅ **完了**
- [x] AI統合アーキテクチャ設計
- [x] Google Cloud Imagen 2 API統合準備
- [x] 基本データモデル・API設計

### Phase 4: AI画像品質向上機能
#### Phase 4-A: バックエンド拡張 ✅ **完了 (v2.4.0)**
- [x] **5つの画像生成パラメータ実装** 
  - [x] `quality` (standard/hd)
  - [x] `aspect_ratio` (1:1/16:9/9:16)  
  - [x] `style_preset` (anime/photographic/digital-art)
  - [x] `seed` (0-2147483647)
  - [x] `negative_prompt` (除外要素制御)
- [x] **Admin API完全実装** (`/api/admin/generate` etc.)
- [x] **18/18テスト成功** (TDD完全準拠)
- [x] **API Mock実装** (外部依存排除)

#### Phase 4-B: フロントエンド接続 🔄 **現在実装中**
- [ ] **T4B-001**: APIサービスクライアント実装 (`frontend/src/services/api.ts`)
- [ ] **T4B-002**: UIコンポーネント改修 (5つのパラメータUI)
- [ ] **T4B-003**: UI-API完全統合 (Mock削除・実API接続)

#### **バックエンド基盤** ✅ **基本稼働中**
- [x] 基本データモデル実装
- [x] FastAPI基本構成
- [x] SQLite基本スキーマ
- [x] 基本テスト環境構築
- [ ] AI画像生成パラメータ拡張 📋 設計段階
- [ ] VEO API統合準備 📋 認証・設定準備中
- [ ] 高度データ検証 📋 要件定義中
- [ ] パフォーマンス最適化 📋 計画中

#### **Phase B: フロントエンド接続** 🔄 **準備完了 - 次回実施**
- [ ] **API Service Layer実装** - frontend/src/services/api.ts統合
- [ ] **React Component統合** - AIGenerationDashboard.tsx API接続
- [ ] **Parameter UI Controls** - 5つの新パラメータUI実装
- [ ] **モックデータ削除** - 完全バックエンド統合
- [ ] **リアルタイム生成状況表示** - 進捗・エラー・完了状態UI

#### **Phase C: 統合品質確保** 📋 **計画中**
- [ ] **テストカバレッジ向上** - 目標40%以上
- [ ] **E2Eテスト実装** - UI→API→画像生成全工程
- [ ] **パフォーマンス最適化** - レスポンス時間・同時リクエスト対応
- [ ] **セキュリティ強化** - 入力検証・認証・認可
- [ ] **カスタムモデル対応** - Google標準→ファインチューンモデル

## 🚨 CRITICAL: 開発品質管理プロトコル - 絶対遵守

### 🔴 技術選択検証プロトコル（必須）
以下の検証を**実装前に必ず実行**すること：

#### 1. ツール・ライブラリ選択検証
```bash
# 必須確認事項
1. 目的と手段の一致確認
   - 目的: "AI画像生成" → 手段: Google Cloud Imagen 2 ✅
   - 目的: "AI画像生成" → 手段: matplotlib ❌ (可視化ツール)

2. 技術スタック妥当性検証
   - 要求品質: "美術館レベル" → matplotlib図形描画 ❌
   - 要求品質: "美術館レベル" → AI画像生成API ✅

3. 代替案検討必須
   - 他の選択肢を最低3つ検討
   - それぞれの利点・欠点を文書化
   - 最適解の根拠を明確化
```

#### 2. アーキテクチャ決定記録（ADR）必須
```bash
# 全ての技術選択で記録すること
1. 背景・問題の説明
2. 検討した選択肢（最低3つ）
3. 選択した解決策
4. 選択理由と根拠
5. 予想される結果と影響
```

#### 3. 実装前検証チェックリスト
```bash
□ 目的と手段が一致している
□ 要求品質に技術選択が適合している  
□ 代替案を3つ以上検討した
□ 選択理由を明文化した
□ チーム・ユーザーレビューを受けた
□ 失敗時のフォールバック計画がある
```

### 🔴 品質ゲート（実装中）
```bash
# 各実装段階での必須確認
1. 設計段階: アーキテクチャ妥当性検証
2. 実装段階: TDD厳守（Red→Green→Refactor）
3. テスト段階: 実機検証必須
4. 完成判定: 品質基準達成確認
```

### 🔴 失敗事例からの学習
**Case Study: matplotlib画像生成事件 (2025-09-20)**
- **問題**: AI画像生成にmatplotlib使用
- **根本原因**: 技術選択段階での検証不足
- **影響**: 4ファイル・375行の無駄実装、品質目標未達
- **教訓**: 目的と手段の一致確認が最重要
- **防止策**: 本プロトコル策定・遵守

## 🛠️ 開発環境セットアップ

### 必要条件
- Raspberry Pi 4/5 (8GB RAM推奨)
- Python 3.11+
- Node.js (Web UI用)
- M5STACK開発環境

### 手動セットアップ（参考）

```bash
# 1. リポジトリクローン
git clone <repository-url>
cd ai-dynamic-painting

# 2. 仮想環境作成・アクティベート
python -m venv .venv
source .venv/bin/activate

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. Serena MCP設定
serena project generate-yml
```

**注意**: 通常は `ai-dev` コマンドを使用してください！

## 🎯 開発哲学

### 新しい開発スタイル：Gemini司令塔 x Claude実装者

本プロジェクトは、AIエージェントの強みを最大限に活かすため、以下の新しい開発スタイルを採用します。

- **Geminiの役割（司令塔/戦略家）**
  - プロジェクトの要件を深く理解し、全体戦略を立案します。
  - 複雑なタスクを明確なステップに分解し、具体的な指示を出します。
  - TDDの「Red」フェーズ（失敗するテストの定義）と「Green」フェーズ（テストがパスする条件）を明確に定義します。
  - 進捗状況、問題点、次の指示などを積極的にドキュメント化し、透明性を確保します。
  - コンテキスト処理の限界を認識し、必要に応じて博士やClaude博士に確認を求めます。

- **Claudeの役割（コーダー/実装者）**
  - Geminiからの明確な指示に基づき、高品質なコードを実装します。
  - TDDの「Green」フェーズ（テストをパスするコードの実装）を担当します。
  - 自身の優れたコーディング能力とコンテキスト処理能力を最大限に活用します。

## 🚨 CRITICAL: 開発品質保証ルール - 絶対遵守 🚨

### SuperClaude必須使用ルール
**すべての開発作業でSuperClaudeフラグの使用が義務**

#### 博士の作業開始儀式（毎回必須・例外なし）
1. **Spec駆動開発状況確認**: 現在のフェーズと実装状況確認
2. **システム動作確認**: Backend/Frontend実動作確認  
3. **状況判断**: 現在のタスクの性質を分析
4. **フラグ選択**: 適切なSuperClaudeフラグ組み合わせを選択
5. **フラグ実行**: 会話開始時に必ずフラグを明記
6. **作業実行**: フラグに基づく動作モードで開発

### TDD + 仕様駆動開発必須ルール
**TDDサイクルを破った実装は全て無効・やり直し**

#### Red-Green-Refactor + Hardware サイクルの完全厳守
1. **🔴 Red**: 失敗するテストを**必ず最初に書く**（ユニット・統合・ハードウェア）
2. **🟢 Green**: テストを通すための**最小限のコード**を書く（余計な機能追加禁止）
3. **🔧 Hardware**: 実際のハードウェアで動作確認（モック・シミュレーション不可）
4. **♻️ Refactor**: テストが通る状態を保ちながらコード改善

#### Spec Kit仕様駆動開発必須
- **仕様化**: `/specify` コマンドで機能仕様作成
- **計画策定**: `/plan` コマンドで実装計画作成  
- **タスク生成**: `/tasks` コマンドで実装タスク生成
- **段階実装**: TDD + ハードウェア確認
- **検証・次フェーズ**: 完成確認・次仕様作成

### 重要な原則
- **TDD必須**: Red → Green → Refactor サイクルの厳守
- **ハードウェア実機確認**: 全てのハードウェアで実際の動作確認必須
- **段階的実装**: 各フェーズ完成まで次に移行しない
- **障害許容設計**: 一部機能停止でもシステム全体は継続動作
- **コスト意識**: 将来のVEO API使用量・電気代等の運用コスト計画
- **事実検証**: すべての報告は客観的証拠に基づく（虚偽報告禁止）

## 🔧 開発ツール

### Serena MCP
- **semantic code retrieval**: AIによるコード理解と検索
- **intelligent editing**: コンテキストを理解した編集支援
- **LSP integration**: 言語サーバープロトコル統合

### SuperClaude統合 - 必須使用なのだ！
SuperClaudeフラグを**必ず使って**効率的開発を実現するのだ〜！

#### 基本フラグ（実際のコマンド）
```bash
# プロジェクト分析・状況確認
--serena --think

# 実装・ハードウェア統合
--serena --validate --task-manage

# デバッグ・問題解決
--introspect --sequential --think

# 新機能・探索的開発
--brainstorm --serena --think
```

#### 博士の実験フロー（必須手順）
1. **状況分析**: `--serena --think` でプロジェクト状況を把握
2. **探索思考**: `--brainstorm` で新しいアイデアを発散
3. **実装**: `--serena --validate --task-manage` で体系的実装
4. **デバッグ**: `--introspect --sequential` で問題を段階的解決
5. **振り返り**: `--think` で構造化された分析と次のステップ決定

**重要**: 博士は毎回の作業で適切なSuperClaudeフラグを使用することが必須なのだ！

### Claude Code統合
```bash
# Claude Codeから接続
serena start-mcp-server --project /home/aipainting/ai-dynamic-painting

# 設定
claude --config
```

## 📊 完成基準

### Phase 1 完成基準 ✅ **ALL COMPLETE**
- [x] 手動動画アップロード・表示が Raspberry Pi + モニターで動作 ✅
- [x] Web UI で動画管理が PC・スマホから操作可能 ✅  
- [x] **M5STACK でボタン操作・センサー読み取りが正常動作** ⭐ **完了**
- [x] **35.5時間連続稼働で安定動作（メモリリーク・クラッシュなし）** ⭐ **完了 2025-09-13**
- [x] **全自動テストがパス + 手動確認完了（100%成功率）** ⭐ **完了 2025-09-13**

### 🎉 Phase 1 System Complete (2025-09-13)
- **Hardware Integration**: M5STACK Basic/Gray with physical buttons ✅
- **Communication**: WiFi → FastAPI REST API ✅  
- **Controls**: A=Play/Pause, B=Stop, C=Next ✅
- **Network**: BSSID-specific router targeting for stable connection ✅
- **Status**: Real-time display sync with backend playback state ✅
- **Validation**: 100% integration test success, 35.5h stability ✅
- **TDD Compliance**: All tests passing, quality assured ✅

### 🎉 **Phase 2 AI Integration Complete!**
VEO API統合と22のAIサービスによる完全自動生成システムが稼働中です。

### 📊 **Phase 2 AI統合システム開発状況** 

**現在の実装状況**: 基盤システム稼働・AI統合開発中

#### **Phase 3達成内容**: 船橋市ベース画像→動画生成パイプライン基本実装完了
- ✅ 船橋市風景画生成（文字なし純粋アート）
- ✅ 動的絵画動画生成（水面揺らぎ、建物明滅）
- ✅ 実用的品質（1080p、安定コーデック）

#### **Phase B達成内容**: AI画像品質向上機能バックエンド完全実装
- ✅ **5つの画像生成パラメータ**: quality, aspect_ratio, negative_prompt, style_preset, seed
- ✅ **TDD厳守実装**: 18/18テスト成功（Red-Green-Refactor完全準拠）
- ✅ **API Mock完全実装**: 外部依存排除・CI/CD対応
- ✅ **包括的ドキュメント**: 技術仕様書・完了報告書・引き継ぎ書

**🔑 次フェーズ課題**: 
- ⏳ フロントエンド統合：React UIでの全パラメータ操作
- ⏳ E2Eテスト：UI→API→画像生成の全工程テスト

```bash
# Phase B フロントエンド接続（次回実施）
# 1. api.ts にAdmin APIクライアント実装
# 2. AIGenerationDashboard.tsx のモック削除・API統合  
# 3. 5つの新パラメータUI実装
```

## 💡 トラブルシューティング

### よくある問題

**仮想環境が見つからない**
```bash
# 仮想環境を再作成
cd /home/aipainting/ai-dynamic-painting
python -m venv .venv
source .venv/bin/activate
pip install serena-agent anthropic
```

**Serenaが起動しない**
```bash
# 依存関係を再インストール
pip install --upgrade serena-agent
serena project generate-yml
```

**パスが見つからない**
```bash
# .bashrcを再読み込み
source ~/.bashrc
```

## 📝 ドキュメント

- [企画書](docs/企画書.md): プロジェクト背景・価値提案
- [詳細設計書](docs/詳細設計書.md): システムアーキテクチャ
- [実装計画書](docs/実装計画書.md): 段階的実装計画
- [CLAUDE.md](docs/CLAUDE.md): Claude用プロジェクト設定
- [PERSONA.md](docs/PERSONA.md): 博士の開発ペルソナ

## 🤝 貢献

このプロジェクトは「AIエージェント主導・段階的実装開発」を採用しています。

1. Issue作成・確認
2. フィーチャーブランチ作成
3. TDDでの開発
4. プルリクエスト
5. ハードウェア実機テスト

## 📄 ライセンス

MIT License

## 👨‍💻 開発者

**博士（はかせ）** - モダンWebアプリケーション開発エキスパート
- 専門: AI・IoT統合システム開発
- 開発哲学: 「技術よりもユーザーの笑顔が一番大切なのだ！」

---

<div align="center">

**「実用的で美しい、家庭で毎日使えるAI動的絵画システムを作るのだ〜！」**

[![Made with ❤️ by 博士](https://img.shields.io/badge/Made%20with%20%E2%9D%A4%EF%B8%8F%20by-%E5%8D%9A%E5%A3%AB-red.svg)](https://github.com/username/ai-dynamic-painting)

</div>