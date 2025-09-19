# Spec: API統合実動作確認

**目的**: Phase 2完成システムの実際のAPI統合動作確認とエンドツーエンドテスト

## 📋 Phase 3.1: API キー設定確認

### 機能要件
- **FR-API-001**: システムMUST 必要なAPI キーが正しく設定されていることを確認する
- **FR-API-002**: システムMUST 各APIへの接続テストが成功することを検証する  
- **FR-API-003**: システムMUST API利用制限・コスト監視が動作することを確認する

### 設定対象API
1. **VEO API (動画生成)**:
   - Google VEO-2 API Key
   - Project ID, Location設定
   - 月次予算・制限設定

2. **Gemini API (AI処理)**:
   - GEMINI_API_KEY
   - プロンプト生成・品質評価
   
3. **Weather API**:
   - OpenWeatherMap API Key
   - 環境連動機能

4. **Claude API (Optional)**:
   - ANTHROPIC_API_KEY
   - AI支援機能

### 確認シナリオ
```gherkin
Scenario: API キー設定確認
  Given API キーが.envファイルに設定されている
  When システムが起動される
  Then 各APIへの接続テストが成功する
  And API利用制限が正しく認識される
  And コスト監視機能が動作する

Scenario: VEO API動画生成テスト
  Given VEO APIキーが設定されている
  When 簡単なプロンプトで動画生成を実行する
  Then 動画生成が成功する
  And 生成コストが記録される
  And 品質評価が実行される

Scenario: 環境連動プロンプト生成
  Given Weather APIキーが設定されている
  And Gemini APIキーが設定されている
  When 現在の天気情報を取得する
  Then 天気連動プロンプトが生成される
  And VEO APIで動画生成される
  And M5STACKに結果が表示される
```

## 📋 Phase 3.2: エンドツーエンド動作確認

### 機能要件
- **FR-E2E-001**: システムMUST センサー入力からAI動画生成まで完全自動で動作する
- **FR-E2E-002**: システムMUST M5STACKボタン操作で学習・評価機能が動作する
- **FR-E2E-003**: システムMUST Web UIからAI生成状況の監視・制御ができる

### テストシナリオ
```gherkin
Scenario: 完全自動化フロー
  Given 全APIキーが設定済み
  And システムが24時間稼働中
  When 定期スケジュールが実行される
  Then 天気データが自動取得される
  And AI動画が自動生成される  
  And 生成動画が自動表示される
  And 学習データが蓄積される

Scenario: M5STACKフィードバック学習
  Given AI生成動画が表示中
  When M5STACKでGood/Bad/Skipボタンが押される
  Then ユーザー嗜好が学習される
  And 次回生成に反映される
  And 学習進捗がWeb UIで確認できる

Scenario: コスト管理・アラート
  Given 月次予算が設定済み
  When API使用量が80%に達する
  Then アラートが発生する
  And 生成頻度が自動調整される  
  And 予算超過が防止される
```

## 🎯 成功基準

### Phase 3.1 完了基準
- [ ] 全API接続テスト成功
- [ ] VEO API動画生成1本成功
- [ ] Weather API天気取得成功
- [ ] Gemini APIプロンプト生成成功
- [ ] コスト監視機能動作確認

### Phase 3.2 完了基準  
- [ ] センサー→AI→表示の完全自動フロー動作
- [ ] M5STACKフィードバック学習動作
- [ ] 24時間自動稼働確認
- [ ] Web UI監視機能確認
- [ ] コスト管理・アラート動作確認

## 🔧 技術実装仕様

### API設定ファイル構造
```bash
backend/.env:
├── VEO_API_KEY=your_veo_api_key
├── GEMINI_API_KEY=your_gemini_api_key  
├── WEATHER_API_KEY=your_weather_api_key
├── ANTHROPIC_API_KEY=your_claude_api_key
└── MAX_MONTHLY_API_COST_USD=50
```

### テスト実行コマンド
```bash
# API接続テスト
python -m pytest tests/integration/test_api_connections.py -v

# E2E動作確認
python -m pytest tests/integration/test_ai_e2e_sandbox.py -v

# コスト監視テスト  
python -m pytest tests/integration/test_cost_management.py -v

# 24時間稼働テスト
python scripts/24hour_stability_test.py
```

---

**Phase 3.1-3.2完了により、AI動的絵画システムの実用稼働が確認できます**