# 🚀 簡単起動ガイド - AI動的絵画システム

## ⚡ 超高速起動（推奨）

### 1. ワンコマンド起動
```bash
cd /home/aipainting/ai-dynamic-painting && ./scripts/quick-start.sh
```

**完了**: 10秒で両サーバー起動完了！

### 2. アクセス確認
- **Backend**: http://localhost:8000 
- **Frontend**: http://localhost:5173
- **API仕様**: http://localhost:8000/docs

---

## 🔧 手動起動（詳細手順）

### 1. プロジェクトディレクトリに移動
```bash
cd /home/aipainting/ai-dynamic-painting
```

### 2. バックエンド起動
```bash
# 仮想環境アクティベート & FastAPIサーバー起動
source .venv/bin/activate
cd backend
PYTHONPATH=/home/aipainting/ai-dynamic-painting/backend/src python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. フロントエンド起動（新しいターミナル）
```bash
cd /home/aipainting/ai-dynamic-painting/frontend
npm run dev
```

---

## 📋 動作確認チェックリスト

### ✅ バックエンド確認
```bash
curl http://localhost:8000/health
# 期待: {"status": "healthy", "phase": "Phase 6: VEO API統合完了"}
```

### ✅ フロントエンド確認
```bash
curl http://localhost:5173/
# 期待: HTMLページが返る
```

### ✅ VEO API確認
```bash
curl -X POST http://localhost:8000/api/ai/health
# 期待: {"status": "healthy", "service": "ai_generation_simple"}
```

---

## 🚨 よくある起動エラーと解決方法

### ❌ "ModuleNotFoundError" (バックエンド)
```bash
# 解決: PYTHONPATHを正しく設定
export PYTHONPATH=/home/aipainting/ai-dynamic-painting/backend/src
```

### ❌ "Port 8000 already in use"
```bash
# 解決: 既存プロセスを終了
pkill -f uvicorn
```

### ❌ "Port 5173 already in use"
```bash
# 解決: 既存プロセスを終了
pkill -f "npm run dev"
```

### ❌ "Virtual environment not found"
```bash
# 解決: 仮想環境を再作成
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 開発環境起動（Claude用）

Claudeが開発する際の起動手順：

### 1. 博士の作業開始儀式
```bash
SuperClaude --serena --think
cd /home/aipainting/ai-dynamic-painting
```

### 2. システム状況確認
```bash
# バックエンド動作確認
curl http://localhost:8000/health

# フロントエンド動作確認
curl http://localhost:5173/
```

### 3. 必要に応じてサーバー起動
```bash
# バックエンドが停止している場合
cd backend && source ../.venv/bin/activate
PYTHONPATH=$(pwd)/src python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &

# フロントエンドが停止している場合
cd frontend && npm run dev &
```

---

## 🔄 プロセス管理

### 起動中プロセス確認
```bash
# バックエンドプロセス確認
ps aux | grep uvicorn

# フロントエンドプロセス確認  
ps aux | grep "npm run dev"
```

### 全サーバー停止
```bash
# 全プロセス終了
pkill -f uvicorn
pkill -f "npm run dev"
```

### バックグラウンド起動
```bash
# バックエンド（バックグラウンド）
cd backend && source ../.venv/bin/activate
nohup PYTHONPATH=$(pwd)/src python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &

# フロントエンド（バックグラウンド）
cd frontend && nohup npm run dev > ../logs/frontend.log 2>&1 &
```

---

## 📊 起動状態早見表

| サービス | URL | 期待レスポンス |
|---------|-----|---------------|
| **Backend Health** | http://localhost:8000/health | `{"status": "healthy"}` |
| **Frontend** | http://localhost:5173/ | HTMLページ表示 |
| **API Docs** | http://localhost:8000/docs | Swagger UI表示 |
| **VEO API** | http://localhost:8000/api/ai/health | `{"status": "healthy"}` |

---

<div align="center">

**💡 起動で困ったら、まず `./scripts/quick-start.sh` を試してね！**

🤖 **博士のAI動的絵画システム - Phase 6: VEO API統合完了**

</div>