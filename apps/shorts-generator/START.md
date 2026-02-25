# Lesson Shorts - Quick Start Guide

## 🚀 One-Command Start (Backend)

### Option A: Using Docker Compose (Recommended)

```bash
cd apps/shorts-generator

# Start everything (PostgreSQL, Redis, API, Celery Worker, Celery Beat, Flower)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop everything
docker-compose down
```

### Option B: Using Nx Commands

```bash
# Start API server
pnpm nx run shorts-generator:dev

# In another terminal - Start Celery Worker
pnpm nx run shorts-generator:worker

# In another terminal - Start Celery Beat (scheduler)
pnpm nx run shorts-generator:beat

# In another terminal - Start Flower (monitoring UI)
pnpm nx run shorts-generator:flower
```

## 🎬 Frontend - View Shorts

```bash
cd apps/learn-app

# Start the frontend
pnpm nx serve learn-app

# Visit: http://localhost:3000/shorts
```

## 📊 Admin Dashboard

```bash
# Frontend must be running
# Visit: http://localhost:3000/admin/shorts
```

## 🧪 Test the API

```bash
# Health check
curl http://localhost:8001/api/v1/health

# Generate a short video
curl -X POST http://localhost:8001/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_path": "01-General-Agents-Foundations/01-agent-factory-paradigm/README.md",
    "target_duration": 60
  }'

# Check job status
curl http://localhost:8001/api/v1/jobs

# View cost summary
curl http://localhost:8001/api/v1/cost/summary
```

## ⏰ Auto-Generation Schedule

**Yes, videos are created automatically!**

Celery Beat runs on a **daily schedule**:
- **Time**: 10 AM UTC (every day)
- **Task**: Auto-generate shorts from lessons without videos
- **Batch Size**: 5 videos per run (configurable)

### Configure Auto-Generation

Add to your `.env` file:

```bash
# Enable/disable auto-generation
AUTO_GENERATE_ENABLED=true

# Number of shorts to generate per run
AUTO_GENERATE_BATCH_SIZE=5

# (Optional) Specific parts to generate from
AUTO_GENERATE_PARTS=01,02,03
```

### View Scheduled Tasks

Visit **Flower** (Celery monitoring UI):
- URL: http://localhost:5555
- Shows: Active tasks, scheduled tasks, worker status

## 📁 Project URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend - Shorts Feed | http://localhost:3000/shorts | Watch shorts |
| Frontend - Admin | http://localhost:3000/admin/shorts | Dashboard |
| Backend API | http://localhost:8001 | API docs |
| API Documentation | http://localhost:8001/docs | Swagger UI |
| Flower Monitoring | http://localhost:5555 | Celery UI |
| Health Check | http://localhost:8001/api/v1/health | Status |

## 🗄️ Database (No Alembic Required!)

Tables are created **automatically** on startup. No migrations needed!

If you need to reset the database:

```bash
# Using Docker
docker-compose down -v
docker-compose up -d

# Or manually drop tables
psql postgresql://postgres:postgres@localhost:5432/shorts_db
DROP TABLE generation_jobs, short_videos, scripts, scenes, short_likes, short_comments, short_views, short_analytics CASCADE;
```

## 🔧 Environment Variables

Required in `apps/shorts-generator/.env`:

```bash
# Gemini API (for script generation)
GEMINI_API_KEY=your-gemini-api-key

# Database (auto-created tables)
SHORTS_DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/shorts_db

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# R2 Storage (for video CDN)
R2_ACCOUNT_ID=your-r2-account-id
R2_ACCESS_KEY_ID=your-r2-access-key-id
R2_SECRET_ACCESS_KEY=your-r2-secret-access-key
R2_BUCKET_NAME=agentfactory-shorts
R2_PUBLIC_URL=https://your-bucket.r2.dev

# Auto-generation
AUTO_GENERATE_ENABLED=true
AUTO_GENERATE_BATCH_SIZE=5

# Cost limits
MAX_COST_PER_VIDEO=0.006
DAILY_BUDGET_ALERT=10
MONTHLY_BUDGET_LIMIT=100
```

## 📊 Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Content extraction | ✅ | From lessons |
| Script generation (Gemini) | ✅ | $0.002/video |
| Image generation (Pollinations) | ✅ | FREE! |
| Audio generation (Edge-TTS) | ✅ | FREE! |
| Video assembly (FFmpeg) | ✅ | FREE! |
| **Cost per video** | ✅ | **~$0.002** |
| Async job processing | ✅ | Celery + Redis |
| R2 CDN storage | ✅ | $0.015/GB |
| TikTok-style feed | ✅ | Vertical scroll |
| Engagement (likes, comments) | ✅ | Full support |
| Search & filters | ✅ | By part/chapter |
| Admin dashboards | ✅ | Generation, analytics, cost |
| **Auto-generation** | ✅ | **Daily @ 10 AM UTC** |
| Recommendation engine | ✅ | Personalized feed |

## 🎯 Quick Commands

```bash
# --- Backend ---

# Start all services (Docker)
cd apps/shorts-generator && docker-compose up -d

# Start API only
cd apps/shorts-generator && pnpm nx run shorts-generator:dev

# Start worker only
cd apps/shorts-generator && pnpm nx run shorts-generator:worker

# Start scheduler only
cd apps/shorts-generator && pnpm nx run shorts-generator:beat

# --- Frontend ---

# Start frontend
cd apps/learn-app && pnpm nx serve learn-app

# --- Testing ---

# Test health
curl http://localhost:8001/api/v1/health

# Generate short
curl -X POST http://localhost:8001/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"lesson_path": "01-General-Agents-Foundations/01-agent-factory-paradigm/README.md"}'

# View jobs
curl http://localhost:8001/api/v1/jobs

# View costs
curl http://localhost:8001/api/v1/cost/summary
```

## 🆘 Troubleshooting

**Problem**: API returns 500
**Solution**: Check `.env` file has all required values

**Problem**: Celery worker not processing tasks
**Solution**: Check Flower at http://localhost:5555

**Problem**: Database connection error
**Solution**: Ensure PostgreSQL is running (`docker ps | grep postgres`)

**Problem**: Tables not created
**Solution**: Tables are created automatically on first API startup

**Problem**: Images not generating
**Solution**: Pollinations.ai is used (free, no API key needed)

## 📚 Additional Resources

- **API Docs**: http://localhost:8001/docs
- **Flower UI**: http://localhost:5555
- **Tasks File**: `.claude/plans/tasks.md`
- **Project Docs**: `/apps/shorts-generator/README.md`
