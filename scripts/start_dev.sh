#!/bin/bash

# AI動的絵画システム 開発環境起動スクリプト
# 作成者: 博士（はかせ）
# 「わくわくする開発の始まりなのだ〜！」

set -e  # エラー時は即座に終了

# カラー出力の設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

# 博士のご挨拶
echo -e "${CYAN}"
cat << 'EOF'
    ____  ____     _____           __
   / __ \/ __ \   |__  /___  ____ / /_____  ______
  / /_/ / / / /    /_ </ __ \/ __ \/ //_/ _ \/ ___/
 / _, _/ /_/ /   ___/ / /_/ / / / / ,< /  __(__  )
/_/ |_/_____/   /____/\____/_/ /_/_/|_|\___/____/

🎨 AI動的絵画システム開発環境 🎨
「すごく楽しい開発が始まるのだ〜！」
EOF
echo -e "${NC}"

# プロジェクト設定
PROJECT_DIR="/home/aipainting/ai-dynamic-painting"
VENV_DIR="$PROJECT_DIR/.venv"
PERSONA_FILE="$PROJECT_DIR/docs/PERSONA.md"
CLAUDE_FILE="$PROJECT_DIR/docs/CLAUDE.md"

log_header "Step 1: ディレクトリ確認なのだ"

# プロジェクトディレクトリの存在確認
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "プロジェクトディレクトリが見つからないのだ: $PROJECT_DIR"
    exit 1
fi

log_success "プロジェクトディレクトリを確認したのだ: $PROJECT_DIR"

# プロジェクトディレクトリに移動
cd "$PROJECT_DIR"
log_info "プロジェクトディレクトリに移動したのだ: $(pwd)"

log_header "Step 2: 仮想環境アクティベートなのだ"

# 仮想環境の存在確認
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    log_error "仮想環境が見つからないのだ: $VENV_DIR"
    exit 1
fi

# 仮想環境をアクティベート
source "$VENV_DIR/bin/activate"
log_success "仮想環境をアクティベートしたのだ！"

# Python環境の確認
PYTHON_VERSION=$(python --version 2>&1)
log_info "Python環境: $PYTHON_VERSION"

log_header "Step 3: 重要ファイル確認なのだ"

# PERSONA.mdの存在確認
if [ ! -f "$PERSONA_FILE" ]; then
    log_warning "PERSONA.mdが見つからないのだ: $PERSONA_FILE"
else
    log_success "PERSONA.mdを確認したのだ"
fi

# CLAUDE.mdの存在確認  
if [ ! -f "$CLAUDE_FILE" ]; then
    log_warning "CLAUDE.mdが見つからないのだ: $CLAUDE_FILE"
else
    log_success "CLAUDE.mdを確認したのだ"
fi

log_header "Step 4: Serena MCP確認なのだ"

# Serenaの動作確認
if ! command -v serena &> /dev/null; then
    log_error "serenaコマンドが見つからないのだ"
    exit 1
fi

SERENA_VERSION=$(serena --help | head -1 || echo "バージョン不明")
log_success "Serena MCPを確認したのだ: $SERENA_VERSION"

log_header "Step 5: 開発環境情報表示なのだ"

echo -e "${CYAN}📊 現在の開発環境情報 📊${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏠 プロジェクトディレクトリ: $PROJECT_DIR"
echo "🐍 Python環境: $PYTHON_VERSION" 
echo "📦 仮想環境: アクティブ"
echo "🤖 Serena MCP: 利用可能"
echo "📋 PERSONA.md: $([ -f "$PERSONA_FILE" ] && echo "✅ 存在" || echo "❌ 不在")"
echo "📋 CLAUDE.md: $([ -f "$CLAUDE_FILE" ] && echo "✅ 存在" || echo "❌ 不在")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_header "Step 6: Serena MCP起動準備なのだ"

# .serenaディレクトリの確認
if [ ! -d "$PROJECT_DIR/.serena" ]; then
    log_warning ".serenaディレクトリが存在しないのだ。作成するのだ..."
    mkdir -p "$PROJECT_DIR/.serena"
fi

# project.ymlの確認
if [ ! -f "$PROJECT_DIR/.serena/project.yml" ]; then
    log_info "project.ymlを生成するのだ..."
    serena project generate-yml
fi

log_success "Serena MCP起動準備完了なのだ！"

echo -e "${GREEN}"
cat << 'EOF'
🎉 開発環境起動完了なのだ〜！ 🎉

次のコマンドでSerena MCPサーバーを起動できるのだ：

    serena start-mcp-server --project /home/aipainting/ai-dynamic-painting

Claude Code統合する場合：
    
    claude --config

博士からのメッセージ：
「準備完了なのだ〜！素晴らしいAI動的絵画システムを作るのだ！」
「失敗を恐れず、楽しく実験していくのだなのだ〜」

EOF
echo -e "${NC}"

# Serena MCPサーバーを自動起動するか確認
echo -e "${YELLOW}Serena MCPサーバーを自動起動しますか？ [y/N]: ${NC}"
read -r -n 1 AUTO_START
echo

if [[ $AUTO_START =~ ^[Yy]$ ]]; then
    log_info "Serena MCPサーバーを起動するのだ..."
    
    # バックグラウンドでSerenaを起動
    echo -e "${CYAN}🚀 Serena MCPサーバー起動中...${NC}"
    serena start-mcp-server --project "$PROJECT_DIR" &
    SERENA_PID=$!
    
    # 少し待って起動確認
    sleep 3
    
    if kill -0 $SERENA_PID 2>/dev/null; then
        log_success "Serena MCPサーバーが起動したのだ！ (PID: $SERENA_PID)"
        echo -e "${GREEN}✨ Claude Codeから接続できるのだ〜！ ✨${NC}"
    else
        log_error "Serena MCPサーバーの起動に失敗したのだ"
    fi
else
    log_info "手動でSerenaを起動してくださいなのだ"
fi

echo -e "${PURPLE}========================================"
echo -e "  🎨 Happy Coding なのだ〜！ 🎨"  
echo -e "========================================${NC}"