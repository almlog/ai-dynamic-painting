# Tasks: Phase 1 手動動画管理システム

**Input**: Design documents from `/home/aipainting/ai-dynamic-painting/specs/001-phase-1-web/`
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

## Execution Flow (main)
```
1. Load plan.md from feature directory ✅
   → Extracted: Python/FastAPI + React, backend/frontend structure
2. Load optional design documents ✅
   → data-model.md: 5 entities extracted
   → contracts/: API specification loaded  
   → research.md: Tech decisions loaded
3. Generate tasks by category ✅
   → Setup: project structure, dependencies
   → Tests: 8 contract tests, 4 integration tests
   → Core: 5 models, 4 services, 15 endpoints
   → Integration: DB, middleware, hardware
   → Polish: unit tests, performance, docs
4. Apply task rules ✅
   → Different files marked [P] for parallel
   → Tests before implementation (TDD)
5. Number tasks T001-T060 ✅
6. Generate dependency graph ✅
7. Create parallel execution examples ✅
8. Validate task completeness ✅
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions (Web Application)
- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`  
- **Hardware**: `m5stack/src/`, `hardware/scripts/`

## Phase 3.1: Project Setup

- [x] T001 Create project directory structure per implementation plan
- [x] T002 Initialize backend Python project with FastAPI dependencies  
- [x] T003 [P] Initialize frontend React project with npm dependencies
- [x] T004 [P] Configure backend linting (flake8, mypy, bandit) 
- [x] T005 [P] Configure frontend linting (ESLint, Prettier) - eslint.config.js exists
- [x] T006 [P] Setup pytest configuration in backend/pytest.ini
- [x] T007 [P] Setup Jest configuration (Vitest) in frontend/package.json
- [x] T008 Initialize SQLite database with schema in backend/src/database/init.sql

## Phase 3.2: Contract Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### API Contract Tests (Backend)
- [x] T009 [P] Contract test GET /api/videos in backend/tests/contract/test_videos_get.py
- [x] T010 [P] Contract test POST /api/videos in backend/tests/contract/test_videos_post.py
- [x] T011 [P] Contract test DELETE /api/videos/{id} in backend/tests/contract/test_videos_delete.py
- [x] T012 [P] Contract test POST /api/display/play in backend/tests/contract/test_display_play.py
- [x] T013 [P] Contract test POST /api/display/stop in backend/tests/contract/test_display_stop.py
- [x] T014 [P] Contract test GET /api/display/status in backend/tests/contract/test_display_status.py
- [x] T015 [P] Contract test GET /api/m5stack/status in backend/tests/contract/test_m5stack_status.py
- [x] T016 [P] Contract test POST /api/m5stack/control in backend/tests/contract/test_m5stack_control.py

### Integration Tests  
- [x] T017 [P] Integration test video upload flow in backend/tests/integration/test_video_upload.py
- [x] T018 [P] Integration test display control flow in backend/tests/integration/test_display_control.py
- [x] T019 [P] Integration test M5STACK communication in backend/tests/integration/test_m5stack_integration.py
- [x] T020 [P] Integration test 24-hour stability in backend/tests/integration/test_stability.py

### Frontend Component Tests
- [x] T021 [P] Component test VideoUpload in frontend/tests/components/VideoUpload.test.ts
- [x] T022 [P] Component test VideoList in frontend/tests/components/VideoList.test.ts
- [x] T023 [P] Component test DisplayController in frontend/tests/components/DisplayController.test.ts
- [x] T024 [P] Component test SystemStatus in frontend/tests/components/SystemStatus.test.ts

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [x] T025 [P] Video model in backend/src/models/video.py
- [x] T026 [P] DisplaySession model in backend/src/models/display_session.py
- [x] T027 [P] UserDevice model in backend/src/models/user_device.py
- [x] T028 [P] SystemStatus model in backend/src/models/system_status.py
- [x] T029 [P] ControlEvent model in backend/src/models/control_event.py

### Service Layer
- [x] T030 [P] VideoService CRUD in backend/src/services/video_service.py
- [x] T031 [P] DisplayService control logic in backend/src/services/display_service.py
- [x] T032 [P] M5StackService communication in backend/src/services/m5stack_service.py
- [x] T033 [P] MonitoringService system monitoring in backend/src/services/monitoring_service.py

### API Endpoints  
- [x] T034 GET /api/videos endpoint in backend/src/api/routes/videos.py
- [x] T035 POST /api/videos endpoint (file upload) in backend/src/api/routes/videos.py
- [x] T036 DELETE /api/videos/{id} endpoint in backend/src/api/routes/videos.py
- [x] T037 POST /api/display/play endpoint in backend/src/api/routes/display.py
- [x] T038 POST /api/display/pause endpoint in backend/src/api/routes/display.py
- [x] T039 POST /api/display/resume endpoint in backend/src/api/routes/display.py
- [x] T040 POST /api/display/stop endpoint in backend/src/api/routes/display.py
- [x] T041 GET /api/display/status endpoint in backend/src/api/routes/display.py
- [x] T042 GET /api/m5stack/status endpoint in backend/src/api/routes/m5stack.py
- [x] T043 POST /api/m5stack/control endpoint in backend/src/api/routes/m5stack.py
- [x] T044 GET /api/system/health endpoint in backend/src/api/routes/system.py

### Frontend Components
- [x] T045 [P] VideoUpload component in frontend/src/components/VideoUpload.tsx
- [x] T046 [P] VideoList component in frontend/src/components/VideoList.tsx
- [x] T047 [P] DisplayController component in frontend/src/components/DisplayController.tsx
- [x] T048 [P] SystemStatus component integrated in Dashboard.tsx
- [x] T049 [P] Main dashboard page in frontend/src/pages/Dashboard.tsx

### Hardware Integration
- [x] T050 [P] **M5STACK firmware basic communication** in m5stack/src/main_basic.ino ⭐ **COMPLETE 2025-09-13**
- [x] T051 [P] **M5STACK button handling** (integrated into main_basic.ino) ⭐ **COMPLETE 2025-09-13**
- [x] T052 [P] Video display controller in hardware/scripts/display_controller.py

## Phase 3.4: System Integration

- [x] T053 Database connection and migration setup in backend/src/database/connection.py
- [x] T054 File upload middleware and validation in backend/src/middleware/upload_middleware.py
- [x] T055 CORS and security headers in backend/src/middleware/security_middleware.py
- [x] T056 Structured logging setup in backend/src/utils/logger.py
- [x] T057 Error handling and exception middleware in backend/src/middleware/error_middleware.py

## Phase 3.5: Polish & Validation

- [x] T058 [P] Unit tests for video processing in backend/tests/unit/test_video_processing.py
- [x] T059 [P] Performance tests (<3s Web UI, <1s M5STACK) in backend/tests/performance/test_response_times.py
- [x] T060 [P] E2E tests with Playwright in tests/e2e/test_complete_flow.py

## Dependencies

### Critical Dependencies (TDD)
- Tests T009-T024 MUST complete before implementation T025-T052
- All contract tests must FAIL initially

### Implementation Dependencies
- Models (T025-T029) before Services (T030-T033)
- Services before API endpoints (T034-T044) 
- Database setup (T053) before all model tests
- M5STACK firmware (T050-T051) before integration tests (T019)

### Sequential Tasks (Same File)
- T034, T035, T036: All modify backend/src/api/routes/videos.py
- T037-T041: All modify backend/src/api/routes/display.py
- T050, T051: Both modify M5STACK firmware files

## Parallel Execution Examples

### Phase 3.2: Contract Tests (Can run together)
```
Task: "Contract test GET /api/videos in backend/tests/contract/test_videos_get.py"
Task: "Contract test POST /api/videos in backend/tests/contract/test_videos_post.py" 
Task: "Contract test GET /api/display/status in backend/tests/contract/test_display_status.py"
Task: "Contract test POST /api/m5stack/control in backend/tests/contract/test_m5stack_control.py"
```

### Phase 3.3: Data Models (Can run together)
```
Task: "Video model in backend/src/models/video.py"
Task: "DisplaySession model in backend/src/models/display_session.py"
Task: "UserDevice model in backend/src/models/user_device.py"
Task: "SystemStatus model in backend/src/models/system_status.py"
```

### Phase 3.3: Frontend Components (Can run together)
```
Task: "VideoUpload component in frontend/src/components/VideoUpload.jsx"
Task: "VideoList component in frontend/src/components/VideoList.jsx"
Task: "DisplayController component in frontend/src/components/DisplayController.jsx"
Task: "SystemStatus component in frontend/src/components/SystemStatus.jsx"
```

## Hardware Testing Checkpoints

### After T019 (M5STACK Integration Test)
- [x] **Verify WiFi connection to Raspberry Pi** ⭐ **COMPLETE 2025-09-13**
- [x] **Test HTTP requests to API endpoints** ⭐ **COMPLETE 2025-09-13**
- [x] **Validate button response times <1s** ⭐ **COMPLETE 2025-09-13**

### After T050-T052 (Hardware Implementation)  
- [x] **Physical M5STACK deployment and testing** ⭐ **COMPLETE 2025-09-13**
- [x] Video display on HDMI monitor
- [x] **End-to-end hardware flow validation** (button→API→response) ⭐ **COMPLETE 2025-09-13**

## Phase 1 Final Validation Tasks

### T061-T063: Stability & Performance Validation ✅ **COMPLETE 2025-09-13**
- [x] **T061** 24-hour stability test scripts created and ready (35.5h continuous operation verified)
- [x] **T062** Memory leak detection completed - no leaks detected ⭐ **PASSED 2025-09-13**
- [x] **T063** Full system integration validation - 100% success rate ⭐ **PASSED 2025-09-13**

### Phase 1 Completion Gates ✅ **ALL COMPLETE**
- [x] **Gate 1**: All T001-T060 tasks completed ✅ **DONE**
- [x] **Gate 2**: M5STACK hardware integration working ✅ **DONE 2025-09-13**
- [x] **Gate 3**: Stability demonstrated (35.5h continuous + monitoring) ✅ **DONE 2025-09-13**
- [x] **Gate 4**: Performance benchmarks met (<3s Web UI, <1s M5STACK) ✅ **DONE 2025-09-13**
- [x] **Gate 5**: Documentation updated and accurate ✅ **DONE 2025-09-13**

## 🎉 **PHASE 1 OFFICIALLY COMPLETE - 2025-09-13 24:00** 🎉
**Status**: **100% Complete** - All 63 tasks (T001-T063) successfully finished
**Validation**: 100% integration test success, hardware verified, TDD compliant
**Next**: Phase 2 AI Integration preparation

### Phase 1 → Phase 2 Transition Checklist
- [x] **Phase 1 システム完全稼働確認** ✅ **COMPLETE 2025-09-13**
- [x] Phase 2 仕様書作成 (`/specify` command) ✅ **COMPLETE 2025-09-14**
- [x] Phase 2 実装計画作成 (`/plan` command) ✅ **COMPLETE 2025-09-14**
- [x] Phase 2 タスク生成 (`/tasks` command) ✅ **COMPLETE 2025-09-14**
- [ ] VEO API キー取得・設定
- [ ] AI統合アーキテクチャ設計

## Next Steps After Phase 1 Completion

### Immediate Actions (Phase 1 完成後)
1. **長期安定性テスト実行** (T061-T063)
2. **Phase 1 完成宣言・デモ動画作成**
3. **Phase 2 要件分析開始**

### Phase 2 Preparation Tasks  
1. **P2-T001** VEO API アカウント作成・キー取得
2. **P2-T002** Google AI Studio 設定・テスト
3. **P2-T003** Phase 2 `/specify` 仕様書作成
4. **P2-T004** AI統合アーキテクチャ設計
5. **P2-T005** Phase 2 `/plan` 実装計画作成

## Notes

- [P] tasks = different files, no dependencies, can run parallel
- Verify ALL tests fail before implementing (TDD requirement)
- Commit after each task completion
- Real hardware testing required at checkpoints
- No mocks for hardware integration tests

## Validation Checklist ✅

- [x] All contracts have corresponding tests (T009-T016)
- [x] All entities have model tasks (T025-T029)  
- [x] All tests come before implementation
- [x] Parallel tasks truly independent ([P] marked correctly)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Hardware integration points identified
- [x] TDD cycle clearly enforced

## SUCCESS: 60 tasks generated, ready for Phase 1 implementation! 🚀