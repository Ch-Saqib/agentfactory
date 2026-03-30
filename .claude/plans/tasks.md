# Lesson Shorts - Implementation Tasks

**Feature**: Automated short video generation from lesson content
**Created**: 2026-02-24
**Status**: Phase 1 (MVP) Complete | Phase 2-4 Pending

---

## Task Summary

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Completed | 14 | 74% |
| 🔄 In Progress | 0 | 0% |
| ⏳ Pending | 5 | 26% |
| **Total** | **19** | **100%** |

---

## Completed Tasks ✅

### Phase 1: MVP - Core Generation Services

#### Task #1: Create shorts-generator app structure ✅
**Status**: Completed
**Files Created**:
- `apps/shorts-generator/project.json` - Nx configuration
- `apps/shorts-generator/pyproject.toml` - Python dependencies
- `apps/shorts-generator/.env.example` - Environment template
- `apps/shorts-generator/README.md` - Documentation
- `apps/shorts-generator/Dockerfile` - Container definition
- `apps/shorts-generator/alembic.ini` - Migration config

**Dependencies**: None

---

#### Task #2: Set up database schema and migrations ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/database/connection.py` - Async DB connection
- `src/shorts_generator/models/__init__.py` - 8 SQLAlchemy models
- `src/shorts_generator/database/migrations/env.py` - Alembic config
- `tests/test_models.py` - Model tests

**Models**: GenerationJob, ShortVideo, Script, Scene, ShortLike, ShortComment, ShortView, ShortAnalytics

**Dependencies**: Task #1

---

#### Task #3: Implement content extractor service ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/services/content_extractor.py` - Content extraction
- `tests/test_content_extractor.py` - Extraction tests

**Features**:
- Fetch lessons from GitHub
- Parse frontmatter and markdown
- Extract key concepts from headings
- Extract code blocks with language detection
- Validate lesson suitability

**Dependencies**: Task #2

---

#### Task #4: Implement script generator with Gemini ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/services/script_generator.py` - Script generation
- `tests/test_script_generator.py` - Script tests

**Features**:
- Generate hook-concept-example-CTA structure
- Visual descriptions for each scene
- Google Gemini 2.0 Flash integration
- Cost: $0.002 per script
- Timing validation (±10 second tolerance)

**Dependencies**: Task #3

---

#### Task #5: Implement visual generation service ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/services/visual_generator.py` - Visual generation
- `tests/test_visual_generator.py` - Visual tests

**Features**:
- Flux.1 via Replicate: $0.002/image
- Carbon.now.sh for code screenshots (free)
- Redis caching by visual hash (30-day TTL)
- 9:16 aspect ratio for vertical video

**Dependencies**: Task #4

---

#### Task #6: Implement audio generation with Edge-TTS ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/services/audio_generator.py` - Audio generation
- `tests/test_audio_generator.py` - Audio tests

**Features**:
- Microsoft Edge-TTS (free)
- Closed captions in SRT format
- Background music mixing support
- Duration estimation from word count

**Dependencies**: Task #5

---

#### Task #7: Implement video assembly with FFmpeg ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/services/video_assembler.py` - Video assembly
- `tests/test_video_assembler.py` - Assembly tests

**Features**:
- Compose scenes, audio, captions with FFmpeg
- Web optimization (H.264, 1080x1920, 30fps)
- Max file size: 50MB
- Dynamic bitrate calculation
- Thumbnail generation

**Dependencies**: Task #6

---

### Phase 2: Pipeline - Automated Generation Service

#### Task #8: Create FastAPI routes and endpoints ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/routes/generate.py` - Single generation endpoint
- `src/shorts_generator/routes/batch.py` - Batch generation endpoint
- `src/shorts_generator/routes/status.py` - Job tracking endpoint
- `src/shorts_generator/main.py` - Updated with routes

**Endpoints**:
- `POST /api/v1/generate` - Generate single short
- `POST /api/v1/generate/sync` - Synchronous generation (blocking)
- `POST /api/v1/batch` - Batch generation
- `GET /api/v1/status/{job_id}` - Job status
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/videos/{video_id}` - Video metadata
- `GET /api/v1/videos` - List all videos
- `GET /api/v1/health` - Health check
- `POST /api/v1/jobs/{job_id}/retry` - Retry failed job

**Dependencies**: Tasks #4, #5, #6, #7, #8

---

#### Task #9: Write comprehensive test suite ✅
**Status**: Completed
**Files Created**:
- `tests/test_config.py` - Configuration tests
- `tests/test_models.py` - Database model tests
- `tests/test_content_extractor.py` - Content extraction tests
- `tests/test_script_generator.py` - Script generation tests
- `tests/test_visual_generator.py` - Visual generation tests
- `tests/test_audio_generator.py` - Audio generation tests
- `tests/test_video_assembler.py` - Video assembly tests

**Test Coverage**: All core services and models

**Dependencies**: All service tasks

---

#### Task #10: Implement Celery job queue system ✅
**Status**: Completed
**Files Created**:
- `src/shorts_generator/workers/celery_worker.py` - Celery configuration
- `src/shorts_generator/workers/tasks.py` - Async task definitions
- `src/shorts_generator/workers/__init__.py` - Package exports
- Updated `routes/generate.py` - Triggers Celery tasks
- Updated `routes/batch.py` - Priority queue support
- Updated `routes/status.py` - Retry via Celery
- Updated `main.py` - Health checks for Redis/Celery
- Updated `project.json` - worker/beat/flower targets

**Features**:
- Redis message broker
- Async task execution with progress tracking
- Retry logic with exponential backoff (max 3 retries)
- Priority queues (high, normal, low)
- Rate limiting (10 generations per minute)
- Celery Beat for periodic tasks (cleanup, purging)
- Time limits (1 hour max, 55 min soft)
- Worker auto-restart after 10 tasks

**Nx Targets**:
- `pnpm nx run shorts-generator:worker` - Start Celery worker
- `pnpm nx run shorts-generator:beat` - Start Celery Beat scheduler
- `pnpm nx run shorts-generator:flower` - Start Flower monitoring UI

**Dependencies**: Task #9

---

## Pending Tasks ⏳

### Phase 2: Pipeline - Automated Generation Service (Continued)
**Status**: Completed
**Files Created**:
- `tests/test_config.py` - Configuration tests
- `tests/test_models.py` - Database model tests
- `tests/test_content_extractor.py` - Content extraction tests
- `tests/test_script_generator.py` - Script generation tests
- `tests/test_visual_generator.py` - Visual generation tests
- `tests/test_audio_generator.py` - Audio generation tests
- `tests/test_video_assembler.py` - Video assembly tests

**Test Coverage**: All core services and models

**Dependencies**: All service tasks

---

## Pending Tasks ⏳

### Phase 2: Pipeline - Automated Generation Service (Continued)

#### Task #10: Implement Celery job queue system ⏳
**Status**: Pending (Blocked by Task #9 - now unblocked)
**Priority**: High

**Description**:
- Create Celery worker configuration
- Implement async task execution
- Set up Redis as message broker
- Job progress tracking
- Retry logic for failed jobs
- Priority queue support (high, normal, low)

**Files to Create**:
- `src/shorts_generator/workers/celery_worker.py` - Worker configuration
- `src/shorts_generator/workers/tasks.py` - Async task definitions
- Update `routes/generate.py` - Trigger Celery tasks
- Update `routes/batch.py` - Batch task dispatch

**Dependencies**: Task #9 (now unblocked)

---

#### Task #11: Implement Cloudflare R2 storage integration ✅
**Status**: Completed
**Priority**: High

**Description**:
- Configure R2 bucket
- Upload videos to CDN
- Upload thumbnails to CDN
- Upload captions to CDN
- Generate signed URLs for access
- Auto-purge old content after 90 days

**Files Created**:
- `src/shorts_generator/services/storage.py` - R2 storage service
- Updated `video_assembler.py` - Upload video after assembly
- Updated `workers/tasks.py` - Upload captions
- Updated `routes/status.py` - Storage stats and delete endpoints
- Updated config - R2 credentials and custom domain
- Updated `.env.example` - R2_CUSTOM_DOMAIN option

**Features**:
- Upload videos, thumbnails, captions to R2
- Generate public CDN URLs
- Generate presigned URLs (7-day expiry)
- Delete individual files or all files for a video
- Storage statistics (file count, size, cost)
- Custom domain support for CDN

**Cost**: $0.015/GB storage + free egress

**Dependencies**: Task #10 ✅

---

### Phase 3: Feed - TikTok-Style UI

#### Task #12: Create Shorts Feed component with TikTok-style UI ✅
**Status**: Completed
**Priority**: High

**Description**:
- Vertical scroll-snap feed (9:16 aspect ratio)
- Auto-play on scroll to viewport
- Pause on scroll away
- Muted by default, tap to unmute
- Double-tap to like
- Swipe up/down navigation

**Files Created**:
- `src/components/shorts/ShortsFeed.tsx` - Main feed component
- `src/components/shorts/ShortVideoPlayer.tsx` - Video player with auto-play
- `src/components/shorts/ShortsControls.tsx` - Like/comment/share controls
- `src/components/shorts/types.ts` - TypeScript types
- `src/components/shorts/hooks/useShortsFeed.ts` - Feed data fetching hook
- `src/components/shorts/hooks/useVideoPlayback.ts` - Playback state management
- `src/components/shorts/index.ts` - Component exports
- `src/components/shorts/styles.css` - Animation and layout styles

**Features**:
- Scroll-snap vertical feed (100vh cards)
- Auto-play on scroll to viewport
- Pause on scroll away
- Muted by default with tap-to-unmute
- Double-tap to like with heart animation
- Swipe gesture support (up/down)
- Keyboard navigation (arrow keys)
- Auto-load more when near end
- Loading, error, and empty states
- Progress indicator dots
- View lesson button

**Dependencies**: Task #9 ✅ (API endpoints)

---

#### Task #13: Create shorts API client integration ✅
**Status**: Completed
**Priority**: High

**Description**:
- TypeScript client for shorts API
- Feed fetching with filters
- Single video fetching
- Engagement actions (like, comment, share)
- Progress tracking

**Files Created**:
- `src/lib/shorts-api.ts` - Complete API client with all endpoints
- Updated `src/components/shorts/hooks/useShortsFeed.ts` - Uses API client, added hooks:
  - `useVideoLike` - Like/unlike functionality
  - `useVideoComments` - Comment functionality
  - `useVideoViewTracking` - View tracking

**Features**:
- Full TypeScript API client with error handling
- Endpoints: health, videos, jobs, batch, engagement, storage
- Pagination support for feeds
- Job status tracking and retry
- Cost estimation for batches
- Storage statistics
- Singleton pattern for API client
- Hooks for common operations (like, comment, view tracking)

**Dependencies**: Task #12 ✅

---

#### Task #14: Implement engagement features ✅
**Status**: Completed
**Priority**: Medium

**Description**:
- Like system with heart animation
- Comment system with threaded replies
- Share system (copy link, download, native share)
- Engagement persistence to backend

**Files Created**:
- `src/components/shorts/ShortsComments.tsx` - Comments panel component
- `src/components/shorts/hooks/useEngagement.ts` - Engagement hook with:
  - `useEngagement` - Main engagement hook
  - `useBatchEngagement` - Batch operations
- `src/routes/engagement.py` - Backend API endpoints:
  - `POST /videos/{video_id}/like` - Like a video
  - `POST /videos/{video_id}/unlike` - Unlike a video
  - `POST /videos/{video_id}/comments` - Add comment
  - `GET /videos/{video_id}/comments` - Get comments with replies
  - `POST /videos/{video_id}/views` - Record view progress
  - `GET /videos/{video_id}/engagement` - Get engagement stats
- Updated `main.py` - Included engagement router

**Features**:
- Threaded comment support (up to 2 levels)
- Native share API with clipboard fallback
- Anonymous view tracking support
- Engagement stats aggregation
- Batch engagement operations

**Dependencies**: Task #12 ✅, Task #13 ✅

---

#### Task #15: Implement discovery and filtering features ✅
**Status**: Completed
**Priority**: Medium

**Description**:
- Filter by Part (01-09)
- Filter by Chapter within Part
- Search by keyword
- Sort by: Recent, Popular, Relevant
- Personalized recommendations

**Files Created**:
- `apps/learn-app/src/components/shorts/ShortsFilters.tsx` - Filter UI
- `apps/learn-app/src/components/shorts/ShortsSearch.tsx` - Search
- `apps/learn-app/src/components/shorts/index.ts` - Updated exports

**Features**:
- Part filter (01-09 with friendly names)
- Chapter filter (shown when part is selected)
- Sort options (Recent, Popular, Relevant)
- Active filter count badge
- Debounced search (300ms delay)
- Keyboard shortcut (Ctrl+K / Cmd+K)
- RecommendedShorts component with "For You", "Continue Learning", and "Trending" sections

**Dependencies**: Task #12 ✅

---

### Phase 4: Advanced - Analytics & Operations

#### Task #16: Create generation dashboard for admins ✅
**Status**: Completed
**Priority**: Medium

**Description**:
- Job queue visualization
- Real-time progress tracking
- Cost breakdown (actual vs estimated)
- Success/failure rate
- Retry failed jobs button
- Batch generation status

**Files Created**:
- `apps/learn-app/src/components/shorts/admin/GenerationDashboard.tsx` - Dashboard UI
- `apps/learn-app/src/components/shorts/admin/index.ts` - Admin exports

**Features**:
- Job queue visualization with status badges
- Real-time progress tracking with auto-refresh
- Statistics cards (total jobs, processing, success rate, total cost)
- Storage statistics display
- Status filter tabs
- Retry failed jobs functionality
- Pagination support
- Compact mini dashboard component

**Dependencies**: Tasks #9 ✅, #10 ✅ (now unblocked)

---

#### Task #17: Create analytics dashboard ✅
**Status**: Completed
**Priority**: Medium

**Description**:
- Per-short analytics (views, likes, shares, completion rate)
- Aggregate analytics (total generated, total cost, top performing)
- CTR to full lesson tracking
- Engagement score calculation

**Files Created**:
- `apps/shorts-generator/src/shorts_generator/routes/analytics.py` - Backend analytics endpoints
- `apps/learn-app/src/components/shorts/admin/AnalyticsDashboard.tsx` - Analytics UI
- Updated `apps/learn-app/src/lib/shorts-api.ts` - Added analytics API methods
- Updated `apps/shorts-generator/src/shorts_generator/main.py` - Included analytics router

**Features**:
- Aggregate analytics (total generated, total cost, total engagement)
- Per-video detailed analytics (views, likes, comments, completion rate, engagement score)
- Top performing videos by views/likes/engagement
- Sortable video list with detailed metrics
- Video details panel with ROI calculation
- Compact mini analytics component
- CTR tracking implementation notes

**Dependencies**: Task #16 ✅

---

#### Task #18: Implement recommendation engine ✅
**Status**: Completed
**Priority**: Low

**Description**:
- Collaborative filtering algorithm
- Content-based filtering
- Hybrid recommendation approach
- Personalized "For You" feed

**Files Created**:
- `src/shorts_generator/services/recommendation.py` - Recommendation logic
- `src/shorts_generator/routes/recommendations.py` - Recommendations endpoints
- Updated `src/shorts_generator/main.py` - Included recommendations router
- Updated `apps/learn-app/src/lib/shorts-api.ts` - Added recommendations API methods

**Features**:
- Collaborative filtering (users who liked what you liked)
- Content-based filtering (same part/chapter recommendations)
- Contextual recommendations (based on current lesson)
- Weaker area prioritization (for struggling topics)
- "For You" personalized feed
- Continue watching (partially watched videos)
- Trending shorts for anonymous users

**Dependencies**: Task #11 ✅

---

#### Task #19: Implement cost control and monitoring ✅
**Status**: Completed
**Priority**: High

**Description**:
- Daily/monthly cost tracking
- Alert when budget exceeded
- Per-job cost breakdown
- Cache hit rate monitoring
- API usage by service

**Files Created**:
- `src/shorts_generator/services/cost_monitor.py` - Cost tracking service
- `src/shorts_generator/routes/cost_monitor.py` - Cost monitoring endpoints
- `apps/learn-app/src/components/shorts/admin/CostMonitorWidget.tsx` - Cost dashboard widget
- Updated `src/shorts_generator/main.py` - Included cost_monitor router
- Updated `apps/learn-app/src/lib/shorts-api.ts` - Added cost monitoring API methods

**Features**:
- Daily cost breakdown with alert thresholds
- Monthly cost breakdown with projections
- Per-job cost breakdown
- Cost summary (today, this month, all-time)
- Budget alert system with severity levels
- Cost monitor dashboard widget with inline variant
- API usage tracking by service
- Service cost definitions (Gemini, Flux, Edge-TTS, FFmpeg, R2)

**Dependencies**: Tasks #9 ✅, #10 ✅ (now unblocked)

---

## Task Dependency Graph

```
Phase 1: MVP (Services)
├── #1: App Structure
├── #2: Database Schema ←── #1
├── #3: Content Extractor ←── #2
├── #4: Script Generator ←── #3
├── #5: Visual Generator ←── #4
├── #6: Audio Generator ←── #5
├── #7: Video Assembler ←── #6
└── #9: Tests ←── #2-7

Phase 2: Pipeline (API)
├── #8: FastAPI Routes ←── #4,5,6,7 ✅ COMPLETED
├── #10: Celery Queue ←── #8 ✅ COMPLETED
└── #11: R2 Storage ←── #10 ✅ COMPLETED

Phase 3: Feed (UI)
├── #12: Shorts Feed ←── #8 ⏳ READY
├── #13: API Client ←── #12
├── #14: Engagement ←── #12
└── #15: Discovery ←── #12

Phase 4: Advanced
├── #16: Gen Dashboard ←── #8, #10 ✅ COMPLETED
├── #17: Analytics ←── #16 ✅ COMPLETED
├── #18: Recommendations ←── #11 ✅ COMPLETED
└── #19: Cost Monitor ←── #8, #10 ✅ COMPLETED
```

---

## Next Steps

**All tasks completed!** 🎉

The Lesson Shorts feature is now fully implemented with:
- Core generation services (content extraction, script generation, visuals, audio, video assembly)
- Async job queue system with Celery
- Cloudflare R2 storage integration
- TikTok-style feed with engagement features
- Discovery and filtering capabilities
- Admin dashboards (generation, analytics, cost monitoring)
- Recommendation engine
- Cost control and monitoring

**Next actions**:
1. Deploy infrastructure (PostgreSQL, Redis, R2)
2. Configure environment variables
3. Generate first batch of shorts from top lessons
4. Monitor costs and performance
5. Iterate based on analytics

---

## Progress by Phase

| Phase | Tasks | Completed | Percentage |
|-------|-------|-----------|------------|
| Phase 1: MVP Services | 9 | 9 | **100%** ✅ |
| Phase 2: Pipeline | 3 | 3 | **100%** ✅ |
| Phase 3: Feed | 4 | 4 | **100%** ✅ |
| Phase 4: Advanced | 4 | 4 | **100%** ✅ |
| **Overall** | **20** | **20** | **100%** ✅ |

---

**Last Updated**: 2026-02-24
**Session**: All tasks completed! 🎉
