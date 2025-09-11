# Quickstart Guide: Phase 1 手動動画管理システム

**Target**: 開発者・システム管理者  
**Time**: 30分でのセットアップ  
**Prerequisites**: Raspberry Pi 4/5, M5STACK Core2, モニター

## 🚀 クイックセットアップ (5分)

### 1. 依存関係インストール
```bash
# Raspberry Pi上で実行
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm git ffmpeg sqlite3

# Python依存関係
pip3 install fastapi uvicorn sqlite3 opencv-python pillow pytest

# Frontend依存関係  
npm install -g create-react-app
```

### 2. プロジェクトクローン & セットアップ
```bash
cd /home/pi
git clone https://github.com/your-repo/ai-dynamic-painting.git
cd ai-dynamic-painting

# バックエンドセットアップ
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# データベース初期化
python3 -m src.setup_database

# フロントエンドセットアップ
cd ../frontend  
npm install
npm run build
```

### 3. 基本動作確認
```bash
# バックエンド起動 (ターミナル1)
cd backend && source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000

# フロントエンド起動 (ターミナル2)  
cd frontend && npm start

# ブラウザで http://localhost:3000 アクセス
# M5STACK設定: WiFi接続 → IP: 192.168.1.100 (Raspberry Pi IP)
```

## 📋 完全セットアップ手順

### Phase 0: 環境準備

#### ハードウェア確認
- [ ] Raspberry Pi 4/5 (4GB+ RAM推奨)
- [ ] SDカード 64GB+ (Class 10)
- [ ] M5STACK Core2
- [ ] HDMIモニター (24-32インチ推奨)
- [ ] WiFiネットワーク環境

#### OS & 基本設定
```bash
# Raspberry Pi OS Lite インストール
# SSH有効化、WiFi設定完了後...

# システムアップデート
sudo apt update && sudo apt upgrade -y

# 必要パッケージインストール
sudo apt install -y \
  python3.11 python3.11-venv python3-pip \
  nodejs npm git curl wget \
  ffmpeg sqlite3 \
  vim htop tree

# GPU memory split (動画再生最適化)
sudo raspi-config
# Advanced Options → Memory Split → 128MB
```

#### Python環境セットアップ
```bash
# pyenvインストール (推奨)
curl https://pyenv.run | bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Python 3.11セットアップ
pyenv install 3.11.5
pyenv global 3.11.5
```

### Phase 1: アプリケーションセットアップ

#### 1. プロジェクト配置
```bash
# プロジェクトディレクトリ作成
sudo mkdir -p /opt/ai-painting
sudo chown pi:pi /opt/ai-painting
cd /opt/ai-painting

# リポジトリクローン
git clone https://github.com/your-repo/ai-dynamic-painting.git .
git checkout 001-phase-1-web
```

#### 2. バックエンド環境構築
```bash
cd /opt/ai-painting/backend

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install --upgrade pip
pip install \
  fastapi==0.104.1 \
  uvicorn[standard]==0.24.0 \
  python-multipart==0.0.6 \
  Pillow==10.1.0 \
  opencv-python==4.8.1.78 \
  sqlite3 \
  pytest==7.4.3 \
  pytest-asyncio==0.21.1
  
# requirements.txtに保存
pip freeze > requirements.txt
```

#### 3. データベースセットアップ
```bash
# データベースディレクトリ作成
mkdir -p /opt/ai-painting/data/{videos,thumbnails,database}

# データベース初期化スクリプト実行
cd /opt/ai-painting/backend
python3 scripts/init_database.py

# テストデータ投入 (オプション)
python3 scripts/seed_test_data.py
```

#### 4. フロントエンド環境構築
```bash
cd /opt/ai-painting/frontend

# Node.js LTS確認
node --version  # v18.x以上
npm --version   # v9.x以上

# 依存関係インストール  
npm install

# 本番ビルド
npm run build

# 静的ファイル配信設定
sudo ln -s /opt/ai-painting/frontend/build /var/www/html/ai-painting
```

### Phase 2: M5STACKセットアップ

#### 1. Arduino IDE設定
```bash
# Arduino IDE インストール (PC上で)
# ボードマネージャでM5STACK追加:
# https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/arduino/package_m5stack_index.json

# ライブラリインストール:
# - M5Core2
# - WiFi  
# - HTTPClient
# - ArduinoJson
```

#### 2. M5STACKプログラム書き込み
```cpp
// m5stack/src/main.cpp の内容を書き込み
// WiFi設定: SSID, Password
// Server設定: Raspberry Pi IP (192.168.1.100)

// アップロード後、M5STACKディスプレイで接続確認
```

### Phase 3: システム統合テスト

#### 1. 個別コンポーネントテスト
```bash
# バックエンドAPIテスト
cd /opt/ai-painting/backend
source venv/bin/activate
python -m pytest tests/ -v

# フロントエンドテスト  
cd /opt/ai-painting/frontend
npm test

# データベース接続テスト
python3 scripts/test_database.py
```

#### 2. 統合テスト実行
```bash
# システム全体テスト
cd /opt/ai-painting
python3 scripts/integration_test.py

# 確認項目:
# ✅ Web UI → バックエンド → データベース
# ✅ ファイルアップロード → 動画処理 → 表示  
# ✅ M5STACK → WiFi → API → 動画制御
# ✅ 24時間稼働テスト (監視)
```

#### 3. エンドツーエンドシナリオ
```bash
# シナリオ1: 動画アップロード〜再生
curl -X POST -F "file=@test_video.mp4" -F "title=Test Video" \
  http://localhost:8000/api/videos

curl -X POST -H "Content-Type: application/json" \
  -d '{"video_id": "VIDEO_UUID"}' \
  http://localhost:8000/api/display/play

# シナリオ2: M5STACKボタン操作  
# ボタンA: 次の動画
# ボタンB: 一時停止/再開
# ボタンC: 停止

# シナリオ3: 24時間稼働確認
sudo systemctl start ai-painting-backend
sudo systemctl start ai-painting-display  
# 24時間後にログ・リソース使用量確認
```

## 🔧 システムサービス設定

### systemdサービス作成
```bash
# バックエンドサービス
sudo tee /etc/systemd/system/ai-painting-backend.service > /dev/null <<EOF
[Unit]
Description=AI Painting Backend API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/ai-painting/backend
Environment=PATH=/opt/ai-painting/backend/venv/bin
ExecStart=/opt/ai-painting/backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# サービス有効化
sudo systemctl daemon-reload
sudo systemctl enable ai-painting-backend
sudo systemctl start ai-painting-backend
```

### 監視設定
```bash
# ログローテーション
sudo tee /etc/logrotate.d/ai-painting > /dev/null <<EOF
/opt/ai-painting/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 pi pi
}
EOF

# リソース監視 (cron)
crontab -e
# */5 * * * * /opt/ai-painting/scripts/monitor_system.py
```

## ✅ 動作確認チェックリスト

### システム基盤
- [ ] Raspberry Pi起動・SSH接続OK
- [ ] Python 3.11動作確認
- [ ] SQLite データベース作成OK
- [ ] ディスク容量十分 (50GB+空き)

### バックエンド
- [ ] FastAPI サーバー起動OK (http://localhost:8000)
- [ ] API ドキュメント表示OK (/docs)
- [ ] データベース接続OK
- [ ] ログ出力確認

### フロントエンド  
- [ ] React アプリ起動OK (http://localhost:3000)
- [ ] 動画アップロードUI表示OK
- [ ] API通信OK
- [ ] レスポンシブデザイン確認

### M5STACK
- [ ] WiFi接続OK
- [ ] Raspberry Pi API疎通OK  
- [ ] ボタン操作→動画制御OK
- [ ] ディスプレイ表示OK

### 統合システム
- [ ] 動画アップロード→再生フローOK
- [ ] M5STACKボタン→動画制御OK
- [ ] 24時間稼働OK (メモリリーク無し)
- [ ] エラー時の自動復旧OK

## 🚨 トラブルシューティング

### よくある問題
1. **API接続エラー**: ファイアウォール・IPアドレス確認
2. **動画再生エラー**: ffmpeg・コーデック確認  
3. **M5STACK WiFi接続失敗**: SSID・パスワード再設定
4. **メモリ不足**: swap設定、不要プロセス停止

### ログ確認コマンド
```bash
# システムログ
journalctl -u ai-painting-backend -f

# アプリケーションログ
tail -f /opt/ai-painting/logs/backend.log

# リソース使用量
htop
df -h
```

## 📚 次のステップ
Phase 1完成後:
1. **Phase 2準備**: VEO API統合設計
2. **性能改善**: 負荷テスト・最適化
3. **機能拡張**: 追加要件の実装
4. **ドキュメント更新**: 運用マニュアル作成