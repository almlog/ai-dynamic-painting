#!/bin/bash
# AI動的絵画システム - 開発セッション自動起動スクリプト
# ラズパイ起動後にこれ一つで全て準備完了

echo "🚀 AI動的絵画システム開発セッション開始"
echo "================================================"

# 1. プロジェクトディレクトリに移動
cd /home/aipainting/ai-dynamic-painting
echo "📁 プロジェクトディレクトリ: $(pwd)"
echo ""

# 2. 現在状況確認（startup-check.shの内容を実行）
echo "📋 プロジェクト状況確認中..."
bash scripts/startup-check.sh
echo ""

# 3. 仮想環境アクティベート確認
if [[ -f ".venv/bin/activate" ]]; then
    echo "🐍 仮想環境をアクティベート中..."
    source .venv/bin/activate
    echo "✅ 仮想環境アクティベート完了"
else
    echo "⚠️ 仮想環境が見つかりません"
fi
echo ""

# 4. Claude Code起動オプション
echo "🤖 Claude Code起動オプション:"
echo "1. 続きから起動: claude-code -c . (推奨)"
echo "2. 新規セッション: claude-code ."
echo "3. 手動起動: 後で手動実行"
echo ""

read -p "起動方法を選択 (1/2/3): " start_option

case $start_option in
    1)
        echo "🔄 Claude Code続きから起動中..."
        echo "📋 前回セッションの記憶・品質・設定を継続します"
        echo "🎯 Phase 2実装準備完了状況から再開"
        echo ""
        claude-code -c .
        ;;
    2)
        echo "🚀 Claude Code新規セッション起動中..."
        echo "⚠️ 新規セッション: プロジェクト状況の再確認が必要"
        echo ""
        claude-code .
        ;;
    3)
        echo "📝 手動起動コマンド:"
        echo "続きから: claude-code -c ."
        echo "新規から: claude-code ."
        echo ""
        echo "🎯 Phase 2実装準備完了！次はVEO API設定から開始です"
        ;;
    *)
        echo "❌ 無効な選択です。手動で起動してください。"
        echo "推奨: claude-code -c ."
        ;;
esac