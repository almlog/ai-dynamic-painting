# 🎨 AI動的絵画システム

> 「時間・天気・季節に応じて自動生成される美しい動画で、毎日新鮮な視覚体験を提供するシステムなのだ〜！」 - 博士

## 📋 プロジェクト概要

AI動的絵画システムは、VEO APIによる動画自動生成とIoTセンサー連携により、リビング空間の雰囲気を向上させる革新的なシステムです。

### 🎯 核心価値提案
- **動的コンテンツ**: 毎日異なる美しい動画で空間の雰囲気を変化
- **環境応答性**: 時間・天気・季節に自動適応する知的表示
- **個人最適化**: 使用者の好みを学習して満足度向上
- **コスト効率**: 商用製品の1/3程度のコストで高品質体験

## 🏗️ システム構成

```
[M5STACK] ← WiFi → [Raspberry Pi] ← HDMI → [PCモニター]
    ↓                    ↓                      ↓
センサー・制御        メイン処理            動画表示
                        ↓
                  [VEO API]
                  動画生成
```

### ハードウェア
- **Raspberry Pi 4/5**: メインシステム
- **M5STACK**: センサー・制御デバイス  
- **PCモニター**: 24-32インチ表示装置

### ソフトウェア
- **Backend**: Python + FastAPI
- **Frontend**: HTML/CSS/JavaScript
- **Display**: Pygame/OpenCV
- **Database**: SQLite
- **AI**: VEO API, Ollama
- **IoT**: M5STACK (Arduino/C++)

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

### Phase 1: 基盤システム構築 (進行中)
- [x] プロジェクト設計完了
- [x] 開発環境構築
- [x] Serena MCP統合
- [ ] 基本表示システム
- [ ] Web管理画面
- [ ] M5STACK基本操作
- [ ] データベース基盤

### Phase 2: AI統合・自動化 (計画中)
- [ ] VEO API統合
- [ ] プロンプト生成エンジン
- [ ] 生成スケジューラー
- [ ] コンテンツ選択AI

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
- **コスト意識**: VEO API使用量・電気代等の運用コスト常時監視

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

### Phase 1 完成基準
- [ ] 手動動画アップロード・表示が Raspberry Pi + モニターで動作
- [ ] Web UI で動画管理が PC・スマホから操作可能
- [ ] M5STACK でボタン操作・センサー読み取りが正常動作
- [ ] 24時間連続稼働で安定動作（メモリリーク・クラッシュなし）
- [ ] 全自動テストがパス + 手動確認完了

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