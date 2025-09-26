#!/bin/bash
# 🚀 AI動的絵画システム - 開発環境一発起動スクリプト

echo "🌅 AI動的絵画システム開発環境起動中..."

# プロジェクトディレクトリに移動
cd /home/aipainting/ai-dynamic-painting

echo "📂 プロジェクトディレクトリ: $(pwd)"

# Git状況確認
echo "📊 Git状況確認..."
git status --porcelain
echo "📝 最新コミット:"
git log --oneline -3

echo ""
echo "🔧 開発サーバー起動中..."

# バックエンド起動（バックグラウンド）
echo "⚡ Backend起動中 (Port 8000)..."
cd backend
PYTHONPATH=/home/aipainting/ai-dynamic-painting/backend/src \
GEMINI_API_KEY=test-api-key-development \
VEO_PROJECT_ID=test-project-id \
/home/aipainting/ai-dynamic-painting/.venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "🎨 Frontend起動中 (Port 5173)..."
cd ../frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "⏳ サーバー起動待機中..."
sleep 5

echo ""
echo "🧪 サーバー動作確認..."

# Backend確認
if curl -s http://localhost:8000/api/videos > /dev/null; then
    echo "✅ Backend (Port 8000): 正常稼働"
else
    echo "❌ Backend (Port 8000): 起動失敗"
fi

# Frontend確認
if curl -s http://localhost:5173/ > /dev/null; then
    echo "✅ Frontend (Port 5173): 正常稼働"
else
    echo "❌ Frontend (Port 5173): 起動失敗"
fi

echo ""
echo "📋 開発情報"
echo "─────────────────────────────"
echo "🔗 Backend URL:  http://localhost:8000"
echo "🔗 Frontend URL: http://localhost:5173"
echo "🔗 API Docs:     http://localhost:8000/docs"
echo ""
echo "📁 ログファイル:"
echo "   Backend:  logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🔄 PIDファイル:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"

# PID保存
cd ..
mkdir -p logs
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "🎯 現在のタスク状況"
echo "─────────────────────────────"
echo "✅ T6-013: CostTracker実装完了 (12/12テストPASS)"
echo "🔄 T6-014: 予算制限機能実装 (次のタスク)"
echo ""
echo "💡 SuperClaude起動推奨コマンド:"
echo "   SuperClaude --serena --think --task-manage"
echo ""
echo "🚀 開発環境起動完了！ Happy Coding! 🎉"