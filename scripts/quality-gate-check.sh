#!/bin/bash

# 品質ゲート検証スクリプト
# 実装前・実装中の品質確認を自動化

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}======================================${NC}"
echo -e "${PURPLE}🚨 品質ゲート検証システム${NC}"
echo -e "${PURPLE}======================================${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 検証対象ディレクトリ
BACKEND_DIR="$PROJECT_ROOT/backend"
DOCS_DIR="$PROJECT_ROOT/docs"

# 失敗カウンター
FAILURES=0

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILURES++))
}

log_info() {
    echo -e "${CYAN}ℹ️ $1${NC}"
}

# Gate 1: 技術選択検証
check_technology_decisions() {
    echo -e "\n${BLUE}Gate 1: 技術選択検証${NC}"
    
    # matplotlib使用チェック（禁止）- venv除外
    if find "$BACKEND_DIR" -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" -exec grep -l "import matplotlib\|from matplotlib" {} \; 2>/dev/null | grep -q .; then
        log_error "matplotlib使用が検出されました（AI画像生成での使用は禁止）"
        echo -e "  検出ファイル:"
        find "$BACKEND_DIR" -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" -exec grep -l "import matplotlib\|from matplotlib" {} \; 2>/dev/null | head -5 | sed 's/^/    /'
        echo -e "  📖 参考: docs/TECHNICAL_DECISION_VALIDATION.md"
    else
        log_success "matplotlib使用チェック: 問題なし"
    fi
    
    # 技術選択記録の存在確認
    if [ -f "$DOCS_DIR/TECHNICAL_DECISION_VALIDATION.md" ]; then
        log_success "技術選択検証文書: 存在確認"
    else
        log_error "技術選択検証文書が見つかりません"
    fi
    
    # ADR文書の確認
    if ls "$DOCS_DIR"/ADR-*.md >/dev/null 2>&1; then
        log_success "アーキテクチャ決定記録: 存在確認"
        echo -e "  記録数: $(ls "$DOCS_DIR"/ADR-*.md 2>/dev/null | wc -l)件"
    else
        log_warning "ADR文書が見つかりません（推奨: 主要技術選択はADRで記録）"
    fi
}

# Gate 2: AI画像生成アーキテクチャ検証
check_ai_architecture() {
    echo -e "\n${BLUE}Gate 2: AI画像生成アーキテクチャ検証${NC}"
    
    # Gemini Service確認
    if [ -f "$BACKEND_DIR/src/services/gemini_service.py" ]; then
        if grep -q "def generate_image" "$BACKEND_DIR/src/services/gemini_service.py"; then
            log_success "AI画像生成サービス: 適切に実装済み"
        else
            log_error "AI画像生成メソッドが見つかりません"
        fi
        
        # Google Cloud Imagen使用確認
        if grep -q "imagegeneration@006\|aiplatform" "$BACKEND_DIR/src/services/gemini_service.py"; then
            log_success "Google Cloud Imagen統合: 確認"
        else
            log_warning "Google Cloud Imagen統合が確認できません"
        fi
    else
        log_error "gemini_service.pyが見つかりません"
    fi
    
    # Admin API統合確認
    if [ -f "$BACKEND_DIR/src/api/routes/admin.py" ]; then
        if grep -q "generate_with_gemini\|gemini_service.generate_image" "$BACKEND_DIR/src/api/routes/admin.py"; then
            log_success "Admin API AI統合: 確認"
        else
            log_error "Admin APIでのAI統合が確認できません"
        fi
    else
        log_warning "admin.pyが見つかりません"
    fi
}

# Gate 3: コード品質検証
check_code_quality() {
    echo -e "\n${BLUE}Gate 3: コード品質検証${NC}"
    
    # Python文法チェック
    if command -v python3 >/dev/null 2>&1; then
        local python_files_count=0
        local syntax_errors=0
        
        while IFS= read -r -d '' file; do
            ((python_files_count++))
            if ! python3 -m py_compile "$file" >/dev/null 2>&1; then
                ((syntax_errors++))
                log_error "Python文法エラー: $file"
            fi
        done < <(find "$BACKEND_DIR" -name "*.py" -not -path "*/.venv/*" -not -path "*/__pycache__/*" -print0)
        
        if [ $syntax_errors -eq 0 ]; then
            log_success "Python文法チェック: ${python_files_count}ファイル 全て正常"
        else
            log_error "Python文法エラー: ${syntax_errors}/${python_files_count}ファイル"
        fi
    else
        log_warning "Python3が見つかりません - 文法チェックをスキップ"
    fi
    
    # テストファイル存在確認
    if [ -d "$PROJECT_ROOT/tests" ] || find "$BACKEND_DIR" -name "test_*.py" -o -name "*_test.py" | head -1 >/dev/null; then
        local test_count=$(find "$PROJECT_ROOT" -name "test_*.py" -o -name "*_test.py" 2>/dev/null | wc -l)
        log_success "テストファイル: ${test_count}ファイル存在"
    else
        log_warning "テストファイルが見つかりません（TDD推奨）"
    fi
}

# Gate 4: 文書化品質検証
check_documentation() {
    echo -e "\n${BLUE}Gate 4: 文書化品質検証${NC}"
    
    # 必須文書の確認
    local required_docs=(
        "README.md"
        "CLAUDE.md"
        "docs/TECHNICAL_DECISION_VALIDATION.md"
    )
    
    for doc in "${required_docs[@]}"; do
        if [ -f "$PROJECT_ROOT/$doc" ]; then
            log_success "必須文書: $doc"
        else
            log_error "必須文書が見つかりません: $doc"
        fi
    done
    
    # 品質管理プロトコル記載確認
    if grep -q "技術選択検証\|品質ゲート\|matplotlib.*事件" "$PROJECT_ROOT/README.md" 2>/dev/null; then
        log_success "品質管理プロトコル: README.mdに記載済み"
    else
        log_error "品質管理プロトコルがREADME.mdに記載されていません"
    fi
    
    if grep -q "技術決定.*検証\|matplotlib.*事件" "$PROJECT_ROOT/CLAUDE.md" 2>/dev/null; then
        log_success "技術検証プロトコル: CLAUDE.mdに記載済み"
    else
        log_error "技術検証プロトコルがCLAUDE.mdに記載されていません"
    fi
}

# Gate 5: セキュリティ・設定検証
check_security_config() {
    echo -e "\n${BLUE}Gate 5: セキュリティ・設定検証${NC}"
    
    # .env.example存在確認
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        log_success "環境変数テンプレート: .env.example存在"
    else
        log_warning ".env.exampleが見つかりません（推奨）"
    fi
    
    # ハードコーディングされたAPIキー検索
    if find "$BACKEND_DIR" -name "*.py" -exec grep -l "sk-\|API_KEY.*=" {} \; 2>/dev/null | head -1 >/dev/null; then
        log_error "ハードコーディングされたAPIキーの可能性を検出"
        echo -e "  確認が必要なファイル:"
        find "$BACKEND_DIR" -name "*.py" -exec grep -l "sk-\|API_KEY.*=" {} \; 2>/dev/null | head -3 | sed 's/^/    /'
    else
        log_success "APIキーハードコーディング: 検出されず"
    fi
    
    # gitignore確認
    if [ -f "$PROJECT_ROOT/.gitignore" ]; then
        if grep -q "\.env$\|__pycache__\|\.venv" "$PROJECT_ROOT/.gitignore"; then
            log_success ".gitignore: 適切に設定済み"
        else
            log_warning ".gitignoreに重要な除外設定が不足している可能性"
        fi
    else
        log_error ".gitignoreが見つかりません"
    fi
}

# メイン実行
main() {
    echo -e "${CYAN}実行時刻: $(date)${NC}"
    echo -e "${CYAN}プロジェクトルート: $PROJECT_ROOT${NC}\n"
    
    # 各ゲートの実行
    check_technology_decisions
    check_ai_architecture
    check_code_quality
    check_documentation
    check_security_config
    
    # 結果サマリー
    echo -e "\n${PURPLE}======================================${NC}"
    echo -e "${PURPLE}📊 品質ゲート検証結果${NC}"
    echo -e "${PURPLE}======================================${NC}"
    
    if [ $FAILURES -eq 0 ]; then
        echo -e "${GREEN}🎉 全ての品質ゲートをパスしました！${NC}"
        echo -e "${GREEN}   実装・デプロイを続行できます。${NC}"
        exit 0
    else
        echo -e "${RED}❌ ${FAILURES}件の問題が検出されました${NC}"
        echo -e "${RED}   問題を修正してから実装を続行してください。${NC}"
        echo -e "\n${CYAN}📖 参考資料:${NC}"
        echo -e "  - docs/TECHNICAL_DECISION_VALIDATION.md"
        echo -e "  - README.md (品質管理プロトコル)"
        echo -e "  - CLAUDE.md (技術検証プロトコル)"
        exit 1
    fi
}

# ヘルプ表示
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [--help]"
    echo ""
    echo "AI動的絵画システムの品質ゲート検証を実行します。"
    echo ""
    echo "検証項目:"
    echo "  Gate 1: 技術選択検証（matplotlib使用禁止等）"
    echo "  Gate 2: AI画像生成アーキテクチャ検証"  
    echo "  Gate 3: コード品質検証"
    echo "  Gate 4: 文書化品質検証"
    echo "  Gate 5: セキュリティ・設定検証"
    echo ""
    echo "終了コード:"
    echo "  0: 全ゲートパス（実装続行可能）"
    echo "  1: 問題検出（修正必要）"
    exit 0
fi

# メイン実行
main