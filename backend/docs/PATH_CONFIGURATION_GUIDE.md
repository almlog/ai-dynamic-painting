# PATH設定ガイド - Google Cloud SDK環境構築

## 📋 問題の概要

Google Cloud SDK (gcloud) インストール後に発生するPATH設定の問題と解決方法について説明します。

## 🔍 問題の詳細

### 発生する状況
```bash
# gcloud CLIインストール後
./google-cloud-sdk/install.sh --quiet --path-update=true --bash-completion=true

# .bashrcは正しく更新される
$ tail ~/.bashrc
export PATH="$PATH:/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin"

# しかし、現在のセッションでは使えない
$ gcloud version
bash: gcloud: command not found

# フルパスでは動作する
$ ./google-cloud-sdk/bin/gcloud version
Google Cloud SDK 540.0.0
```

### 根本原因
1. **セッション継続の問題**: 既存のBashセッションでは、新しく追加されたPATH設定が自動的に反映されない
2. **PATH優先度の問題**: 一部の環境では、既存のPATH設定が新しい設定を上書きする場合がある
3. **環境変数の読み込みタイミング**: `source ~/.bashrc`実行後も、環境によってはPATHが即座に更新されない

## ✅ 解決方法

### 方法1: 現在セッション用の即座対応（推奨）
```bash
# 1. .bashrcを再読み込み
source ~/.bashrc

# 2. 現在セッション用にPATHを明示的に設定
export PATH="/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin:$PATH"

# 3. 確認
which gcloud
gcloud version
```

### 方法2: 新しいシェルセッション開始
```bash
# 新しいBashセッションを開始
bash

# または新しいターミナル起動
# PATHが自動的に設定される
gcloud version
```

### 方法3: 永続的なエイリアス設定
```bash
# .bashrcに便利なエイリアスを追加
echo 'alias gcloud="/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin/gcloud"' >> ~/.bashrc
source ~/.bashrc

# エイリアス経由でアクセス
gcloud version
```

## 🔧 確実な設定手順

### Step 1: インストール状況確認
```bash
# インストール確認
ls -la google-cloud-sdk/bin/gcloud

# 実行権限確認
./google-cloud-sdk/bin/gcloud version
```

### Step 2: .bashrc設定確認
```bash
# .bashrcの最後の数行を確認
tail -10 ~/.bashrc

# 期待される内容:
# export PATH="$PATH:/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin"
```

### Step 3: 現在セッションでのPATH更新
```bash
# 推奨手順
source ~/.bashrc
export PATH="/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin:$PATH"

# 確認
echo $PATH | grep google-cloud-sdk
which gcloud
```

### Step 4: 動作確認
```bash
# 基本動作確認
gcloud version
gcloud config list

# プロジェクト設定確認
gcloud config get-value project
```

## 🚨 トラブルシューティング

### 症状: `gcloud: command not found`
```bash
# 診断
echo $PATH | grep google-cloud-sdk

# 解決策1: 手動PATH設定
export PATH="/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin:$PATH"

# 解決策2: フルパス使用
/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin/gcloud version
```

### 症状: PATH設定が永続化されない
```bash
# .bashrcの確認
grep "google-cloud-sdk" ~/.bashrc

# 手動で追加（重複回避）
if ! grep -q "google-cloud-sdk" ~/.bashrc; then
    echo 'export PATH="$PATH:/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin"' >> ~/.bashrc
fi
```

### 症状: 認証時のエラー
```bash
# 環境確認
gcloud info --run-diagnostics

# 設定確認
gcloud config list
gcloud auth list
```

## 📚 ベストプラクティス

### 開発環境での推奨設定
```bash
# 1. 現在セッション用の確実な設定
source ~/.bashrc
export PATH="/home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin:$PATH"

# 2. プロジェクト設定
gcloud config set project ai-dynamic-painting

# 3. 動作確認スクリプト
cat << 'EOF' > check_gcloud.sh
#!/bin/bash
echo "=== gcloud PATH確認 ==="
which gcloud
echo "=== gcloud バージョン ==="
gcloud version
echo "=== gcloud 設定 ==="
gcloud config list
EOF
chmod +x check_gcloud.sh
./check_gcloud.sh
```

### 本番環境での設定
```bash
# システム全体での設定（管理者権限必要）
sudo ln -sf /home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud

# または個別ユーザー用
mkdir -p ~/.local/bin
ln -sf /home/aipainting/ai-dynamic-painting/google-cloud-sdk/bin/gcloud ~/.local/bin/gcloud
```

## 🎯 検証方法

### 完全なテストシーケンス
```bash
# 1. 基本コマンド実行
gcloud version || echo "ERROR: gcloud not found in PATH"

# 2. プロジェクト設定確認
gcloud config get-value project || echo "ERROR: Project not set"

# 3. 認証状況確認
gcloud auth list || echo "ERROR: No authentication"

# 4. APIアクセステスト（認証後）
gcloud projects describe ai-dynamic-painting || echo "ERROR: Cannot access project"
```

## 📝 記録・ログ

### 設定作業の記録
```bash
# 作業ログ記録
echo "$(date): gcloud PATH設定完了" >> ~/gcloud_setup.log
echo "PATH: $PATH" >> ~/gcloud_setup.log
echo "gcloud location: $(which gcloud)" >> ~/gcloud_setup.log
```

## 🔄 今後の注意点

1. **新しいターミナル**: 新しいターミナルでは自動的にPATHが設定される
2. **既存セッション**: 継続作業では手動でPATH更新が必要
3. **スクリプト実行**: シェルスクリプト内ではフルパス推奨
4. **CI/CD環境**: 自動化環境では毎回PATH設定を確認

---

**作成日**: 2025-09-26  
**対象**: AI動的絵画システム Phase 6  
**用途**: Google Cloud SDK PATH設定の標準化

**⚠️ 重要**: 本ドキュメントは実際のトラブルシューティング経験に基づいて作成されており、類似環境での問題解決に活用できます。