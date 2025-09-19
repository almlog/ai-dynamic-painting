# 🚀 M5STACK 本番環境デプロイメントガイド

## 📋 デプロイ前チェックリスト

### ✅ 環境設定の確認
- [ ] WiFi設定の確認
- [ ] Backend APIのIPアドレス確認
- [ ] M5STACK Core2 充電完了

## 🔧 本番コードのデプロイ手順

### 1. Arduino IDE準備
```bash
# Arduino IDEを起動
# M5Stack Core2ボードを選択
Tools -> Board -> M5Stack -> M5Stack Core2
```

### 2. ライブラリ確認
必要なライブラリ:
- M5Stack (最新版)
- WiFi (標準)
- HTTPClient (標準)
- ArduinoJson (v6.x)

### 3. 設定変更 (重要！)

`/home/aipainting/ai-dynamic-painting/m5stack/src/ai/ai_display.ino` の以下の部分を確認・修正:

```cpp
// ===== Configuration =====
const char* WIFI_SSID = "makotaronet";                    // ← あなたのWiFi SSID
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918";  // ← あなたのWiFiパスワード
const char* API_BASE_URL = "http://192.168.10.7:8000";    // ← Raspberry PiのIPアドレス:8000
const char* DEVICE_ID = "m5stack-display-001";            // そのまま
const char* USER_ID = "m5stack_user_001";                 // そのまま
```

### 4. コンパイル・アップロード

#### 手順:
1. **M5STACKをUSB接続**
2. **ポート選択**: Tools -> Port -> (M5STACKのポート)
3. **コンパイル**: Verify/Compile (✓ボタン)
4. **アップロード**: Upload (→ボタン)

### 5. 動作確認

#### 起動後の表示確認:
```
┌─────────────────────────────┐
│ 🎨 AI Dynamic Painting 🟢   │  ← WiFi接続成功で🟢
├─────────────────────────────┤
│                             │
│  🤖 AI STATUS              │
│                             │
│  Generation: 🟢 ACTIVE      │  ← AI生成状況
│  Progress: 0% ▒▒▒▒▒▒▒▒▒▒  │  ← 進捗バー
│  Task: Waiting...          │  ← 現在のタスク
│                             │
│  Total Generated: 0         │  ← 総生成数
│  Last: --:--               │  ← 最終生成時刻
│                             │
│  Status: 🟢AI 🟢Learning 🟢API│  ← システム状況
│                             │
├─────────────────────────────┤
│ A:Prev   B:Refresh   C:Next │  ← ボタン操作
└─────────────────────────────┘
```

## 🎯 本番環境での主な機能

### Page 1: AI Status (AI生成状況)
- **リアルタイム生成状況表示**
- **進捗パーセンテージ**
- **現在のタスク内容**
- **累計生成数**
- **最終生成時刻**

### Page 2: Learning (学習進捗)
- **総インタラクション数**
- **学習済み嗜好数**
- **信頼度スコア (%)** 
- **学習モード表示**
- **最新フィードバック**

### Page 3: Recommendations (推薦)
- **次の推薦コンテンツ**
- **推薦理由**
- **信頼度**
- **代替案リスト**
- **コンテキスト情報**

## 🔄 ボタン操作

- **Button A**: 前のページへ
- **Button B**: データ更新 (手動リフレッシュ)
- **Button C**: 次のページへ

## 🛠️ トラブルシューティング

### WiFi接続失敗時
```cpp
// シリアルモニターで確認
Tools -> Serial Monitor (115200 baud)

// 表示例:
Connecting to WiFi...
WiFi connected!
IP address: 192.168.10.XXX
```

### API接続失敗時
1. Raspberry PiでBackend起動確認:
```bash
curl http://192.168.10.7:8000/api/ai/status
```

2. M5STACKとRaspberry Piが同じネットワーク上にあるか確認

### 表示が更新されない
- UPDATE_INTERVAL = 3000 (3秒間隔)で自動更新
- Button Bで手動更新可能

## 📡 APIエンドポイント

M5STACKが呼び出すAPI:
```
GET http://192.168.10.7:8000/api/ai/status
GET http://192.168.10.7:8000/api/ai/learning-metrics  
GET http://192.168.10.7:8000/api/ai/recommendations
GET http://192.168.10.7:8000/api/system/health
```

## ✅ デプロイ完了確認

### 成功基準:
1. **WiFi接続**: ヘッダーに🟢表示
2. **API接続**: Status行に🟢API表示
3. **データ更新**: 3秒ごとに自動更新
4. **ページ切替**: A/Cボタンで3画面切替
5. **AI状況表示**: Backend連動でリアルタイム表示

## 🎉 デプロイ完了！

M5STACKがAI動的絵画システムの状況をリアルタイムで表示するようになりました！

---

**注意事項**:
- WiFi設定は環境に合わせて必ず変更してください
- Raspberry PiのIPアドレスを正しく設定してください
- 初回起動時はAPI接続まで少し時間がかかる場合があります