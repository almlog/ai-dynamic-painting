# M5STACK Core2 デプロイメントガイド

## 🚀 Phase 1 AI動的絵画システム - M5STACKセットアップ

このガイドでは、M5STACK Core2に AI動的絵画システムのコントローラーファームウェアをデプロイする方法を説明します。

## 📋 必要なもの

### ハードウェア
- M5STACK Core2 (M5Stack Core2 ESP32 IoT Development Kit)
- USB-C ケーブル
- WiFi環境
- Raspberry Pi (APIサーバー稼働中)

### ソフトウェア
- Arduino IDE 2.x または PlatformIO
- M5Core2 ライブラリ
- ArduinoJson ライブラリ

## 🔧 セットアップ手順

### 1. Arduino IDE の準備

1. **Arduino IDE 2.x をダウンロード・インストール**
   - https://www.arduino.cc/en/software

2. **ESP32 ボードマネージャーの追加**
   - ファイル → 環境設定
   - 追加ボードマネージャーURL: 
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```

3. **ボードのインストール**
   - ツール → ボード → ボードマネージャー
   - "ESP32" で検索 → "ESP32 by Espressif Systems" をインストール

### 2. 必要ライブラリのインストール

Arduino IDE でライブラリマネージャーを開き、以下をインストール：

```
1. M5Core2 by M5Stack
2. ArduinoJson by Benoit Blanchon
3. WiFi (ESP32標準ライブラリ)
4. HTTPClient (ESP32標準ライブラリ)
```

### 3. ソースコードの準備

**実際のプロジェクトフォルダ**：
```
C:\Users\SYUNPEI\m5stack\
└── AI_Dynamic_Painting\
    └── AI_Dynamic_Painting.ino  ← メインファームウェア
```

**リポジトリ内のソースコード**：
```
m5stack/
├── src/
│   ├── main.ino        ← Arduino IDE用ファイル
│   ├── main.cpp        ← 元のC++ファイル
│   ├── buttons.cpp     ← ボタン処理
│   └── buttons.h       ← ヘッダーファイル
└── docs/
    └── DEPLOYMENT.md   ← このファイル
```

### 4. 設定のカスタマイズ

**AI_Dynamic_Painting.ino の設定項目を変更してください：**

```cpp
// === ここを変更してください ===
const char* WIFI_SSID = "makotaronet";           // WiFi ネットワーク名
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918";   // WiFi パスワード
const char* API_BASE_URL = "http://192.168.10.7:8000"; // Raspberry Pi のIP
// ============================
```

### 5. M5STACK への書き込み

1. **M5STACK Core2 を PC に接続**
   - USB-C ケーブルで接続

2. **ボード設定**
   - ツール → ボード → "M5Stack-Core2"
   - ツール → ポート → 適切なCOMポートを選択

3. **コンパイル・書き込み**
   - ✓ ボタンでコンパイル確認
   - → ボタンで書き込み実行

## 🎮 使用方法

### ボタン操作

M5STACK Core2 の3つのボタン：

| ボタン | 機能 | API 呼び出し |
|--------|------|-------------|
| **A (左)** | 再生/一時停止切り替え | `/api/m5stack/control` (play/pause) |
| **B (中央)** | 停止 | `/api/m5stack/control` (stop) |
| **C (右)** | 次の動画 | `/api/m5stack/control` (next) |

### 画面表示

M5STACKの画面には以下が表示されます：

```
AI Dynamic Painting
System Online
Status: Playing
Video: sample_video.mp4

A: Play/Pause  B: Stop  C: Next
```

## 🔍 トラブルシューティング

### WiFi接続できない

**症状**: "WiFi Connection Failed!" と表示される

**解決方法**:
1. WiFi SSID/パスワードを確認
2. 2.4GHz WiFi を使用していることを確認（5GHzは非対応）
3. WiFiルーターが近くにあることを確認

### API通信エラー

**症状**: "Error: HTTP 404" や "Command sent successfully" が表示されない

**解決方法**:
1. Raspberry Pi のIPアドレスを確認
2. Raspberry Pi のAPI サーバーが起動していることを確認
   ```bash
   # Raspberry Pi で確認
   curl http://localhost:8000/api/system/health
   ```
3. ネットワーク接続を確認

### ボタンが反応しない

**症状**: ボタンを押しても何も起こらない

**解決方法**:
1. M5STACK Core2 の電源を確認
2. ファームウェアの再書き込み
3. シリアルモニターでログを確認

## 🛠️ 開発・デバッグ

### シリアルモニター

Arduino IDE でシリアルモニターを開くと、詳細なログが確認できます：

```
=== AI Dynamic Painting M5STACK ===
Connecting to WiFi...
WiFi Connected!
IP: 192.168.1.151
API: http://192.168.1.100:8000
Button A pressed: Sending play command
Command sent successfully
```

### API レスポンステスト

以下の curl コマンドでAPI動作を確認できます：

```bash
# システム状態確認
curl http://192.168.1.100:8000/api/display/status

# M5STACK制御確認  
curl -X POST http://192.168.1.100:8000/api/m5stack/control \
  -H "Content-Type: application/json" \
  -d '{"action":"play"}'
```

## 📊 性能要件

Phase 1 では以下の性能要件を満たします：

- **ボタン応答時間**: < 1秒
- **API通信**: < 1秒
- **WiFi接続安定性**: 24時間連続動作
- **メモリ使用量**: ESP32の制限内

## 🎯 Phase 1 完了チェックリスト

M5STACK 関連のタスク完了確認：

- [ ] WiFi接続成功（SSID表示）
- [ ] API サーバー通信確認（Status: Online）
- [ ] ボタンA: 再生/一時停止動作
- [ ] ボタンB: 停止動作
- [ ] ボタンC: 次の動画動作
- [ ] 画面表示正常（ステータス・動画名表示）
- [ ] 1時間連続動作テスト
- [ ] エラー時の復旧動作確認

## 🚨 重要な注意事項

1. **WiFi**: 2.4GHz のみ対応（5GHz非対応）
2. **電源**: USB給電または内蔵バッテリー使用
3. **通信**: HTTP通信（HTTPS非対応）
4. **IPアドレス**: 固定IP推奨（DHCP可）

## 🔄 アップデート方法

ファームウェア更新時：

1. 新しいコードをダウンロード
2. WiFi設定を再設定
3. Arduino IDE で再コンパイル・書き込み
4. 動作確認

---

**Phase 1 完了おめでとうございます！** 🎉

これでM5STACK Core2を使って動画システムを制御できるようになりました。問題がある場合は、シリアルモニターのログを確認してください。