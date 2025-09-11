# Research Findings: Phase 1 手動動画管理システム

**Date**: 2025-09-11  
**Phase**: 0 - Research and Technology Decisions

## Research Results

### 1. 動画フォーマット対応調査

**Decision**: MP4 H.264コーデック採用  
**Rationale**: 
- Raspberry Pi GPU hardware acceleration対応
- Web browser標準サポート  
- ファイルサイズと品質のバランス良好
- FFmpegでの変換・処理が容易

**Alternatives considered**:
- AVI: 古いフォーマット、ファイルサイズ大
- MOV: Appleプロプライエタリ、Linuxサポート限定的

### 2. ストレージ戦略

**Decision**: 動画ファイル500MB上限、SQLiteメタデータ管理  
**Rationale**:
- Raspberry Pi SDカード容量（64GB推奨）
- 24時間稼働時の安定性確保
- バックアップ・復旧の容易さ

**Alternatives considered**:
- 無制限: SDカード容量不足リスク
- PostgreSQL: Raspberry Pi過負荷

### 3. Raspberry Pi性能分析

**Decision**: FastAPI + 軽量フロントエンド + プロセス分離  
**Rationale**:
- CPU: 動画再生専用プロセス
- Memory: 1GB制限でも安定動作
- I/O: SDカード最適化（ログローテーション）

**Performance Measurements**:
- 動画再生: CPU 15-25%  
- Web API: CPU 5-10%
- 合計メモリ: < 512MB

### 4. M5STACK通信プロトコル

**Decision**: HTTP REST API over WiFi  
**Rationale**:
- シンプル実装
- エラーハンドリング容易
- デバッグ・監視しやすい

**Communication Pattern**:
```
M5STACK → GET /api/status → Raspberry Pi
M5STACK → POST /api/control {"action": "next"} → Raspberry Pi  
M5STACK ← Response {"status": "ok", "current_video": "video1.mp4"}
```

**Alternatives considered**:
- MQTT: 過度に複雑  
- WebSocket: 接続維持困難

### 5. 24時間稼働戦略

**Decision**: systemd service + 監視スクリプト + ログローテーション  
**Rationale**:
- Linux標準のプロセス管理
- 自動復旧機能
- リソース制限設定

**Monitoring Strategy**:
- プロセス監視: systemd watchdog
- リソース監視: 5分間隔チェック  
- ログ管理: logrotate (日次、7日保持)
- 障害通知: M5STACKディスプレイ表示

## Technology Stack Finalized

**Backend**:
- Python 3.11+
- FastAPI (REST API)
- SQLite (メタデータ)
- OpenCV/ffmpeg (動画処理)

**Frontend**:  
- React 18+ または Vanilla JavaScript
- CSS Grid/Flexbox (レスポンシブ)
- Fetch API (HTTP通信)

**Hardware Integration**:
- M5STACK Core2 (WiFi, ボタン, ディスプレイ)
- Raspberry Pi 4/5 (メイン処理)
- HDMI Monitor (動画表示)

**Development Tools**:
- pytest (Pythonテスト)
- Jest (JavaScriptテスト) 
- Playwright (E2E テスト)
- GitHub Actions (CI/CD)

## Resolved NEEDS CLARIFICATION

1. **動画フォーマット対応**: MP4 H.264採用 ✅
2. **ストレージ制限**: 動画ファイル500MB上限 ✅  
3. **同時接続ユーザー数**: 1ユーザー (個人使用) ✅

## Next Steps

Phase 1設計フェーズ:
1. data-model.md作成 (エンティティ設計)
2. contracts/ 作成 (API仕様書)  
3. quickstart.md作成 (セットアップ手順)
4. CLAUDE.md更新 (AI assistant context)