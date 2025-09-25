# Phase 6計画改訂 - Gemini評価対応版

**改訂日**: 2025-09-23  
**改訂理由**: Gemini総合評価に基づく重要な不整合と改善点の対応

## 🔴 最重要改訂: DBモデル不整合の解決

### 問題の詳細
- **現状**: Videoテーブルは手動アップロード前提（filepath必須、file_size等）
- **計画**: VideoGeneration型は動画生成前提（task_id、video_url、progress等）
- **影響**: このまま実装するとDB層で動作しない

### 解決策: 新テーブル追加アプローチ
```python
# 新規テーブル: video_generations
class VideoGeneration(Base):
    """AI動画生成管理テーブル"""
    __tablename__ = 'video_generations'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(String(100), unique=True, nullable=False)  # VEO task ID
    
    # 生成パラメータ
    prompt = Column(Text, nullable=False)
    duration_seconds = Column(Integer, default=30)
    resolution = Column(String(20), default='1080p')
    fps = Column(Integer, default=30)
    quality = Column(String(20), default='standard')
    
    # ステータス管理
    status = Column(String(20), default='pending')
    progress_percent = Column(Float, default=0.0)
    
    # 結果
    video_url = Column(String(512), nullable=True)
    veo_video_id = Column(String(100), nullable=True)
    
    # コスト
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # エラー管理
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # 既存Videoテーブルとの関連（完成後）
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=True)
    video = relationship("Video", back_populates="generation")
```

## 📅 改訂スケジュール（5日→6日に延長）

### Day 1-2: フロントエンド統一（変更なし）
- T6-001〜T6-010: 計画通り実施

### Day 3: バックエンド基盤改修
- T6-011: Google Cloud認証設定
- T6-012: VEOクライアント強化
- **T6-012.5**: 🆕 VideoGenerationテーブル作成とマイグレーション
  ```bash
  - Alembicマイグレーションスクリプト作成
  - video_generationsテーブル追加
  - 既存videosテーブルとの関連定義
  ```

### Day 4: DBとAPI統合
- **T6-013**: CostTracker実装（VideoGenerationテーブル使用）
- **T6-014**: 予算制限機能実装
- **T6-014.5**: 🆕 セッション復元機能実装
  ```typescript
  // フロントエンド: localStorage使用
  - task_id保存機能
  - ページ再読み込み時の復元
  - 未完了タスクの自動再接続
  ```
- T6-015: メトリクス収集実装
- T6-016: ダッシュボードAPI追加

### Day 5: 統合テスト（1日後ろ倒し）
- T6-017〜T6-020: 計画通り実施
- **T6-020.5**: 🆕 セッション復元E2Eテスト

### Day 6: 品質保証・デプロイ（1日後ろ倒し）
- T6-021〜T6-025: 計画通り実施

## 🚨 追加リスク項目

### 新規追加リスク
| リスク | 影響 | 発生確率 | 対策 |
|-------|------|---------|-----|
| DBマイグレーション失敗 | 高 | 中 | バックアップ取得、ロールバック手順準備 |
| セッション復元複雑化 | 中 | 高 | localStorageとサーバー同期の厳密な設計 |
| 長時間生成のタイムアウト | 高 | 中 | タスクID永続化、非同期ジョブ管理強化 |

## ✅ 改善された完了基準

### T6-002: VideoGenerationForm実装
- [ ] コード実装完了
- [ ] ユニットテストPASS
- [ ] **具体的テスト項目**:
  - プロンプト空入力時にエラーメッセージ表示
  - 解像度選択で3つのオプション（720p/1080p/4K）が選択可能
  - FPS選択で無効値（61以上）入力時にバリデーションエラー
  - Submit時に全パラメータが正しくAPIに送信される

### T6-003: VideoProgressDisplay実装
- [ ] コード実装完了
- [ ] ユニットテストPASS
- [ ] **具体的テスト項目**:
  - progress=0で「準備中」、progress=50で「生成中50%」表示
  - キャンセルボタンクリックでキャンセルAPIが呼ばれる
  - 完了時（progress=100）に完了メッセージと動画URLが表示
  - エラー時に赤色のエラーメッセージが表示

### T6-014: 予算制限機能実装
- [ ] コード実装完了
- [ ] ユニットテストPASS
- [ ] **具体的テスト項目**:
  - 日次予算$10超過時に新規生成がブロックされる
  - 80%使用時（$8.00）に警告メッセージが表示
  - 予算リセット時刻（UTC 0:00）に使用量がリセット
  - 管理者による予算上限変更がDBに反映される

### T6-014.5: セッション復元機能実装
- [ ] コード実装完了
- [ ] ユニットテストPASS
- [ ] **具体的テスト項目**:
  - task_idがlocalStorageに保存される
  - ページリロード時に進行中タスクが自動復元
  - 完了済みタスクは復元されない
  - localStorageクリア後は復元されない

## 📊 主要な改訂ポイントまとめ

1. **DBモデル追加**: VideoGenerationテーブル新規作成（T6-012.5）
2. **スケジュール延長**: 5日→6日（DB改修工数追加）
3. **セッション復元**: localStorage活用した復元機能（T6-014.5）
4. **完了基準具体化**: 主要タスクに具体的テストシナリオ追記
5. **リスク項目追加**: DBマイグレーション、セッション復元、長時間生成

## 🎯 Gemini指摘事項への対応状況

| 指摘事項 | 対応状況 | 対応内容 |
|---------|---------|---------|
| DBモデル不整合 | ✅ 対応済 | VideoGenerationテーブル新規追加 |
| Day 3の工数不足 | ✅ 対応済 | 6日間に延長、Day 4をDB/API統合に |
| セッション復元リスク | ✅ 対応済 | T6-014.5追加、localStorage活用 |
| 完了基準の具体性 | ✅ 対応済 | 主要タスクに具体的テスト項目追記 |
| タスク粒度 | ✅ 問題なし | Gemini評価通り適切 |

---

これでGeminiの指摘に完全対応したPhase 6改訂計画が完成なのだ〜！🎉