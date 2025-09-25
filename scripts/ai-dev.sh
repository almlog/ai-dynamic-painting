#!/bin/bash

# AI動的絵画システム 統合開発環境起動スクリプト
# 作成者: Gemini (博士の設計思想を継承)
# 「これ一つで、全ての準備が整うのだ〜！」

set -e  # エラー時は即座に終了

# カラー出力の設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}
log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}
log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}
log_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE} $1 ${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

log_header "AI動的絵画システム 統合起動シーケンス開始"

# --- Step 1: 環境準備 ---
log_info "Step 1: 開発環境の準備なのだ"

PROJECT_DIR="/home/aipainting/ai-dynamic-painting"
VENV_DIR="$PROJECT_DIR/.venv"

# プロジェクトディレクトリに移動
cd "$PROJECT_DIR" || { log_error "プロジェクトディレクトリが見つからないのだ"; exit 1; }
log_success "作業ディレクトリ: $(pwd)"

# 仮想環境をアクティベート
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    log_success "仮想環境をアクティベートしたのだ！"
else
    log_error "仮想環境が見つからないのだ: $VENV_DIR"
    exit 1
fi

# --- Step 2: サーバープロセス起動 ---
log_header "Step 2: サーバープロセスの起動なのだ"

log_info "既存のサーバープロセスを停止します..."
pkill -f "uvicorn src.main:app" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
log_success "既存プロセスのクリーンアップ完了！"

log_info "環境変数を設定します..."
export PYTHONPATH="$PROJECT_DIR/backend/src"
export GEMINI_API_KEY=${GEMINI_API_KEY:-"test-api-key-development"}
export VEO_PROJECT_ID=${VEO_PROJECT_ID:-"test-project-id"}
log_success "環境変数を設定しました。"

log_info "バックエンドサーバーを起動します... (http://localhost:8000)"
(cd "$PROJECT_DIR/backend" && "$VENV_DIR/bin/uvicorn" src.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/backend_startup.log" 2>&1) &
BACKEND_PID=$!

log_info "フロントエンドサーバーを起動します... (http://localhost:5173)"
cd "$PROJECT_DIR/frontend" && npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_DIR" # ディレクトリを戻す

log_info "サーバーの起動を待っています... (約10秒)"
sleep 10

# --- Step 3: 起動確認 ---
log_header "Step 3: 起動ヘルスチェックなのだ"
if curl -s --head http://localhost:8000 | head -n 1 | grep -q "200 OK\|405 Method Not Allowed"; then
    log_success "バックエンド API: 正常に起動しました (PID: $BACKEND_PID)"
else
    log_error "バックエンド API: 起動に失敗しました"
fi

if curl -s --head http://localhost:5173 | head -n 1 | grep -q "200 OK"; then
    log_success "フロントエンド: 正常に起動しました (PID: $FRONTEND_PID)"
else
    log_error "フロントエンド: 起動に失敗しました"
fi

log_header "🎉 全ての準備が完了したのだ〜！ 🎉"
echo -e "${GREEN}Backend: http://localhost:8000/docs"
echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
echo ""
