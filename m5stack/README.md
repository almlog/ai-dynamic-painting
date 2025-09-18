# M5STACK Core2 - AI動的絵画システム

Phase 1 手動動画管理システム用のM5STACKコントローラーファームウェア

## 📁 ディレクトリ構成

```
m5stack/
├── README.md           ← このファイル
├── QUICKSTART.md       ← 1分で動かすガイド ⚡
├── src/
│   ├── main.cpp        ← メインファームウェア (T050)
│   ├── buttons.cpp     ← ボタン処理 (T051) 
│   └── buttons.h       ← ヘッダーファイル
├── docs/
│   └── DEPLOYMENT.md   ← 詳細デプロイガイド
├── examples/           ← サンプルコード (将来使用)
└── libraries/          ← カスタムライブラリ (将来使用)
```

## ⚡ クイックスタート

**すぐに動かしたい場合**: `QUICKSTART.md` を見てください

**詳細な設定が必要**: `docs/DEPLOYMENT.md` を参照

## 🎮 機能

- **WiFi接続**: Raspberry Pi API との通信
- **ボタン制御**: 3つのボタンで動画操作
  - A: 再生/一時停止
  - B: 停止
  - C: 次の動画
- **画面表示**: システム状態とボタンガイド
- **高度なボタン処理**: デバウンス、長押し、ダブルクリック対応

## 🔧 必要な設定

main.cpp の以下の部分を変更：

```cpp
const char* WIFI_SSID = "your_wifi_ssid";        // WiFi名
const char* WIFI_PASSWORD = "your_wifi_password"; // WiFiパスワード
const char* API_BASE_URL = "http://192.168.1.100:8000"; // Raspberry Pi IP
```

## 📊 Phase 1 実装状況

- ✅ T050: Basic communication (main.cpp)
- ✅ T051: Button handling (buttons.cpp/.h)
- ✅ デプロイメントガイド作成
- ✅ クイックスタートガイド作成

## 🚀 次のステップ

1. `QUICKSTART.md` でセットアップ
2. M5STACKに書き込み
3. Raspberry Pi と通信テスト
4. 動画制御の動作確認

---

**Phase 1 M5STACK実装完了！** 🎉