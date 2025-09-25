# 高品質動画生成フロー構築 - タスクリスト

**ステータス:**
- ❌: 未着手
- 🔄: 作業中
- ✅: 完了

---

### フェーズ1: VEOサービスのImage-to-Video対応

- `✅ T-V001`: `test_veo_service.py` に、画像入力ありの失敗するテスト `test_generate_video_with_image` を作成する (Red Phase)。
  - `✅ T-V002`: `veo_client.py` の `generate_video` メソッドを、画像データを受け取れるように拡張する。
  - `✅ T-V003`: `generate_video` の実装を、画像入力に対応させる (Green Phase)。
  - `✅ T-V004`: `test_veo_service.py` のテストがすべて成功することを確認する。

### フェーズ2: 統合オーケストレーションサービスの構築

- `🔄 T-V005`: `services` に `master_generation_service.py` を新規作成する。
- `🔄 T-V006`: `tests/services` に `test_master_generation_service.py` を作成し、静止画から動画までの一連のフローを検証する失敗するテストを記述する (Red Phase)。
- `❌ T-V007`: `MasterGenerationService` に、`GeminiService` と `VEOGenerationService` を順に呼び出す `create_masterpiece_flow` メソッドを実装する (Green Phase)。
- `❌ T-V008`: `test_master_generation_service.py` のテストが成功することを確認する。

### フェーズ3: APIエンドポイントの接続

- `❌ T-V009`: `ai_generation.py` の `/generate` エンドポイントが、新しい `MasterGenerationService` を呼び出すように修正する。
- `❌ T-V010`: 上記変更に伴うAPIの統合テストを作成し、失敗することを確認する (Red Phase)。
- `❌ T-V011`: 統合テストが成功するように修正する (Green Phase)。

### フェーズ4: 最終化

- `❌ T-V012`: 関連コード全体のリファクタリングと最終的な動作確認を行う。
- `❌ T-V013`: `GEMINI_DEV_LOG.md` と `TASK_LIST_VIDEO_GENERATION.md` を更新し、全タスクに `✅` を付ける。
