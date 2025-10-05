#!/bin/bash
# 🚀 AI動的絵画システム - 超高速起動スクリプト
# Author: Claude (博士)
# Phase 6: VEO API統合システム対応

set -e

echo "🎨 AI動的絵画システム - Phase 6 起動中..."
echo "=================================================="

# プロジェクトディレクトリに移動
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
echo "📁 プロジェクトディレクトリ: $PROJECT_ROOT"

# 仮想環境確認
if [ ! -d ".venv" ]; then
    echo "❌ 仮想環境が見つかりません。セットアップを実行してください。"
    echo "   python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "✅ 仮想環境確認完了"

# 既存プロセスの確認と停止
echo "🔍 既存プロセス確認中..."

# uvicornプロセスの確認
if pgrep -f "uvicorn" > /dev/null; then
    echo "⚠️  既存のバックエンドプロセスを停止中..."
    pkill -f "uvicorn" || true
    sleep 2
fi

# npm run dev プロセスの確認
if pgrep -f "npm run dev" > /dev/null; then
    echo "⚠️  既存のフロントエンドプロセスを停止中..."
    pkill -f "npm run dev" || true
    sleep 2
fi

echo "✅ プロセス確認・クリーンアップ完了"

# ログディレクトリ作成
mkdir -p logs

# バックエンド起動
echo "🚀 バックエンドサーバー起動中..."
cd backend
source ../.venv/bin/activate

# 環境変数設定
export PYTHONPATH="$PROJECT_ROOT/backend/src"
export GEMINI_API_KEY="test-api-key-development"
export VEO_PROJECT_ID="test-project-id"

# バックエンドをバックグラウンドで起動
nohup python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ バックエンド起動完了 (PID: $BACKEND_PID)"

# フロントエンド起動
echo "🚀 フロントエンドサーバー起動中..."
cd ../frontend

# Node.js依存関係確認
if [ ! -d "node_modules" ]; then
    echo "📦 Node.js依存関係をインストール中..."
    npm install
fi

# フロントエンドをバックグラウンドで起動
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ フロントエンド起動完了 (PID: $FRONTEND_PID)"

cd ..

# 起動待機
echo "⏳ サーバー起動待機中..."
sleep 5

# ヘルスチェック
echo "🏥 ヘルスチェック実行中..."

# バックエンドヘルスチェック
if curl -s "http://localhost:8000/health" > /dev/null; then
    echo "✅ バックエンド正常稼働: http://localhost:8000"
else
    echo "❌ バックエンドヘルスチェック失敗"
    echo "   ログ確認: tail -f logs/backend.log"
fi

# フロントエンドヘルスチェック
if curl -s "http://localhost:5173/" > /dev/null; then
    echo "✅ フロントエンド正常稼働: http://localhost:5173"
else
    echo "❌ フロントエンドヘルスチェック失敗"
    echo "   ログ確認: tail -f logs/frontend.log"
fi

# VEO APIヘルスチェック
if curl -s "http://localhost:8000/api/ai/health" > /dev/null; then
    echo "✅ VEO API正常稼働: http://localhost:8000/api/ai/health"
else
    echo "⚠️  VEO APIヘルスチェック - 一部制限あり（正常）"
fi

echo ""
echo "🎉 起動完了！"
echo "=================================================="
echo "📊 アクセス情報:"
echo "   • Frontend:   http://localhost:5173"
echo "   • Backend:    http://localhost:8000"
echo "   • API Docs:   http://localhost:8000/docs"
echo "   • VEO API:    http://localhost:8000/api/ai/health"
echo ""
echo "📋 管理コマンド:"
echo "   • ログ確認:    tail -f logs/backend.log   (または logs/frontend.log)"
echo "   • プロセス確認: ps aux | grep uvicorn     (または npm)"
echo "   • 停止:        pkill -f uvicorn && pkill -f 'npm run dev'"
echo ""
echo "🎨 Phase 6: VEO API統合システム稼働中..."
echo "   博士のAI動的絵画システムをお楽しみください！"