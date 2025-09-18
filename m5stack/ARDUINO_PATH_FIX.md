# 🚨 Arduino IDE 日本語パス問題の解決方法

## 問題
Arduino IDEは日本語を含むパスでエラーが発生します：
- ❌ `C:\Users\SYUNPEI\OneDrive\デスクトップ\AI-Dynamic-Painting`
- ❌ 「デスクトップ」という日本語が問題

## 解決方法

### 📁 方法1: 英語パスにプロジェクトをコピー（推奨）

1. **新しいフォルダを作成**（日本語を含まない場所）：
   ```
   C:\Users\SYUNPEI\m5stack\   ← 実際に使用するパス
   C:\M5STACK\
   C:\Arduino\AI-Dynamic-Painting\
   D:\Development\M5STACK\
   ```

2. **必要なファイルをコピー**：
   - `main.ino` (このリポジトリのm5stack/src/main.ino)
   - `C:\Users\SYUNPEI\m5stack\AI_Dynamic_Painting\AI_Dynamic_Painting.ino` として保存
   - WiFi設定を変更してコピー

### 📝 方法2: スケッチフォルダ設定を変更

1. **Arduino IDE の設定**:
   - ファイル → 環境設定
   - スケッチブックの保存場所: `C:\Arduino`（英語パスに変更）

2. **新規スケッチ作成**:
   - ファイル → 新規
   - 名前を付けて保存: `M5STACK_Controller`
   - main.inoの内容をコピペ

### 🎯 最速セットアップ手順

1. **ユーザーフォルダにプロジェクト作成**:
   ```batch
   mkdir C:\Users\SYUNPEI\m5stack\AI_Dynamic_Painting
   cd C:\Users\SYUNPEI\m5stack\AI_Dynamic_Painting
   ```

2. **Arduino IDEで新規スケッチ**:
   - ファイル → 新規
   - 以下の場所に保存: `C:\Users\SYUNPEI\m5stack\AI_Dynamic_Painting\AI_Dynamic_Painting.ino`

3. **main.inoの内容をコピペ**:
   - WiFi設定を変更（makotaronet, 192.168.10.7）
   - コンパイル → 書き込み

## ✅ 動作確認

**パスに日本語が含まれていないか確認**:
```
C:\M5STACK\M5STACK_Controller\M5STACK_Controller.ino  ✅ OK
C:\Users\SYUNPEI\Desktop\project\main.ino             ✅ OK（英語のみ）
C:\Users\SYUNPEI\デスクトップ\project\main.ino        ❌ NG（日本語あり）
```

## 🔍 エラーが出た場合

**よくあるエラー**:
- `fork/exec ... : The system cannot find the file specified.`
- `Error compiling for board M5Stack-Core2`
- `Invalid argument`

これらはすべて**日本語パス**が原因です。英語パスに移動すれば解決します！

## 📊 推奨フォルダ構成

```
C:\M5STACK\                          ← 英語パス（推奨）
├── M5STACK_Controller\
│   └── M5STACK_Controller.ino       ← Arduino IDE用
├── libraries\                       ← 追加ライブラリ
└── README.txt                       ← メモ用
```

---

**注意**: OneDriveのフォルダも避けた方が安全です（同期の問題があることがあります）