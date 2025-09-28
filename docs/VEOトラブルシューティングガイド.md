# 🔧 VEOトラブルシューティングガイド

**AI動的絵画システム - VEO API問題解決完全マニュアル**

> 「トラブルが起きても大丈夫！このガイドで問題を解決するのだ〜！」 - 博士

## 📋 概要

VEO動画生成システムで発生する可能性のある問題と、その詳細な解決方法を体系的にまとめました。初心者から上級者まで対応できる包括的なトラブルシューティングガイドです。

## 🚨 緊急度別問題分類

### 🔴 緊急（即座対応必要）
- システム全体が応答しない
- 予算制限を大幅超過
- 生成された動画が破損
- セキュリティエラー

### 🟡 重要（24時間以内対応）
- 特定機能が動作しない
- 生成品質が著しく低下
- コスト計算が不正確
- パフォーマンス低下

### 🟢 軽微（時間があるときに対応）
- UI表示の軽微な問題
- 生成時間が予想より長い
- 履歴表示の並び順
- プロンプト提案の改善

## 🔍 問題診断フローチャート

```
問題発生
    ↓
[システム全体の問題？]
    Yes → システム診断セクションへ
    No ↓
[動画生成の問題？]
    Yes → 生成問題セクションへ
    No ↓
[UI・表示の問題？]
    Yes → UI問題セクションへ
    No ↓
[コスト・料金の問題？]
    Yes → コスト問題セクションへ
    No ↓
[その他] → その他セクションへ
```

## 🖥️ システム診断・修復

### システム応答なし
**症状**: Web画面が表示されない、APIが応答しない

**診断手順**:
```bash
# 1. 基本接続確認
curl -I http://localhost:5173/
curl -I http://localhost:8000/health

# 2. サービス状態確認
ps aux | grep -E "(node|python|uvicorn)"
netstat -tlnp | grep -E "(5173|8000)"

# 3. ログ確認
tail -f backend/logs/application.log
tail -f frontend/logs/dev-server.log
```

**解決方法**:
```bash
# サービス再起動（推奨順序）
# 1. バックエンド再起動
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. フロントエンド再起動
cd frontend && npm run dev

# 3. 全体再起動（問題継続時）
docker-compose down && docker-compose up -d
```

### データベース接続エラー
**症状**: "Database connection failed", "SQLite lock error"

**診断方法**:
```bash
# データベースファイル確認
ls -la backend/database.db
sqlite3 backend/database.db ".schema"

# ファイル権限確認
ls -la backend/ | grep database
```

**解決方法**:
```bash
# 1. データベースファイル修復
sqlite3 backend/database.db "PRAGMA integrity_check;"

# 2. 権限修正
chmod 664 backend/database.db
chown $USER:$USER backend/database.db

# 3. バックアップから復元（最終手段）
cp backend/database_backup.db backend/database.db
```

### Google Cloud認証エラー
**症状**: "Authentication failed", "Invalid credentials"

**診断手順**:
```bash
# 1. 認証ファイル確認
ls -la backend/credentials/
echo $GOOGLE_APPLICATION_CREDENTIALS

# 2. gcloud認証状態確認
gcloud auth list
gcloud auth application-default print-access-token

# 3. プロジェクト設定確認
gcloud config get-value project
```

**解決方法**:
```bash
# 1. 認証ファイル再設定
export GOOGLE_APPLICATION_CREDENTIALS="backend/credentials/veo-service-account.json"

# 2. gcloud再認証
gcloud auth application-default login

# 3. 権限確認・修正
gcloud projects add-iam-policy-binding ai-dynamic-painting \
    --member="serviceAccount:veo-service@ai-dynamic-painting.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

## 🎬 動画生成問題の診断・解決

### 生成が開始されない
**症状**: 「Generate Video」ボタンを押しても processing にならない

**原因と解決**:

#### 1. パラメータ入力エラー
```yaml
チェック項目:
  - プロンプト: 1-2000文字以内
  - 長さ: 5-30秒の範囲
  - 解像度: 720p/1080p/4K のいずれか
  - FPS: 24/30/60 のいずれか
  - 品質: standard/high/premium のいずれか

解決方法:
  - ブラウザの開発者ツールでエラーメッセージ確認
  - フォームを一度リセットして再入力
  - サンプルプロンプトで動作テスト
```

#### 2. 予算制限到達
```yaml
確認方法:
  - Dashboard > Settings > Budget で使用量確認
  - 今月の使用金額と制限値の比較

解決方法:
  - 予算制限値の引き上げ
  - 不要な履歴動画の削除
  - 翌月まで待機
```

#### 3. API制限到達
```yaml
レート制限確認:
  - 1分間の生成回数: 10回以下
  - 1時間の生成回数: 100回以下
  - 同時生成数: 3個以下

解決方法:
  - 10分待ってから再試行
  - 他の生成が完了してから開始
  - 時間を空けてアクセス
```

### 生成が「Processing」で止まる
**症状**: 進捗が0%または途中で止まる

**段階的診断**:

#### Stage 1: 基本確認（0-5分）
```bash
# 1. 生成ステータス直接確認
curl -s http://localhost:8000/ai/ai/generation/{task_id}

# 2. システムログ確認
tail -f backend/logs/veo_client.log
grep -i error backend/logs/application.log
```

#### Stage 2: VEO API接続確認（5-10分）
```bash
# VEO接続テスト実行
cd backend && python scripts/test_veo_connection.py

# Google Cloud API有効化確認
gcloud services list --enabled | grep aiplatform
```

#### Stage 3: 長時間処理の判定（10分以上）
```yaml
正常な処理時間の目安:
  720p/standard: 8-30秒
  1080p/high: 30-120秒
  4K/premium: 2-10分

異常判定基準:
  - 30分以上 processing 状態継続
  - progress_percent が30分以上変化なし
  - エラーログに繰り返し同じエラー
```

**解決方法**:
```bash
# 1. 生成キャンセル
curl -X DELETE http://localhost:8000/ai/ai/generation/{task_id}

# 2. より軽い設定で再試行
# 720p/5秒/standard でテスト生成

# 3. 時間帯を変更して再試行
# 深夜2-6時（JST）推奨
```

### 生成完了後に動画が再生できない
**症状**: 「Completed」になったが動画ファイルが開けない

**原因別対処**:

#### 1. ファイル破損
```bash
# ファイル存在・サイズ確認
curl -I {video_url}
wget {video_url} -O test_video.mp4
ffprobe test_video.mp4
```

#### 2. ブラウザ互換性
```yaml
対応ブラウザ:
  - Chrome: 90+
  - Firefox: 88+
  - Safari: 14+
  - Edge: 90+

対処方法:
  - ブラウザを最新版に更新
  - 他のブラウザで確認
  - ダウンロードして専用プレイヤーで再生
```

#### 3. ネットワーク問題
```bash
# 帯域幅テスト
curl -w "time_total: %{time_total}s\n" -o /dev/null {video_url}

# DNS解決確認
nslookup storage.googleapis.com
```

### 生成品質が期待より低い
**症状**: 生成された動画の画質・内容が期待と異なる

**品質改善手順**:

#### 1. プロンプト最適化
```yaml
現在のプロンプト分析:
  - 文字数: {count}文字
  - 言語: 日本語/英語
  - 具体性: 抽象的/具体的
  - 修飾語数: {count}個

改善方針:
  - 英語プロンプトに変更（品質向上）
  - より具体的な描写に変更
  - 不要な修飾語を削除
  - アクション要素を追加
```

#### 2. パラメータ調整
```yaml
品質向上パラメータ:
  resolution: 1080p → 4K
  quality: standard → high → premium
  fps: 24 → 30 → 60

コスト効率パラメータ:
  - 1080p/high: 品質と価格のバランス
  - 4K/standard: 高解像度でコスト抑制
```

#### 3. 参考プロンプト活用
```yaml
高品質プロンプト例:
  風景: "Cinematic wide shot of a serene mountain lake at golden hour, mist rising from water surface, reflected peaks, 4K nature documentary style"
  
  抽象: "Fluid abstract shapes morphing in slow motion, iridescent colors blending seamlessly, ethereal lighting, minimalist aesthetic"
  
  動物: "Majestic eagle soaring over pristine wilderness, wings spread wide, mountain backdrop, National Geographic style cinematography"
```

## 🖥️ UI・表示問題の解決

### フォームが送信できない
**症状**: 「Generate Video」ボタンが無効、エラーメッセージが表示

**診断手順**:
```javascript
// ブラウザ開発者ツールで確認
// 1. Console タブでJavaScriptエラー確認
console.log("Form validation errors");

// 2. Network タブでAPI通信確認
// 3. Application タブでLocalStorage確認
localStorage.getItem('veo_settings');
```

**解決方法**:
```yaml
手順1: ブラウザキャッシュクリア
  - Ctrl+Shift+Delete (Windows/Linux)
  - Cmd+Shift+Delete (Mac)
  - 「Cached images and files」を選択

手順2: ローカルストレージクリア
  - 開発者ツール > Application > Local Storage
  - localhost:5173 の項目を削除

手順3: ページ強制リロード
  - Ctrl+F5 (Windows/Linux)
  - Cmd+Shift+R (Mac)
```

### 履歴が表示されない・更新されない
**症状**: Generation History タブが空、新しい生成が反映されない

**確認項目**:
```bash
# 1. API直接確認
curl -s http://localhost:8000/ai/ai/tasks

# 2. データベース直接確認
sqlite3 backend/database.db "SELECT * FROM generation_tasks LIMIT 5;"

# 3. ブラウザネットワークタブ確認
# 履歴API呼び出しのステータスコード確認
```

**解決方法**:
```yaml
API応答正常の場合:
  - ブラウザリロード
  - 時間フィルター設定確認
  - ページネーション設定確認

API応答異常の場合:
  - バックエンドログ確認
  - データベース接続状態確認
  - サービス再起動
```

### プレビュー動画が再生されない
**症状**: 履歴の「Preview」ボタンを押しても動画が表示されない

**原因別対処**:
```yaml
原因1: ファイルURL無効
  確認: 動画URLの有効性チェック
  対処: 再生成または管理者連絡

原因2: ブラウザセキュリティ設定
  確認: Mixed Content警告の有無
  対処: HTTPS接続または設定変更

原因3: 動画ファイル破損
  確認: ダウンロードして外部プレイヤーで確認
  対処: 再生成リクエスト
```

## 💰 コスト・料金問題の解決

### 予想より高額請求
**症状**: 想定よりも高い料金が計算されている

**料金確認手順**:
```bash
# 1. 詳細履歴の確認
curl -s "http://localhost:8000/ai/ai/tasks?include_costs=true"

# 2. コスト計算の検証
# 実際の設定値と料金計算式の照合
```

**料金計算式確認**:
```yaml
基本計算:
  基本料金 = $0.02/秒
  
係数適用:
  解像度係数 = 720p:1x, 1080p:2.5x, 4K:8x
  FPS係数 = 24fps:1x, 30fps:1.25x, 60fps:2x
  品質係数 = standard:1x, high:2x, premium:4x
  
最終料金:
  $0.02 × 秒数 × 解像度係数 × FPS係数 × 品質係数

例: 1080p/10秒/30fps/high
  $0.02 × 10 × 2.5 × 1.25 × 2 = $1.25
```

**対処方法**:
```yaml
設定見直し:
  - 不要に高い設定を標準に変更
  - テスト生成は720p/standard使用
  - 最終版のみ高品質設定

料金追跡:
  - 生成前に見積もり確認
  - 月間予算アラート設定
  - 週次料金レビュー実施
```

### 予算制限が正しく動作しない
**症状**: 予算制限を設定したが生成が続行される

**設定確認**:
```bash
# 現在の予算設定確認
curl -s "http://localhost:8000/ai/ai/admin/config" | grep budget

# 使用量確認
curl -s "http://localhost:8000/ai/ai/dashboard/summary" | grep cost
```

**問題パターンと解決**:
```yaml
パターン1: 設定が保存されていない
  確認: 設定画面での値と実際の値比較
  解決: 再設定後に明示的に保存

パターン2: 集計タイミングの問題
  確認: リアルタイム集計 vs バッチ集計
  解決: 数分待ってから確認

パターン3: 複数セッションの問題
  確認: 他のブラウザ・タブでの同時利用
  解決: 全セッションで設定同期
```

## 🔧 その他の問題

### システムが重い・遅い
**症状**: 画面表示や操作に時間がかかる

**パフォーマンス診断**:
```bash
# 1. システムリソース確認
htop
df -h
free -m

# 2. ネットワーク状況確認
ping google.com
speedtest-cli

# 3. プロセス負荷確認
ps aux --sort=-%cpu | head -10
```

**最適化手順**:
```yaml
短期対処:
  - 不要なブラウザタブを閉じる
  - 他のアプリケーションを終了
  - ブラウザキャッシュクリア

長期対処:
  - システムメモリ増設
  - SSDストレージ使用
  - より高速なネットワーク環境
```

### ログファイルサイズ過大
**症状**: ディスク容量不足、ログファイルが巨大

**ログ管理**:
```bash
# ログサイズ確認
du -sh backend/logs/
ls -lah backend/logs/

# ログローテーション
find backend/logs/ -name "*.log" -size +100M -delete
logrotate /etc/logrotate.d/ai-painting-system
```

### バックアップ・復元
**症状**: データ損失に備えたバックアップが必要

**バックアップ手順**:
```bash
# 1. データベースバックアップ
sqlite3 backend/database.db ".backup backend/backup_$(date +%Y%m%d).db"

# 2. 設定ファイルバックアップ
tar -czf config_backup_$(date +%Y%m%d).tar.gz backend/.env frontend/.env.local

# 3. 生成動画バックアップ（選択的）
rsync -av backend/generated_videos/ backup/videos/
```

## 📞 サポート・連絡先

### 自己解決チェックリスト
```yaml
基本確認（5分）:
  □ サービス再起動試行
  □ ブラウザキャッシュクリア
  □ 最新ドキュメント確認

中級確認（15分）:
  □ ログファイル分析
  □ API直接テスト実行
  □ 設定値検証

上級確認（30分）:
  □ システムリソース分析
  □ ネットワーク接続診断
  □ データベース整合性確認
```

### 技術サポートへの報告情報
```yaml
必須情報:
  - 発生日時（JST）
  - 問題の詳細な症状
  - エラーメッセージ（完全版）
  - 操作手順の再現ステップ

環境情報:
  - ブラウザ名・バージョン
  - OS名・バージョン
  - ネットワーク環境

ログ情報:
  - backend/logs/application.log（エラー前後5分）
  - ブラウザ開発者ツールのConsoleログ
  - 実行したコマンドと結果
```

### ドキュメント更新・改善提案
問題解決方法の改善案や新しいトラブル事例があれば、本ドキュメントの更新提案をお願いします。

---

**🔧 VEOトラブルシューティングガイド**  
**AI動的絵画システム - 包括的問題解決マニュアル**

> 「どんな問題も、適切な手順で必ず解決できるのだ〜！このガイドを活用して、快適にVEOを楽しむのだ〜！」 - 博士