# Implementation Plan: Phase 1 手動動画管理システム

**Branch**: `001-phase-1-web` | **Date**: 2025-09-11 | **Spec**: [../spec.md](./spec.md)
**Input**: Feature specification from `/home/aipainting/ai-dynamic-painting/specs/001-phase-1-web/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✅
   → Spec loaded successfully
2. Fill Technical Context (scan for NEEDS CLARIFICATION) ✅
   → Detected Project Type: web (frontend + backend)
   → Set Structure Decision to Option 2: Web application
3. Evaluate Constitution Check section below ✅
   → No violations exist
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md 🔄
   → NEEDS CLARIFICATION detected - resolving now
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md
6. Re-evaluate Constitution Check section
7. Plan Phase 2 → Describe task generation approach
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Phase 1では、ユーザーが手動で動画をアップロード・管理し、Web UIとM5STACKで動画を表示・制御できるシステムを構築する。24時間安定稼働を前提とした基盤システムの実装。

## Technical Context
**Language/Version**: Python 3.11+ (backend), HTML/CSS/JavaScript (frontend)
**Primary Dependencies**: FastAPI (backend), React/Vue.js (frontend), SQLite (database)
**Storage**: ファイルシステム（動画ファイル）+ SQLite（メタデータ）
**Testing**: pytest (backend), Jest (frontend), Playwright (E2E)
**Target Platform**: Raspberry Pi (Linux ARM64) + PC/スマホブラウザ
**Project Type**: web - determines source structure (backend/ + frontend/)
**Performance Goals**: 24時間安定稼働, Web UI応答時間 < 3秒, M5STACK応答時間 < 1秒
**Constraints**: Raspberry Pi 4/5のリソース制限, 100MB+の動画ファイル対応
**Scale/Scope**: 個人利用（1ユーザー）, 数百本の動画管理, 24時間稼働

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 2 (backend, frontend) (max 3 ✅)
- Using framework directly? (FastAPI, React - no wrappers ✅)
- Single data model? (Video, DisplaySession, UserDevice, SystemStatus ✅)
- Avoiding patterns? (直接DB access, no Repository/UoW ✅)

**Architecture**:
- EVERY feature as library? (core modules as libraries ✅)
- Libraries listed: [video-manager, display-controller, m5stack-interface, web-api]
- CLI per library: [--help/--version/--format supported ✅]
- Library docs: llms.txt format planned ✅

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? (Yes - TDD mandatory ✅)
- Git commits show tests before implementation? (Yes ✅)
- Order: Contract→Integration→E2E→Unit strictly followed? (Yes ✅)
- Real dependencies used? (実際のRaspberry Pi, M5STACK, database ✅)
- Integration tests for: new libraries, contract changes, shared schemas? (Yes ✅)
- FORBIDDEN: Implementation before test ✅

**Observability**:
- Structured logging included? (JSON logging with levels ✅)
- Frontend logs → backend? (unified stream ✅)
- Error context sufficient? (stack traces, context data ✅)

**Versioning**:
- Version number assigned? (1.0.0 ✅)
- BUILD increments on every change? (Yes ✅)
- Breaking changes handled? (parallel tests, migration plan ✅)

## Project Structure

### Documentation (this feature)
```
specs/001-phase-1-web/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command) 
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 2: Web application (frontend + backend detected)
backend/
├── src/
│   ├── models/          # Video, DisplaySession, UserDevice, SystemStatus
│   ├── services/        # video_manager, display_controller, m5stack_interface
│   ├── api/             # FastAPI routes
│   └── lib/             # Core libraries
└── tests/
    ├── contract/        # API contract tests
    ├── integration/     # Hardware integration tests  
    └── unit/            # Unit tests

frontend/
├── src/
│   ├── components/      # Video upload, player, management UI
│   ├── pages/           # Main dashboard, settings
│   └── services/        # API client, state management
└── tests/
    ├── e2e/             # Playwright E2E tests
    └── unit/            # Jest unit tests

m5stack/                 # M5STACK firmware
├── src/
└── tests/

hardware/               # Hardware integration scripts
├── scripts/
└── tests/
```

**Structure Decision**: Option 2 (Web application) - frontend + backend detected from requirements

## Phase 0: Outline & Research

NEEDS CLARIFICATION items from spec:
1. **動画フォーマット対応**: MP4/AVI/MOVIのどれをサポートするか？
2. **ストレージ制限**: 100MB+の動画、具体的な上限は？
3. **同時接続ユーザー数**: 個人使用だが、具体的な制限は？

### Research Tasks:
1. **動画フォーマット調査**: Raspberry Pi上でのMP4/AVI/MOV再生性能比較
2. **ストレージ戦略**: SQLiteファイルサイズ制限とファイルシステム容量管理
3. **Raspberry Pi性能**: 動画再生とWeb UI同時実行時のリソース使用量
4. **M5STACK通信**: WiFi経由でのRaspberry Pi連携ベストプラクティス
5. **24時間稼働**: プロセス監視、自動復旧、ログローテーション戦略
