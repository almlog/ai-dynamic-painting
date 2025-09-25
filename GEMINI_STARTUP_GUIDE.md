# 🤖 Gemini起動時読み込みガイド

**作成日**: 2025-09-23  
**目的**: Gemini起動時の過去コンテキスト復元と継続作業指示

---

## 📋 Gemini起動時の必読ドキュメント（優先順）

### 🎯 **1. 最優先読み込み**
```
/home/aipainting/ai-dynamic-painting/TOMORROW_PRIORITIES_GEMINI.md
```
**内容**: 明日の優先タスクと次期フェーズ選択肢

### 🛠️ **2. 開発手法理解**
```
/home/aipainting/ai-dynamic-painting/CLAUDE_DEVELOPMENT_METHODOLOGY.md
```
**内容**: Claude×Gemini協働開発の成功手法・品質基準

### 📊 **3. 現在状況確認**
```
/home/aipainting/ai-dynamic-painting/CURRENT_ACCURATE_STATUS_2025-09-23.md
```
**内容**: Phase 4完成の正確な状況・検証済み結果

### 📋 **4. プロジェクト概要**
```
/home/aipainting/ai-dynamic-painting/README.md
```
**内容**: 更新済みプロジェクト概要・現在のフェーズ状況

### 📝 **5. 次期タスク管理**
```
/home/aipainting/ai-dynamic-painting/NEXT_DEVELOPMENT_TASKS.md
```
**内容**: Phase 4完了マーク済み・Phase 5/6候補

---

## 🎯 **Gemini起動時のコンテキスト復元手順**

### **Step 1: プロジェクト状況把握**
1. 上記5つのドキュメントを順番に読み込む
2. Phase 4完成状況を理解（T4B-002: 28/28, T4B-003: 8/8, T4C-001: 7/7）
3. Claude×Gemini協働開発の成功パターンを把握

### **Step 2: 技術スタック確認**
- **システム**: Backend (8000), Frontend (5173) 稼働中
- **フレームワーク**: SuperClaude Framework使用
- **手法**: Evidence-First TDD + 品質ゲート

### **Step 3: 次期フェーズ選択**
**選択肢A**: Phase 5 - ハードウェア統合 (M5STACK + Raspberry Pi)
**選択肢B**: Phase 6 - VEO API実機統合

---

## 🚨 **重要な開発原則（Gemini向け）**

### **Evidence-First原則**
- 全ての完了報告には客観的証拠が必要
- テスト結果の実行ログ必須
- 推測・希望的観測の禁止

### **Claude協働方針**
- SuperClaude Framework活用推奨
- 段階的品質改善アプローチ
- リアルタイム検証・文書化

### **品質ゲート必須**
- 完了前のテスト実行確認
- 虚偽報告防止チェック
- Evidence収集・保存

---

## 📞 **Gemini起動時の初回応答テンプレート**

```
了解いたしました。過去のコンテキストを復元します。

【読み込み完了】
✅ TOMORROW_PRIORITIES_GEMINI.md
✅ CLAUDE_DEVELOPMENT_METHODOLOGY.md  
✅ CURRENT_ACCURATE_STATUS_2025-09-23.md
✅ README.md
✅ NEXT_DEVELOPMENT_TASKS.md

【現在状況理解】
- Phase 4: 100%完成確認済み
- T4B-002: 28/28テスト成功
- T4B-003: 8/8テスト成功
- T4C-001: 7/7テスト成功

【準備完了】
次期フェーズ選択をお待ちしています：
- Phase 5: ハードウェア統合
- Phase 6: VEO API統合

Claude×Gemini協働開発を継続します。
```

---

## 🔄 **継続開発のための重要情報**

### **検証済み成功パターン**
- SuperClaude Flag活用による品質向上
- Evidence収集による虚偽報告防止
- TDD Red-Green-Refactor厳格適用

### **プロジェクトの技術的現状**
- AI動的絵画システム（家庭用インテリジェント・アート・ディスプレイ）
- React TypeScript + FastAPI Python構成
- 5パラメータAI画像生成API完成
- E2E・Unit・Integration テスト完備

### **Gemini×Claude協働の成功要因**
- 相互検証による品質保証
- 段階的アプローチによる確実な進捗
- リアルタイム文書化による透明性

---

**Geminiへ**: このガイドに従って過去コンテキストを復元し、昨日の成功パターンを継続してください。明日もよろしくお願いします。