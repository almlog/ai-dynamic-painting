#!/bin/bash

# Version Integrity Audit Script
# Created: 2025-09-22 for信頼性回復

echo "=== AI動的絵画システム 実態監査 ==="
echo "実行日時: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. システムバージョン確認
echo "🔍 システム実態確認:"
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    SYSTEM_STATUS=$(curl -s http://localhost:8000/health)
    echo "  Backend稼働: ✅ 正常"
    echo "  システム情報: $SYSTEM_STATUS"
else
    echo "  Backend稼働: ❌ 停止中"
fi

# 2. ファイル実装確認
echo ""
echo "📁 実装状況:"
BACKEND_FILES=$(find backend/src -name "*.py" 2>/dev/null | wc -l)
TEST_FILES=$(find backend/tests -name "test_*.py" 2>/dev/null | wc -l)
echo "  Backendファイル数: ${BACKEND_FILES}個"
echo "  テストファイル数: ${TEST_FILES}個"

# 3. Phase定義確認
echo ""
echo "📊 フェーズ状況:"
if grep -q "Phase 2" backend/src/main.py 2>/dev/null; then
    echo "  システムPhase: Phase 2 (main.pyより)"
else
    echo "  システムPhase: 未定義"
fi

# 4. README整合性確認
echo ""
echo "📄 文書整合性:"
README_VERSION=$(grep -o "v[0-9]\+\.[0-9]\+" README.md | head -1)
README_PHASE=$(grep -o "Phase [0-9]" README.md | head -1)
echo "  README記載バージョン: ${README_VERSION}"
echo "  README記載フェーズ: ${README_PHASE}"

# 5. 虚偽表記チェック
echo ""
echo "⚠️ 虚偽表記チェック:"
FAKE_COMPLETE=$(grep -c "100%完了\|完全完成" README.md 2>/dev/null || echo 0)
EXAGGERATION=$(grep -c "🎉.*完了" README.md 2>/dev/null || echo 0)
echo "  100%完了表記: ${FAKE_COMPLETE}箇所"
echo "  誇張完了表記: ${EXAGGERATION}箇所"

# 6. 結論
echo ""
echo "📋 監査結論:"
if [ "$FAKE_COMPLETE" -eq 0 ] && [ "$EXAGGERATION" -lt 3 ]; then
    echo "  情報信頼性: ✅ 良好"
else
    echo "  情報信頼性: ⚠️ 要改善 (虚偽表記あり)"
fi

echo ""
echo "=== 監査完了 ==="