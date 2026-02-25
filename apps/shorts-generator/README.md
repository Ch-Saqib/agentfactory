# Lesson Shorts Generator

> Automated short video generation from lesson content using AI

## Overview

The Lesson Shorts Generator transforms lesson markdown content into engaging 60-90 second short videos using AI automation. It extracts key concepts, generates scripts with Google Gemini, creates visuals with Flux.1, adds narration with Edge-TTS (free), and assembles videos with FFmpeg.

**Target Cost**: ~$0.006 per video (98% savings vs traditional methods)

## Architecture

```
Lesson Content → Content Extractor → Script Generator (Gemini)
                                              ↓
Visual Generator (Flux.1) ←←←←←←←←←←←←←←←←←←
                                              ↓
Audio Generator (Edge-TTS) ←←←←←←←←←←←←←←←←←←
                                              ↓
Video Assembly (FFmpeg) → Upload to R2 CDN → Short Video
```

## Quick Start

### 1. Install Dependencies

```bash
cd apps/shorts-generator
uv sync
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Development Server

```bash
# Using nx
nx serve shorts-generator

# Or directly
cd src
uv run python -m uvicorn shorts_generator.main:app --reload --port 8001
```

### 4. Test Health Endpoint

```bash
curl http://localhost:8001/api/v1/health
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/generate` | POST | Generate single short |
| `/api/v1/batch` | POST | Batch generate shorts |
| `/api/v1/status/{job_id}` | GET | Get job status |
| `/api/v1/jobs` | GET | List all jobs |

## Cost Breakdown

| Component | Service | Cost |
|-----------|---------|------|
| Script Generation | Gemini 2.0 Flash | $0.002 |
| Image Generation | Flux.1 | $0.002 |
| Audio Generation | Edge-TTS | FREE |
| Storage | Cloudflare R2 | $0.001 |
| **Total** | | **$0.005** |

## Development

### Run Tests

```bash
nx test shorts-generator
```

### Lint Code

```bash
nx lint shorts-generator
```

### Type Check

```bash
nx typecheck shorts-generator
```

## Services

- **Content Extractor**: Parses lesson markdown and extracts key concepts
- **Script Generator**: Uses Google Gemini to generate 60-second scripts
- **Visual Generator**: Uses Flux.1 via Replicate for scene images
- **Audio Generator**: Uses Microsoft Edge-TTS for free narration
- **Video Assembler**: Uses FFmpeg to composite final video
- **Storage Service**: Uploads to Cloudflare R2 CDN

## Database Schema

Tables:
- `generation_jobs` - Job queue and status tracking
- `short_videos` - Generated video metadata
- `scripts` - Versioned script storage
- `scenes` - Individual scene data
- `short_likes` - User likes
- `short_comments` - User comments
- `short_views` - View tracking
- `short_analytics` - Aggregated analytics

## Deployment

### Docker

```bash
docker build -t shorts-generator:latest .
docker run -p 8001:8001 --env-file .env shorts-generator:latest
```

### Production

1. Set up PostgreSQL database
2. Run migrations: `uv run alembic upgrade head`
3. Configure Celery worker: `uv run celery -A shorts_generator.workers.celery_worker worker --loglevel=info`
4. Start API server: `uvicorn shorts_generator.main:app --host 0.0.0.0 --port 8001`

## License

MIT
