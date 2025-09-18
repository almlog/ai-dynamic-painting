# 🎨 AI動的絵画システム

> 「AI自動生成の美しい動画をM5STACKで簡単操作できる、インテリジェントな家庭用動的絵画システムなのだ〜！」 - 博士  
> **🎉 Phase 2 AI統合システム 100%完成！ (2025-09-18)**

## 📋 プロジェクト概要

AI動的絵画システムは、**完全AI統合**により自動動画生成・学習機能を搭載した次世代リビング空間システムです。Phase 1の手動基盤から**Phase 2のフル AI統合**へと進化し、完全な自動化とインテリジェント機能を実現しています。

### 🎯 核心価値提案（Phase 1完了）
- **簡単操作**: M5STACKの物理ボタンで直感的な動画制御
- **手軽管理**: Web UIで動画のアップロード・管理が簡単
- **安定表示**: Raspberry Piで24時間安定した動画再生
- **コスト効率**: 市販品の1/3コストで高品質な表示環境

### 🚀 AI統合価値（**Phase 2完全完成100%** ✅ 2025-09-18）
- **🤖 自動AI生成**: VEO API統合で高品質動画自動生成 ✅
- **🧠 インテリジェント学習**: ユーザー嗜好・環境適応学習 ✅
- **⚡ スマート最適化**: コスト・時間・品質の最適バランス ✅
- **📊 リアルタイム監視**: 24時間安定稼働・コスト管理 ✅
- **🔄 自動フォールバック**: API障害時の自動代替処理 ✅
- **🎯 コンテキスト生成**: 天気・時間・季節連動コンテンツ ✅
- **📈 分析ダッシュボード**: 使用状況・パフォーマンス可視化 ✅
- **🎨 プロンプト最適化**: 動的品質向上エンジン ✅
- **💰 コスト管理**: 予算監視・アラート・最適化 ✅
- **📱 フル統合UI**: 5つのAIコンポーネント完備 ✅
- **🏗️ 拡張可能設計**: 将来機能追加対応アーキテクチャ ✅

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

### ソフトウェア（**Phase 2完全統合版**）
- **Backend**: Python + FastAPI + **18のAI REST API** ✅
- **Frontend**: React + TypeScript + **5つのAIコンポーネント** ✅
- **AI Models**: **8つのAIデータモデル** + SQLite拡張 ✅
- **AI Services**: **22のAIサービス** (VEO, Learning, Monitoring等) ✅
- **Testing**: **245個のテストケース** (TDD完全実践) ✅
- **Hardware**: M5STACK AI統合 (フィードバック・監視) ✅
- **Database**: SQLite + AI拡張スキーマ ✅
- **Architecture**: 完全拡張可能設計 ✅

## 🚀 クイックスタート

### 🎉 一発起動コマンド

```bash
ai-dev
```

このコマンド一つで以下が自動実行されます：
- プロジェクトディレクトリに移動
- 仮想環境をアクティベート
- 重要ファイル（PERSONA.md、CLAUDE.md）を確認
- Serena MCPの動作確認
- 開発環境情報を表示
- Serena MCPサーバーの起動オプション

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

## 🔄 開発フェーズ

### Phase 1: 基盤システム構築 ✅ **100%完了 - 2025-09-13** 🎉
- [x] プロジェクト設計完了
- [x] 開発環境構築
- [x] Serena MCP統合
- [x] FastAPI Backend基盤
- [x] React Frontend基盤
- [x] **M5STACK Hardware Integration** ⭐ **2025-09-13完成**
- [x] **物理ボタン制御（A: Play/Pause, B: Stop, C: Next）**
- [x] **WiFi通信・API連携確立**
- [x] SQLiteデータベース基盤
- [x] **最終検証・統合テスト100%成功** ⭐ **2025-09-13完成**

### Phase 2: AI統合・自動化 🎉 **100%完了 - 2025-09-18** ⭐
- [x] **Phase 2仕様書作成** ⭐ **2025-09-14完成**
- [x] **Phase 2実装計画作成** ⭐ **2025-09-14完成**  
- [x] **Phase 2タスク生成（63タスク）** ⭐ **2025-09-14完成**
- [x] **VEO API統合** ⭐ **2025-09-18完成** - Google VEO-2 完全統合
- [x] **プロンプト生成エンジン** ⭐ **2025-09-18完成** - 時間・天気連動プロンプト
- [x] **生成スケジューラー** ⭐ **2025-09-18完成** - 自動・手動・条件付きスケジュール
- [x] **AI品質管理システム** ⭐ **2025-09-18完成** - 動画品質自動評価
- [x] **監視・アラートシステム** ⭐ **2025-09-18完成** - リアルタイム監視
- [x] **完全REST API（18エンドポイント）** ⭐ **2025-09-18完成**
- [x] **高度AI機能** ⭐ **2025-09-18完成** - 学習・最適化・分析
- [x] **AIフロントエンド統合** ⭐ **2025-09-18完成** - 5つのAIコンポーネント

### Phase 3: 高度機能・運用最適化 (計画中)
- [ ] 個人化学習
- [ ] 運用自動化
- [ ] 拡張機能
- [ ] パフォーマンス最適化

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

### 博士の開発スタイル
- **段階的改善**: 完璧な初期実装より動作するものから段階拡張
- **実験的アプローチ**: 失敗を恐れず迅速な試行錯誤と改善
- **ユーザビリティ優先**: 技術的完璧性より日常使用の便利さ
- **TDD必須**: Red → Green → Refactor サイクルの厳守

### 重要な原則
- **ハードウェア実機確認**: 全てのハードウェアで実際の動作確認必須
- **段階的実装**: 各フェーズ完成まで次に移行しない
- **障害許容設計**: 一部機能停止でもシステム全体は継続動作
- **コスト意識**: 将来のVEO API使用量・電気代等の運用コスト計画

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

### 🚀 **Ready for Phase 2: AI Integration**
Phase 1基盤システム完成により、VEO API統合とAI自動動画生成の準備が整いました。

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