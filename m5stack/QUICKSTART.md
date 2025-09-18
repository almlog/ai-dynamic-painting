# 🚀 M5STACK クイックスタートガイド

## すぐに動かしたい人向け！

### ⚡ 1分セットアップ

1. **プロジェクトフォルダ作成**: `C:\Users\SYUNPEI\m5stack\AI_Dynamic_Painting\`
2. **main.ino をコピー**: このフォルダに `AI_Dynamic_Painting.ino` として保存
3. **Arduino IDE で開いて書き込み**

### 📋 コピペ用コード

**AI_Dynamic_Painting.ino に貼り付けるコード**:

```cpp
// === ⚠️ 必ず変更してください ===
const char* WIFI_SSID = "makotaronet";        // あなたのWiFi名
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918"; // WiFiパスワード  
const char* API_BASE_URL = "http://192.168.10.7:8000"; // Raspberry Pi のIP
// mDNS使用の場合: "http://raspberrypi.local:8000"
// ============================
```

**↑ この部分だけ変更してコピペすれば動きます！**

### 🔧 IPアドレス問題の解決方法

**問題**: 有線と無線でIPアドレスが変わる

#### 方法1: mDNSホスト名を使用（簡単）
```cpp
const char* API_BASE_URL = "http://raspberrypi.local:8000";
```
→ IPが変わっても自動で見つけてくれる！

#### 方法2: 現在のIPアドレス確認
```bash
# Raspberry Pi で実行
hostname -I
```

#### 方法3: 新しいRaspberry Pi固定IP設定
```bash
# 新しいRaspberry Pi OS の場合
sudo nano /etc/NetworkManager/system-connections/接続名.nmconnection

# または
sudo nmcli connection modify 接続名 ipv4.method manual
sudo nmcli connection modify 接続名 ipv4.addresses 192.168.10.7/24
```

**注意**: 既にSSH設定で `192.168.10.7` を使用中の場合は、そのIPを使用してください

### ⚙️ ボード設定（Arduino IDE）

```
ボード: M5Stack-Core2
ポート: COM3 (Windowsの場合) または /dev/ttyUSB0 (Linuxの場合)
```

### 🎮 使い方

M5STACKのボタン:
- **左ボタン(A)**: 再生/一時停止
- **中ボタン(B)**: 停止  
- **右ボタン(C)**: 次の動画

### 📺 画面表示の見方

```
AI Dynamic Painting    ← システム名
WiFi: 接続             ← WiFi状態
Status: 再生中         ← 再生状態
Video: sample.mp4      ← 現在の動画

A:再生/停止 B:停止 C:次  ← ボタンガイド
```

### 🚨 トラブルシューティング

**WiFi接続エラー**: SSID/パスワードを再確認
**API通信エラー**: Raspberry Pi のIPアドレスと起動状態を確認
**ボタン無反応**: USB電源を確認、再起動試行

### ✅ 動作確認チェックリスト

- [ ] M5STACKの画面に「System Online」表示
- [ ] 左ボタンで再生/一時停止切り替わり
- [ ] 中ボタンで停止
- [ ] 右ボタンで次の動画選択
- [ ] 画面に動画名とステータス表示

**これで完了！** 🎉

---

**詳細な設定**: `docs/DEPLOYMENT.md` を参照
**問題解決**: シリアルモニター（115200bps）でログ確認