#!/bin/bash

# API キー設定スクリプト - AI動的絵画システム
# Phase 3: API統合実動作確認用

set -e

# カラー出力の設定
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
PURPLE='\\033[0;35m'
CYAN='\\033[0;36m'
NC='\\033[0m'

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
🔑 API Key Setup Script 🔑
「Phase 3でついに実動作確認なのだ〜！」

Phase 1 ✅ 基盤システム完成
Phase 2 ✅ AI統合システム完成  
Phase 3 🔄 実API統合・動作確認
EOF
echo -e "${NC}"

PROJECT_DIR="/home/aipainting/ai-dynamic-painting"
ENV_FILE="$PROJECT_DIR/backend/.env"
ENV_TEMPLATE="$PROJECT_DIR/backend/.env.template"

log_header "Step 1: 環境確認"

# プロジェクトディレクトリの確認
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "プロジェクトディレクトリが見つかりません: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"
log_success "プロジェクトディレクトリ確認: $(pwd)"

# テンプレートファイルの確認
if [ ! -f "$ENV_TEMPLATE" ]; then
    log_error ".env.templateが見つかりません: $ENV_TEMPLATE"
    exit 1
fi

log_success ".env.templateファイル確認完了"

log_header "Step 2: 既存設定確認"

# 既存の.envファイル確認
if [ -f "$ENV_FILE" ]; then
    log_warning "既存の.envファイルが存在します"
    echo -e "${YELLOW}既存ファイルをバックアップしますか？ [y/N]: ${NC}"
    read -r BACKUP_CHOICE
    
    if [[ $BACKUP_CHOICE =~ ^[Yy]$ ]]; then
        BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$ENV_FILE" "$BACKUP_FILE"
        log_success "バックアップ作成: $BACKUP_FILE"
    fi
else
    log_info "新規.envファイルを作成します"
fi

log_header "Step 3: .envファイル作成"

# テンプレートから.envファイルを作成
cp "$ENV_TEMPLATE" "$ENV_FILE"
log_success ".envファイルをテンプレートから作成しました"

log_header "Step 4: API キー設定"

echo -e "${CYAN}以下のAPI キーの設定が必要です：${NC}"
echo "1. 🎬 VEO API Key (Google VEO-2) - 動画生成"
echo "2. 🧠 Gemini API Key (Google Gemini) - AI処理"  
echo "3. 🌤️ Weather API Key (OpenWeatherMap) - 天気データ"
echo "4. 🤖 Claude API Key (Anthropic) - AI支援 (Optional)"
echo ""

# VEO API設定
echo -e "${BLUE}VEO API Key設定:${NC}"
echo "Google Cloud Console → VEO API → 認証情報でキーを取得"
echo -e "${YELLOW}VEO API Keyを入力してください (空白でスキップ): ${NC}"
read -r VEO_API_KEY

if [ -n "$VEO_API_KEY" ]; then
    # .envファイルでVEO_API_KEYを更新
    sed -i "s/VEO_API_KEY=.*/VEO_API_KEY=$VEO_API_KEY/" "$ENV_FILE"
    log_success "VEO API Key設定完了"
else
    log_warning "VEO API Keyスキップ - 後で手動設定が必要"
fi

# Gemini API設定
echo -e "${BLUE}Gemini API Key設定:${NC}"
echo "Google AI Studio → API Key作成でキーを取得"
echo -e "${YELLOW}Gemini API Keyを入力してください (空白でスキップ): ${NC}"
read -r GEMINI_API_KEY

if [ -n "$GEMINI_API_KEY" ]; then
    # .envファイルにGEMINI_API_KEYを追加
    echo "GEMINI_API_KEY=$GEMINI_API_KEY" >> "$ENV_FILE"
    log_success "Gemini API Key設定完了"
else
    log_warning "Gemini API Keyスキップ - 後で手動設定が必要"
fi

# Weather API設定
echo -e "${BLUE}Weather API Key設定:${NC}"
echo "OpenWeatherMap → Sign up → API keysでキーを取得"
echo -e "${YELLOW}Weather API Keyを入力してください (空白でスキップ): ${NC}"
read -r WEATHER_API_KEY

if [ -n "$WEATHER_API_KEY" ]; then
    sed -i "s/WEATHER_API_KEY=.*/WEATHER_API_KEY=$WEATHER_API_KEY/" "$ENV_FILE"
    log_success "Weather API Key設定完了"
else
    log_warning "Weather API Keyスキップ - 後で手動設定が必要"
fi

# Claude API設定
echo -e "${BLUE}Claude API Key設定 (Optional):${NC}"
echo "Anthropic Console → API Keysでキーを取得"
echo -e "${YELLOW}Claude API Keyを入力してください (空白でスキップ): ${NC}"
read -r CLAUDE_API_KEY

if [ -n "$CLAUDE_API_KEY" ]; then
    echo "ANTHROPIC_API_KEY=$CLAUDE_API_KEY" >> "$ENV_FILE"
    log_success "Claude API Key設定完了"
else
    log_info "Claude API Keyスキップ (Optional)"
fi

log_header "Step 5: 設定確認"

# 設定内容の確認（キーをマスクして表示）
echo -e "${CYAN}設定された.envファイル内容:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# API Keyをマスクして表示
if grep -q "VEO_API_KEY=.*[^=]$" "$ENV_FILE"; then
    echo "✅ VEO_API_KEY: ****...$(grep VEO_API_KEY "$ENV_FILE" | cut -d'=' -f2 | tail -c 5)"
else
    echo "❌ VEO_API_KEY: 未設定"
fi

if grep -q "GEMINI_API_KEY=.*[^=]$" "$ENV_FILE"; then
    echo "✅ GEMINI_API_KEY: ****...$(grep GEMINI_API_KEY "$ENV_FILE" | cut -d'=' -f2 | tail -c 5)"
else
    echo "❌ GEMINI_API_KEY: 未設定"
fi

if grep -q "WEATHER_API_KEY=.*[^=]$" "$ENV_FILE"; then
    echo "✅ WEATHER_API_KEY: ****...$(grep WEATHER_API_KEY "$ENV_FILE" | cut -d'=' -f2 | tail -c 5)"
else
    echo "❌ WEATHER_API_KEY: 未設定"
fi

if grep -q "ANTHROPIC_API_KEY=.*[^=]$" "$ENV_FILE"; then
    echo "✅ ANTHROPIC_API_KEY: ****...$(grep ANTHROPIC_API_KEY "$ENV_FILE" | cut -d'=' -f2 | tail -c 5)"
else
    echo "ℹ️ ANTHROPIC_API_KEY: 未設定 (Optional)"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_header "Step 6: 次のステップ"

echo -e "${GREEN}🎉 API Key設定スクリプト完了！${NC}"
echo ""
echo -e "${CYAN}次のアクション:${NC}"
echo "1. 📝 手動設定（必要に応じて）:"
echo "   nano $ENV_FILE"
echo ""
echo "2. 🧪 API接続テスト:"
echo "   cd backend"
echo "   python -m pytest tests/integration/test_*_connection.py -v"
echo ""
echo "3. 🎬 VEO API動画生成テスト:"
echo "   python -m pytest tests/integration/test_veo_generation.py -v"
echo ""
echo "4. 🔄 完全システム起動:"
echo "   ./scripts/start_dev.sh"
echo ""
echo -e "${PURPLE}博士からのメッセージ:${NC}"
echo "「API キー設定完了で、ついに実動作確認の始まりなのだ〜！」"
echo "「Phase 3でAI動的絵画システムが実用レベルに到達するのだ！」"

echo ""
echo -e "${YELLOW}⚠️ セキュリティ注意:${NC}"
echo "- .envファイルは.gitignoreで除外されています"
echo "- API キーは外部に公開しないでください"
echo "- 定期的にキーをローテーションしてください"