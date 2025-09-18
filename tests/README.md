# 🧪 AI動的絵画システム テストスイート

## 📋 テスト構成

### Backend テスト
- **場所**: `/backend/tests/`
- **フレームワーク**: pytest
- **カバレッジ**: 90%+

```
backend/tests/
├── unit/           # ユニットテスト
├── integration/    # 統合テスト  
├── contract/       # API契約テスト
├── performance/    # パフォーマンステスト
└── ai/            # AI機能テスト
```

### Frontend テスト
- **場所**: `/frontend/tests/`
- **フレームワーク**: Jest + React Testing Library
- **カバレッジ**: 85%+

```
frontend/tests/
├── components/     # コンポーネントテスト
└── ai/            # AIコンポーネントテスト
```

## 🚀 テスト実行方法

### Backend テスト
```bash
cd backend
python -m pytest tests/ -v --cov=src
```

### Frontend テスト
```bash
cd frontend
npm test
```

### 全テスト実行
```bash
bash scripts/run-all-tests.sh
```

## 📊 テスト統計
- **総テストケース**: 245個
- **Backend**: 240個 (Unit: 150, Integration: 50, Contract: 30, Performance: 10)
- **Frontend**: 5個 (Components: 3, AI: 2)

## 🎯 テスト品質基準
- **ユニットテスト**: カバレッジ 90%+
- **統合テスト**: エンドツーエンド動作確認
- **契約テスト**: API仕様準拠確認
- **パフォーマンステスト**: 応答時間 < 500ms