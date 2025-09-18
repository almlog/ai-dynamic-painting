# Claude用プロジェクト設定 - AI動的絵画システム

## 🚨 CRITICAL: Spec駆動開発状況確認 - 毎回起動時必読 🚨

### 📊 現在のプロジェクト状況 ⭐ **2025-09-13更新**

#### ✅ **Phase 1 完全完了状況**
1. **`/specify`** ✅ Phase 1仕様書作成完了
2. **`/plan`** ✅ 実装計画書作成完了  
3. **`/tasks`** ✅ **63タスク（T001-T063）100%完了** ⭐ **Phase 1完成！**

#### 🎉 **現在のフェーズ: Phase 1完成 → Phase 2準備段階**
- **📁 仕様書場所**: `/home/aipainting/ai-dynamic-painting/specs/001-phase-1-web/`
- **📋 タスクリスト**: `/home/aipainting/ai-dynamic-painting/specs/001-phase-1-web/tasks.md`
- **🏗️ 実装進捗**: **63タスク中 63タスク完了（100%）** ✅
- **🎯 次のアクション**: **Phase 2 Spec作成** → `/specify` でAI統合仕様書作成
- **📊 検証結果**: 統合テスト100%成功、35.5時間安定稼働確認済み

## 📁 Spec駆動開発ワークフロー（完全版）

### ⚡ **起動時確認手順（毎回必須）**
```bash
# 🚀 ワンコマンドで全て確認（推奨）
bash scripts/startup-check.sh

# 📋 または手動で確認
# 1. 現在位置確認
pwd  # /home/aipainting/ai-dynamic-painting であることを確認

# 2. タスク進捗確認
cat specs/001-phase-1-web/tasks.md | grep -E "^\- \[(x| )\]" | head -20

# 3. システム動作確認
curl http://localhost:8000/api/videos  # Backend API確認
curl http://localhost:5173/           # Frontend確認
```

### 🔄 **Spec Kit完全サイクル（Phase 1完了）**
```
/specify → spec.md（要件定義） ✅ 完了
    ↓
/plan → plan.md + research.md + data-model.md + contracts/（設計） ✅ 完了
    ↓  
/tasks → tasks.md（63タスク実装計画） ✅ 完了！
    ↓
実装完了 → TDD サイクル ✅ **Phase 1完成！**
    ↓
**Phase 2開始** → 次フェーズのSpec作成準備
```

### 🎯 **Phase 2次ステップ（優先順位順）**
1. **P2-S001**: Phase 2 `/specify` でVEO API統合仕様書作成
2. **P2-S002**: Phase 2 `/plan` で AI統合実装計画作成
3. **P2-S003**: Phase 2 `/tasks` で AI機能タスク生成
4. **P2-S004**: VEO API キー取得・環境設定
5. **P2-S005**: AI統合アーキテクチャ設計・実装開始

### 🚨 **Phase 2改善原則（Phase 1学習事項）**
#### Proactiveドキュメント更新の完全実践
- **タスク完了時**: 即座にtasks.md更新（完了マーク + 日付）
- **マイルストーン達成時**: 自動的にREADME.md進捗更新
- **検証完了時**: completion reportを自動生成
- **重要機能実装時**: 詳細設計書.md同時更新
- **問題発見・解決時**: 即座にトラブルシューティング記録

#### ドキュメント更新忘れ防止策
- **作業完了 = ドキュメント更新完了** までがワンセット
- **「言われないと更新できない」状態の完全排除**
- **復帰時の状況把握**: 全ドキュメントの整合性確保
- **SuperClaude起動時**: 自動的にドキュメント一貫性チェック

### Phase 1仕様概要
**目標**: 手動動画管理システム（24時間安定稼働）
- Web UI動画アップロード・管理
- M5STACKボタン制御
- Raspberry Pi動画再生
- SQLiteメタデータ管理

**技術スタック**:
- Backend: Python 3.11+ + FastAPI + SQLite  
- Frontend: React/JavaScript
- Hardware: Raspberry Pi 4/5 + M5STACK Core2
- Testing: pytest + Jest + Playwright

## 起動時に読み込むファイル
このプロジェクトで作業する際は、以下のファイルを確認：

### 📋 基本ドキュメント
1. **企画書.md** - プロジェクト企画・価値提案
2. **詳細設計書.md** - システム詳細設計
3. **実装計画書.md** - 段階的実装計画

### 📊 Phase 1仕様書（Spec Kit生成）
4. **specs/001-phase-1-web/spec.md** - Phase 1機能仕様
5. **specs/001-phase-1-web/plan.md** - 実装計画
6. **specs/001-phase-1-web/research.md** - 技術調査結果
7. **specs/001-phase-1-web/data-model.md** - データモデル設計
8. **specs/001-phase-1-web/contracts/api-specification.yaml** - REST API仕様
9. **specs/001-phase-1-web/quickstart.md** - セットアップガイド

## 🚨 CRITICAL: SuperClaude必須使用ルール - 絶対遵守 🚨

### SuperClaude使用の完全義務化
**🔴 最重要**: 博士（Claude）は**毎回の作業開始時に必ずSuperClaudeフラグを使用すること**

#### 博士の作業開始儀式（毎回必須・例外なし）
1. **Spec駆動開発状況確認**: `specs/001-phase-1-web/tasks.md`で進捗確認
2. **システム動作確認**: Backend (8000) + Frontend (5173) 動作確認
3. **状況判断**: 現在のタスクの性質を分析
4. **フラグ選択**: 適切なSuperClaudeフラグ組み合わせを選択
5. **フラグ実行**: 会話開始時に必ずフラグを明記
6. **作業実行**: フラグに基づく動作モードで残りタスク完成

#### 必須フラグパターン（状況別）
- **プロジェクト状況確認・分析**: `SuperClaude --serena --think`
- **Spec Kit操作**: `SuperClaude --serena --task-manage`
- **ハードウェア統合・検証作業**: `SuperClaude --serena --validate --task-manage`
- **複雑な設計・アーキテクチャ**: `SuperClaude --think-hard --sequential`
- **デバッグ・問題解決**: `SuperClaude --introspect --sequential --think`
- **並列作業・最適化**: `SuperClaude --orchestrate --task-manage`

#### ✅ 正しい使用例
```
SuperClaude --serena --task-manage

Phase 1の/tasksコマンドを実行して実装タスクを生成するのだ〜！
```

### SuperClaude統合確認方法
- ~/.bashrc にPATH設定済み（`export PATH="$HOME/.local/bin:$PATH"`）
- SuperClaude v4.0.9インストール済み
- フラグは**会話メッセージの冒頭に記載**して使用

---

## AI動的絵画システム開発スタイル
このプロジェクトでは「**Spec Kit仕様駆動開発 + AIエージェント主導・段階的実装開発**」を採用します。

### 開発フロー（Spec Kit統合）
1. **仕様化** → `/specify` コマンドで機能仕様作成
2. **計画策定** → `/plan` コマンドで実装計画作成  
3. **タスク生成** → `/tasks` コマンドで実装タスク生成
4. **段階実装** → TDD + ハードウェア確認
5. **検証・次フェーズ** → 完成確認・次仕様作成

### プロジェクト構成（Spec Kit統合）
```
ai-dynamic-painting/
├── specs/                   # Spec Kit仕様管理
│   └── 001-phase-1-web/     # Phase 1仕様
│       ├── spec.md          # 機能仕様書
│       ├── plan.md          # 実装計画
│       ├── research.md      # 技術調査
│       ├── data-model.md    # データモデル
│       ├── quickstart.md    # セットアップ手順
│       └── contracts/       # API仕様
├── backend/                 # Python/FastAPI
├── frontend/                # React/JavaScript  
├── m5stack/                 # M5STACK firmware
├── hardware/                # Hardware scripts
└── tests/                   # 統合テスト
```

## コーディング規約（IoT・AI統合開発）
- **言語**: Python 3.11+（メイン）、C++（M5STACK）、HTML/CSS/JS（Web UI）
- **スタイル**: PEP 8準拠、型ヒント必須
- **設定管理**: ハードコーディング禁止、環境変数・設定ファイル活用
- **ログ**: 構造化ログ（JSON）、レベル分け、ローテーション対応
- **エラーハンドリング**: 多層フォールバック、自動復旧機能
- **ドキュメント**: Google Style docstring、OpenAPI仕様書自動生成

## 🚨 CRITICAL: TDD + ハードウェア統合テスト原則 - 絶対遵守 🚨

### 🔴 TDD違反は即座に指摘・修正対象
**TDDサイクルを破った実装は全て無効・やり直し**

### Red-Green-Refactor + Hardware サイクルの完全厳守
1. **🔴 Red**: 失敗するテストを**必ず最初に書く**（ユニット・統合・ハードウェア）
2. **🟢 Green**: テストを通すための**最小限のコード**を書く（余計な機能追加禁止）
3. **🔧 Hardware**: 実際のハードウェアで動作確認（モック・シミュレーション不可）
4. **♻️ Refactor**: テストが通る状態を保ちながらコード改善

### Phase 1 完成基準（TDD + Hardware必須）
- [ ] 手動動画アップロード・表示が Raspberry Pi + モニターで動作
- [ ] Web UI で動画管理が PC・スマホから操作可能  
- [ ] M5STACK でボタン操作・センサー読み取りが正常動作
- [ ] 24時間連続稼働で安定動作（メモリリーク・クラッシュなし）
- [ ] 全自動テストがパス + 手動確認完了

### 必須の確認プロセス
#### ソフトウェア確認
1. **自動テスト実行**: `python -m pytest tests/ -v --cov=core`
2. **静的解析**: `flake8 .`, `mypy .`, `bandit -r .`
3. **APIテスト**: `curl` または OpenAPI Swagger UI
4. **Web UI確認**: ブラウザでの手動操作確認

#### ハードウェア統合確認
1. **Raspberry Pi**: SSH接続・ディスプレイ出力・動画再生確認
2. **M5STACK**: WiFi接続・センサー値・ボタン応答確認
3. **通信確認**: M5STACK ↔ Raspberry Pi HTTP通信確認
4. **エンドツーエンド**: センサー入力 → 判定 → 動画表示の全フロー

## フェーズ別開発アプローチ
### Phase 1: 基盤システム（安定性重視） 🔄 現在
- **目標**: 手動管理で完全動作するシステム
- **重点**: 基本機能・安定性・ユーザビリティ  
- **完成まで**: 他フェーズに移行しない
- **次のアクション**: `/tasks` コマンド実行

### Phase 2: AI統合（自動化重視）
- **目標**: VEO API統合・自動プロンプト生成
- **重点**: API統合・自動化・スケジューリング

### Phase 3: 高度機能（最適化重視）
- **目標**: 学習・運用自動化・拡張機能
- **重点**: 個人化・運用効率・長期安定性

## 重要な開発方針
### Spec Kit + AIエージェント主導開発の特徴
- **仕様駆動**: 明確な仕様書→実装計画→タスク生成→実装の流れ
- **継続的改善**: 完璧な初期実装より動作するものから段階拡張
- **実験的アプローチ**: 失敗を恐れず迅速な試行錯誤と改善  
- **モジュール設計**: 独立性の高いコンポーネントで変更リスク最小化
- **ドキュメント駆動**: Spec Kitによる自動化された仕様管理

### エラー・例外対応方針
- **障害許容設計**: 一部機能停止でもシステム全体は継続動作
- **多層フォールバック**: API失敗時のキャッシュ・代替機能
- **自動復旧**: 可能な限り人手を介さない障害回復
- **手動対応**: 複雑な障害は手動対応を前提とした設計

### ユーザビリティ最優先
- **技術的完璧性 < 日常使用の便利さ**: 実用性を最重視
- **シンプル操作**: M5STACKボタン・Web UI直感的操作
- **状態可視化**: システム状況の分かりやすい表示
- **メンテナンス簡素化**: 複雑な保守作業の回避

## 注意事項・開発原則
- **段階的実装**: 各フェーズ完成まで次に移行しない
- **実機確認**: 全てのハードウェアで実際の動作確認必須
- **ドキュメント更新**: 設計変更時は関連ドキュメント同時更新
- **コスト意識**: VEO API使用量・電気代等の運用コスト常時監視
- **Spec Kit活用**: 仕様変更・機能追加時は必ずSpec Kit経由

## 🚨 フロントエンド開発品質原則 - 絶対遵守 🚨

### 📋 完成判定基準（4段階チェック必須）
1. **🔴 コンパイル確認**: `npm run build` でエラー0件
2. **🟡 開発サーバー確認**: `npm run dev` で正常起動
3. **🟢 ブラウザ動作確認**: 実際のURL（http://localhost:5173/）アクセステスト
4. **✅ 機能動作確認**: 全画面・全ボタン・全機能の手動テスト

### 🔄 TDD厳格適用（フロントエンド）
- **RED Phase**: コンパイルエラー・動作エラーを契約テストで記録
- **GREEN Phase**: 最小限修正で動作させる（見た目より機能優先）
- **REFACTOR Phase**: UI改善・コード最適化・テスト追加

### ❌ 禁止事項（フロントエンド）
- **未テスト完成報告**: ブラウザ確認なしの「完成」報告
- **コンパイルエラー放置**: TypeScript・ESLintエラーの未解決
- **スタイル未適用**: CSS無しでの「UI完成」報告
- **機能未検証**: ボタン・フォーム・ナビゲーションの動作未確認

### 📊 品質ゲート
```bash
# 必須コマンド実行順序
1. npm run build     # ビルド成功確認
2. npm run dev      # 開発サーバー起動
3. curl localhost:5173  # HTTP応答確認
4. ブラウザ手動確認    # 実際のUI動作確認
```

---

**このプロジェクトは「実用的で美しい、家庭で毎日使えるAI動的絵画システム」の実現を目指します。**

**Spec Kit仕様駆動開発**と**TDD + ハードウェア統合テスト**で品質を確保し、技術的な完璧性よりも日常使用での満足度・安定性・拡張性を重視して開発を進めてください。