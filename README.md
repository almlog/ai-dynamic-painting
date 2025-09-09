# 🎨 AI Dynamic Painting

> **時間・天気・季節に応じて自動生成される美しい動画を表示する準動的絵画システムなのだ〜！**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4%2F5-red.svg)](https://www.raspberrypi.org/)

## 📋 概要

AI Dynamic Paintingは、VEO APIとエッジAIを活用して、家庭環境の時間帯・天気・季節に応じた美しい動画コンテンツを自動生成・表示する革新的な動的絵画システムなのだ！

### ✨ 主な特徴
- 🌅 **時間帯連動**: 朝・昼・夕・夜に応じた自動コンテンツ切り替え
- 🌦️ **天気応答**: リアルタイム天気情報に基づく動画生成
- 🤖 **AI生成**: Google VEO APIによる高品質8秒動画の自動生成
- 📱 **スマート制御**: M5STACKによる物理操作・センサー統合
- 🌐 **Web管理**: スマホ・PCからの設定・管理インターフェース
- 🧠 **学習機能**: 個人の好みを学習する賢いシステム

## 🏗️ システム構成

```
┌─────────────────┐    WiFi     ┌─────────────────────────────────┐
│   M5STACK       │◄───────────►│      Raspberry Pi               │
│  ・センサー      │             │  ┌─────────────────────────────┐ │
│  ・制御UI       │             │  │     Main Application        │ │
│  ・状態表示     │             │  │  ┌─────────┬─────────────┐ │ │
└─────────────────┘             │  │  │FastAPI  │Display      │ │ │
                                │  │  │Server   │Controller   │ │ │
┌─────────────────┐             │  │  └─────────┴─────────────┘ │ │
│  PC Monitor     │    HDMI     │  │  ┌─────────┬─────────────┐ │ │
│  ・24-32inch    │◄───────────►│  │  │Video    │AI Prompt    │ │ │
│  ・1080p+       │             │  │  │Manager  │Generator    │ │ │
└─────────────────┘             │  │  └─────────┴─────────────┘ │ │
                                │  └─────────────────────────────┘ │
                                └─────────────────────────────────┘
                                               │ HTTPS
                                    ┌─────────▼─────────┐
                                    │   External APIs   │
                                    │  ・Google VEO API │
                                    │  ・Weather API    │
                                    └───────────────────┘
```

## 🔧 技術スタック

### ハードウェア
- **Raspberry Pi 4/5** (8GB RAM推奨)
- **M5STACK Core/Core2** + センサーモジュール
- **PCモニター** (24-32インチ、HDMI接続)

### ソフトウェア
- **バックエンド**: Python 3.11+, FastAPI, SQLite
- **表示制御**: Pygame, OpenCV
- **フロントエンド**: HTML/CSS/JavaScript
- **AI統合**: Google VEO API, Gemini API
- **IoT通信**: WiFi/HTTP, M5STACK (Arduino IDE)

## 🚀 セットアップ

### 前提条件
- Raspberry Pi OS (64-bit)
- Python 3.11以上
- M5STACK開発環境 (Arduino IDE)
- Google AI Pro アカウント

### クイックスタート

```bash
# リポジトリクローン
git clone https://github.com/your-username/ai-dynamic-painting.git
cd ai-dynamic-painting

# 自動セットアップスクリプト実行
chmod +x scripts/setup.sh
./scripts/setup.sh

# 設定ファイル作成
cp .env.example .env
# .envファイルにAPIキーを設定

# 開発サーバー起動
source venv/bin/activate
python main.py
```

### 詳細セットアップ
詳しいセットアップ手順は [docs/setup.md](docs/setup.md) を参照してください。

## 📱 使用方法

### Web UI
ブラウザで `http://raspberry-pi-ip:8080` にアクセスして管理画面を開けるのだ：
- 動画ライブラリの管理
- 自動生成設定
- システム監視・ログ確認

### M5STACK操作
- **Aボタン**: 次の動画に切り替え
- **Bボタン**: お気に入り登録/削除  
- **Cボタン**: 設定メニュー表示

## 🎯 開発計画

### Phase 1: 基盤システム 🚧
- [x] 企画書・設計書作成
- [ ] 基本表示システム
- [ ] Web管理画面
- [ ] M5STACK統合
- [ ] 手動動画管理

### Phase 2: AI統合 🔜
- [ ] VEO API統合
- [ ] 自動プロンプト生成
- [ ] スケジュール生成
- [ ] コンテキスト分析

### Phase 3: 高度機能 🔮
- [ ] 学習機能
- [ ] 運用自動化
- [ ] 拡張機能
- [ ] 長期運用最適化

## 🧪 開発・テスト

### テスト実行
```bash
# 全テスト実行
python -m pytest tests/ -v --cov=core

# 特定テスト実行
python -m pytest tests/test_video_manager.py -v

# 統合テスト
python -m pytest tests/integration/ -v
```

### TDD開発フロー
このプロジェクトではテスト駆動開発を厳守しています：
1. **Red**: 失敗するテストを書く
2. **Green**: テストを通す最小限のコード
3. **Refactor**: コードを美しく改善

### コード品質
```bash
# スタイルチェック
flake8 .

# 型チェック  
mypy .

# セキュリティチェック
bandit -r .
```

## 📁 プロジェクト構造

```
ai-dynamic-painting/
├── README.md
├── requirements.txt
├── .env.example
├── main.py                 # メインアプリケーション
├── docs/                   # ドキュメント
│   ├── 企画書.md
│   ├── 詳細設計書.md
│   ├── 実装計画書.md
│   ├── claude.md
│   └── PERSONA.md
├── core/                   # コアシステム
│   ├── display_controller.py
│   ├── video_manager.py
│   └── config_manager.py
├── api/                    # API統合
│   ├── veo_client.py
│   └── weather_client.py
├── web/                    # Web UI
│   ├── app.py
│   ├── routes/
│   └── static/
├── m5stack/               # M5STACKプログラム
│   └── ai_painting_m5stack.ino
├── database/              # データ管理
│   ├── models.py
│   └── database.py
├── tests/                 # テストスイート
│   ├── test_core.py
│   ├── test_api.py
│   └── integration/
├── scripts/               # セットアップ・ユーティリティ
│   ├── setup.sh
│   └── backup.sh
└── deployment/           # デプロイメント
    ├── systemd/
    └── docker/
```

## 🎨 スクリーンショット・デモ

### システム動作例
![システム概要](docs/images/system_overview.jpg)

### Web管理画面
![Web UI](docs/images/web_ui.png)

### M5STACK表示
![M5STACK](docs/images/m5stack_display.jpg)

## 💰 運用コスト

### 初期費用
- ハードウェア: 既存Raspberry Pi・M5STACK活用
- ディスプレイ: 市場価格（24-32インチPCモニター）

### 月間運用費
- Google AI Pro: ¥3,000（VEO 3 Fast 90動画/月）
- 電気代: ¥500程度（24時間稼働）
- **月額合計**: ¥3,500程度

## 🤝 コントリビューション

このプロジェクトへの貢献を歓迎するのだ！

### 貢献方法
1. **Issue作成**: バグ報告・機能要望
2. **Pull Request**: コード改善・新機能
3. **ドキュメント**: 使い方・セットアップガイド改善
4. **テスト**: テストケースの追加・改善

### 開発ガイドライン
- TDD（テスト駆動開発）を厳守
- PEP 8スタイルガイドに準拠
- 型ヒント必須
- 分かりやすいcommitメッセージ

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

## 🙋‍♀️ サポート・質問

### よくある質問
- [FAQ](docs/FAQ.md) - よくある質問と回答
- [トラブルシューティング](docs/troubleshooting.md) - 問題解決方法

### 連絡先
- **Issues**: [GitHub Issues](https://github.com/your-username/ai-dynamic-painting/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-dynamic-painting/discussions)

## 🌟 謝辞

このプロジェクトは以下の素晴らしい技術・サービスを活用しています：
- [Google VEO API](https://ai.google.dev/) - AI動画生成
- [Raspberry Pi Foundation](https://www.raspberrypi.org/) - シングルボードコンピューター
- [M5STACK](https://m5stack.com/) - IoTデバイス
- [FastAPI](https://fastapi.tiangolo.com/) - モダンWebフレームワーク

## 📈 ロードマップ

- [x] **v0.1.0**: プロジェクト企画・設計完了
- [ ] **v0.2.0**: Phase 1完成（基盤システム）
- [ ] **v0.3.0**: Phase 2完成（AI統合）
- [ ] **v1.0.0**: Phase 3完成（フル機能）
- [ ] **v1.1.0**: 音声認識機能
- [ ] **v1.2.0**: スマートホーム連携
- [ ] **v2.0.0**: マルチディスプレイ対応

---
