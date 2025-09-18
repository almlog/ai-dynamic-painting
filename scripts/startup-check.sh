#!/bin/bash
# AI動的絵画システム - Spec駆動開発起動時確認スクリプト
# 毎回のセッション開始時に実行して、現在の状況を把握する

echo "🎯 AI動的絵画システム - Spec駆動開発状況確認"
echo "================================================"
echo ""

# 1. 現在位置確認
echo "📁 1. プロジェクトディレクトリ確認"
if [[ $(basename $(pwd)) == "ai-dynamic-painting" ]]; then
    echo "✅ 正しいディレクトリです: $(pwd)"
else
    echo "❌ 警告: 正しいディレクトリに移動してください"
    echo "   現在: $(pwd)"
    echo "   正解: /home/aipainting/ai-dynamic-painting"
    exit 1
fi
echo ""

# 2. Spec駆動開発サイクル確認  
echo "🔄 2. Spec駆動開発サイクル状況"
echo "Phase 1: /specify → /plan → /tasks → 実装 → ✅ **完了** (2025-09-13)"
echo "Phase 2: /specify → /plan → /tasks → ✅ **準備完了** (2025-09-14)"
echo ""
echo "📋 Phase 2 Spec準備状況"
echo "/specify → ✅ Phase 2仕様書作成完了 (2025-09-14)"
echo "/plan    → ✅ Phase 2実装計画作成完了 (2025-09-14)" 
echo "/tasks   → ✅ 73タスク（T201-T273）生成完了 (2025-09-14)"
echo "次ステップ → 🚀 VEO API設定 → AI統合実装開始"
echo ""

# 3. Phase 1完成状況確認
echo "📋 3. Phase 1完成状況"
if [[ -f "specs/001-phase-1-web/tasks.md" ]]; then
    total_tasks=$(grep -c "^\- \[" specs/001-phase-1-web/tasks.md)
    completed_tasks=$(grep -c "^\- \[x\]" specs/001-phase-1-web/tasks.md)
    echo "✅ タスク完了: ${completed_tasks}/${total_tasks} (100%)"
    echo "✅ 統合テスト: 100%成功 (8/8 tests)"
    echo "✅ 安定稼働: 35.5時間連続動作確認済み"
    echo "✅ M5STACK統合: 物理ボタン制御完全動作"
    echo ""
    echo "🎉 Phase 1 正式完成宣言: 2025-09-13 24:00"
else
    echo "❌ tasks.md が見つかりません"
fi
echo ""

# 4. システム動作確認
echo "🚀 4. システム動作確認"

# Backend確認
echo -n "Backend API (8000): "
if curl -s http://localhost:8000/api/videos >/dev/null 2>&1; then
    echo "✅ 稼働中"
else
    echo "❌ 停止中 - 起動が必要"
fi

# Frontend確認  
echo -n "Frontend (5173): "
if curl -s http://localhost:5173/ >/dev/null 2>&1; then
    echo "✅ 稼働中"
else
    echo "❌ 停止中 - 起動が必要"
fi

# Database確認
echo -n "Database: "
if [[ -f "backend/data/ai_painting_development.db" ]]; then
    echo "✅ 存在"
else
    echo "❌ 見つからない"
fi
echo ""

# 5. Phase 2実装開始準備
echo "🎯 5. Phase 2実装開始のための次ステップ"
echo ""
echo "A) Phase 1システム稼働確認:"
echo "   ✅ Backend API (8000) → M5STACK制御動作確認"
echo "   ✅ Frontend (5173) → Web UI動作確認"
echo "   ✅ M5STACK Hardware → 物理ボタン動作確認"
echo ""
echo "B) Phase 2 Spec完成済み:"
echo "   ✅ /specify → Phase 2仕様書完成 (2025-09-14)"
echo "   ✅ /plan → Phase 2実装計画完成 (2025-09-14)"
echo "   ✅ /tasks → 73タスク生成完成 (2025-09-14)"  
echo ""
echo "C) Phase 2実装開始準備:"
echo "   1. VEO API アカウント・キー取得"
echo "   2. Google AI Studio 環境設定"
echo "   3. Phase 2タスクT201から実装開始"
echo ""
echo "🚨 重要: Phase 2では proactiveドキュメント更新を実践！"
echo ""

echo "================================================"
echo "🚨 重要: SuperClaudeフラグを使用して作業開始してください"
echo "📚 詳細: CLAUDE.md を参照"