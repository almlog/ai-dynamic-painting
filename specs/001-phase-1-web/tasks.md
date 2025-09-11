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
- [ ] T003 [P] Initialize frontend React project with npm dependencies
- [x] T004 [P] Configure backend linting (flake8, mypy, bandit) 
- [ ] T005 [P] Configure frontend linting (ESLint, Prettier)
- [x] T006 [P] Setup pytest configuration in backend/pytest.ini
- [ ] T007 [P] Setup Jest configuration in frontend/package.json
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
- [ ] T017 [P] Integration test video upload flow in backend/tests/integration/test_video_upload.py
- [ ] T018 [P] Integration test display control flow in backend/tests/integration/test_display_control.py
- [ ] T019 [P] Integration test M5STACK communication in backend/tests/integration/test_m5stack_integration.py
- [ ] T020 [P] Integration test 24-hour stability in backend/tests/integration/test_stability.py

### Frontend Component Tests
- [ ] T021 [P] Component test VideoUpload in frontend/tests/components/VideoUpload.test.js
- [ ] T022 [P] Component test VideoList in frontend/tests/components/VideoList.test.js
- [ ] T023 [P] Component test DisplayController in frontend/tests/components/DisplayController.test.js
- [ ] T024 [P] Component test SystemStatus in frontend/tests/components/SystemStatus.test.js

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [x] T025 [P] Video model in backend/src/models/video.py
- [x] T026 [P] DisplaySession model in backend/src/models/display_session.py
- [ ] T027 [P] UserDevice model in backend/src/models/user_device.py
- [x] T028 [P] SystemStatus model in backend/src/models/system_status.py
- [ ] T029 [P] ControlEvent model in backend/src/models/control_event.py

### Service Layer
- [x] T030 [P] VideoService CRUD in backend/src/services/video_service.py
- [x] T031 [P] DisplayService control logic in backend/src/services/display_service.py
- [x] T032 [P] M5StackService communication in backend/src/services/m5stack_service.py
- [ ] T033 [P] MonitoringService system monitoring in backend/src/services/monitoring_service.py

### API Endpoints  
- [x] T034 GET /api/videos endpoint in backend/src/api/routes/videos.py
- [ ] T035 POST /api/videos endpoint (file upload) in backend/src/api/routes/videos.py
- [ ] T036 DELETE /api/videos/{id} endpoint in backend/src/api/routes/videos.py
- [x] T037 POST /api/display/play endpoint in backend/src/api/routes/display.py
- [ ] T038 POST /api/display/pause endpoint in backend/src/api/routes/display.py
- [ ] T039 POST /api/display/resume endpoint in backend/src/api/routes/display.py
- [ ] T040 POST /api/display/stop endpoint in backend/src/api/routes/display.py
- [ ] T041 GET /api/display/status endpoint in backend/src/api/routes/display.py
- [x] T042 GET /api/m5stack/status endpoint in backend/src/api/routes/m5stack.py
- [x] T043 POST /api/m5stack/control endpoint in backend/src/api/routes/m5stack.py
- [ ] T044 GET /api/system/health endpoint in backend/src/api/routes/system.py

### Frontend Components
- [ ] T045 [P] VideoUpload component in frontend/src/components/VideoUpload.jsx
- [ ] T046 [P] VideoList component in frontend/src/components/VideoList.jsx
- [ ] T047 [P] DisplayController component in frontend/src/components/DisplayController.jsx
- [ ] T048 [P] SystemStatus component in frontend/src/components/SystemStatus.jsx
- [ ] T049 [P] Main dashboard page in frontend/src/pages/Dashboard.jsx

### Hardware Integration
- [ ] T050 [P] M5STACK firmware basic communication in m5stack/src/main.cpp
- [ ] T051 [P] M5STACK button handling in m5stack/src/buttons.cpp
- [ ] T052 [P] Video display controller in hardware/scripts/display_controller.py

## Phase 3.4: System Integration

- [ ] T053 Database connection and migration setup in backend/src/database/connection.py
- [ ] T054 File upload middleware and validation in backend/src/middleware/upload_middleware.py
- [ ] T055 CORS and security headers in backend/src/middleware/security_middleware.py
- [ ] T056 Structured logging setup in backend/src/utils/logger.py
- [ ] T057 Error handling and exception middleware in backend/src/middleware/error_middleware.py

## Phase 3.5: Polish & Validation

- [ ] T058 [P] Unit tests for video processing in backend/tests/unit/test_video_processing.py
- [ ] T059 [P] Performance tests (<3s Web UI, <1s M5STACK) in backend/tests/performance/test_response_times.py
- [ ] T060 [P] E2E tests with Playwright in tests/e2e/test_complete_flow.py

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
- [ ] Verify WiFi connection to Raspberry Pi
- [ ] Test HTTP requests to API endpoints
- [ ] Validate button response times <1s

### After T050-T052 (Hardware Implementation)  
- [ ] Physical M5STACK deployment and testing
- [ ] Video display on HDMI monitor
- [ ] End-to-end hardware flow validation

### After T060 (E2E Tests)
- [ ] 24-hour stability test with real hardware
- [ ] Memory leak detection on Raspberry Pi
- [ ] Full system integration validation

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