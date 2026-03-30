# Lesson Shorts - Automated Short Video Generation System

> **Transform lesson content into engaging 60-90 second videos using AI automation**

## 🎯 Vision

Capitalize on the short-form content revolution (YouTube Shorts, TikTok, Reels) by automatically generating bite-sized, informative videos from lesson content. Meet students where they already are - consuming quick, visual content.

## 📊 Market Insight

**The Shift to Short-Form:**
- YouTube Shorts: 2 billion+ logged-in monthly users
- Average watch time: 60-90 seconds
- 73% of users prefer short-form for learning quick concepts
- Attention spans have decreased from 12s (2000) to 8s (2023)

**Educational Content Gap:**
- Most educational shorts are manually created (expensive, slow)
- No platform auto-generates shorts from long-form content
- Opportunity to be first in "AI-generated educational shorts"

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Lesson Shorts System                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐   │
│  │   Content   │───▶│    Script    │───▶│   Video Generator   │   │
│  │  Extractor  │    │   Generator  │    │   (AI Pipeline)     │   │
│  └─────────────┘    └──────────────┘    └─────────────────────┘   │
│         │                   │                      │                │
│         │                   ▼                      ▼                │
│         │         ┌──────────────┐    ┌─────────────────────┐      │
│         │         │   Key        │    │   Visual Gen        │      │
│         │         │  Concepts    │    │   (DALL-E/SD)       │      │
│         │         └──────────────┘    └─────────────────────┘      │
│         │                   │                      │                │
│         ▼                   ▼                      ▼                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Video Assembly Engine                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │   │
│  │  │   Images   │+│  Voiceover │+│   Music    │            │   │
│  │  │   +       │  │   (TTS)    │  │  (Asset)   │            │   │
│  │  │ Animation  │  │            │  │            │            │   │
│  │  └────────────┘  └────────────┘  └────────────┘            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│                   ┌──────────────────┐                             │
│                   │   Storage & CDN  │                             │
│                   │   (Upload/Cache) │                             │
│                   └──────────────────┘                             │
│                              │                                      │
│                              ▼                                      │
│                   ┌──────────────────┐                             │
│                   │  Shorts Feed UI  │                             │
│                   │  (TikTok-style)  │                             │
│                   └──────────────────┘                             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔧 Technical Components

### 1. Content Extractor Service
```python
# apps/shorts-generator/src/extractor.py
- Parse lesson Markdown
- Extract key concepts (headings, code blocks, key_points)
- Identify quotable moments
- Generate summary bullets
- Extract code examples for visualization
```

### 2. Script Generator Agent
```python
# apps/shorts-generator/src/scripter.py
- LLM-powered script generation
- 60-90 second timing optimization (~150-225 words)
- Hook → Concept → Example → CTA structure
- Platform-specific formatting (Shorts vs TikTok vs Reels)
```

### 3. Video Generation Pipeline
```python
# apps/shorts-generator/src/generator.py
├── Visual Generation
│   ├── DALL-E 3 / Stable Diffusion for images
│   ├── Code screenshot generation (carbon.now.sh API)
│   ├── Text overlay animations
│   └── Transition effects
│
├── Audio Generation
│   ├── OpenAI TTS / ElevenLabs for narration
│   ├── Background music (royalty-free library)
│   └── Sound effects library
│
└── Assembly
    ├── FFmpeg / Remotion for video composition
    ├── Subtitle/caption generation
    └── Platform optimization (9:16 aspect ratio)
```

### 4. Shorts Feed Frontend
```tsx
// apps/learn-app/src/components/shorts/ShortsFeed.tsx
- TikTok-style vertical scroll feed
- Auto-play on scroll
- Like, comment, share actions
- "Watch full lesson" CTA
- Filter by topic/part/chapter
```

## 📝 Script Template

```markdown
# {Lesson Title} - Short Script (60 seconds)

## Hook (0-5 seconds)
{Attention-grabbing question or statement}
"Did you know that..." or "Here's why..."

## Core Concept (5-30 seconds)
{Main teaching point}
- One key idea
- Simple explanation
- Visual: {description for AI image generator}

## Example/Proof (30-50 seconds)
{Concrete example or code snippet}
"Here's how it looks..."
Visual: Code screenshot or diagram

## Call to Action (50-60 seconds)
"What to learn more? Read the full lesson here..."
Visual: Lesson cover animation
```

## 🎨 Video Style Guide

### Visual Identity
- **Color Scheme**: Match Agent Factory brand (purple/blue gradient)
- **Typography**: Clean, readable sans-serif (Inter/Roboto)
- **Animation Style**: Smooth transitions, kinetic typography
- **Image Style**: Modern tech/AI aesthetic, consistent across videos

### Audio Identity
- **Voice**: Professional AI voice (alloy/echo for tech content)
- **Background Music**: Subtle lo-fi beats (doesn't compete with narration)
- **Sound Effects**: Minimal whoosh/click for transitions

## 🚀 Implementation Phases

### Phase 1: MVP (Proof of Concept)
**Deliverable**: Generate 5 sample shorts from existing lessons

**Tasks**:
- [ ] Content extractor script
- [ ] Basic script generator (GPT-4)
- [ ] Image generation (DALL-E 3)
- [ ] TTS narration (OpenAI)
- [ ] Basic FFmpeg assembly
- [ ] Manual upload to test feed

**Time Estimate**: 2-3 weeks

**Tech Stack**:
- Python 3.13+
- OpenAI API (GPT-4, DALL-E 3, TTS)
- FFmpeg for video assembly
- Supabase storage

### Phase 2: Automated Pipeline
**Deliverable**: Fully automated generation service

**Tasks**:
- [ ] Shorts Generator API service (FastAPI)
- [ ] Queue system for batch generation (Celery/Redis)
- [ ] Storage backend (CDN integration)
- [ ] Database to track generated shorts
- [ ] Web UI to trigger generation
- [ ] Progress tracking for generation jobs

**Time Estimate**: 3-4 weeks

**Tech Stack**:
- FastAPI backend
- Celery + Redis for async jobs
- Supabase (PostgreSQL + Storage)
- Vercel Blob CDN for video delivery

### Phase 3: Feed & Engagement
**Deliverable**: Full user-facing feature

**Tasks**:
- [ ] TikTok-style Shorts Feed component
- [ ] Like, comment, share functionality
- [ ] User progress integration (watched shorts)
- [ ] Filter by topic/part/chapter
- [ ] "Related Shorts" on lesson pages
- [ ] Mobile-responsive design

**Time Estimate**: 4-5 weeks

**Tech Stack**:
- React + TypeScript
- Framer Motion for animations
- Docusaurus integration
- Progress API integration

### Phase 4: Advanced Features
**Deliverable**: Enhanced engagement and personalization

**Tasks**:
- [ ] AI-generated quizzes at end of shorts
- [ ] "Short of the Day" notifications
- [ ] Social sharing (download for posting)
- [ ] Multi-language support
- [ ] Personalized short recommendations
- [ ] Creator studio (customize short style)
- [ ] Analytics dashboard

**Time Estimate**: 6-8 weeks

## 💰 Cost Analysis

### Per Video Costs
| Component | Service | Cost (USD) |
|-----------|---------|------------|
| Script Generation | GPT-4 | ~$0.10 |
| Image Generation | DALL-E 3 | ~$0.04 x 5 = $0.20 |
| Voiceover | OpenAI TTS | ~$0.015 |
| Storage | CDN | ~$0.01 |
| **Total per video** | | **~$0.35** |

### Scale Costs
- 100 lessons = $35 one-time generation
- 1000 lessons = $350 one-time generation
- Storage/bandwidth: ~$10-50/month depending on views

### Monthly Operating Costs (Estimates)
| Users/Views | Bandwidth | Storage | Total |
|-------------|-----------|---------|-------|
| 1K views/day | $5 | $2 | $7/month |
| 10K views/day | $25 | $5 | $30/month |
| 100K views/day | $150 | $10 | $160/month |

## 🎯 Success Metrics

### Engagement Metrics
- **Watch rate**: % of users who watch full short (target: 70%+)
- **CTR to lesson**: % who click "Read full lesson" (target: 15-25%)
- **Share rate**: % who share shorts externally (target: 5-10%)
- **Daily active users** viewing shorts

### Learning Metrics
- **Concept retention**: Quiz performance after watching shorts
- **Lesson completion**: Does shorts exposure increase lesson completion?
- **Time to mastery**: Do shorts accelerate learning?

### Growth Metrics
- **Viral coefficient**: How many users share organically?
- **SEO impact**: Do shorts drive organic traffic?
- **Social media reach**: Views on shared shorts

## 🔄 Generation Workflow

```python
# Example: Generate a short for Chapter 1 Lesson 1

# 1. Extract content
lesson = Lesson.get("01-General-Agents-Foundations/01-agent-factory-paradigm/01-the-2025-inflection-point.md")
concepts = extractor.extract_key_concepts(lesson)

# 2. Generate script
script = scripter.generate(
    title=lesson.title,
    concepts=concepts,
    duration=60,  # seconds
    hook_style="question",
    cta_link=f"/docs/{lesson.slug}"
)

# 3. Generate visuals
images = []
for scene in script.scenes:
    image = image_gen.generate(
        prompt=scene.visual_description,
        style="tech, modern, AI aesthetic",
        aspect_ratio="9:16"
    )
    images.append(image)

# 4. Generate audio
narration = tts.generate(script.narration_text, voice="alloy")

# 5. Assemble video
video = assembler.assemble(
    images=images,
    audio=narration,
    music="background_lofi.mp3",
    captions=script.narration_text,
    duration=60
)

# 6. Upload and publish
short_id = storage.upload(video)
feed.publish(short_id, lesson_id=lesson.id)
```

## 📱 Feed UI Design

```
┌────────────────────────────────────┐
│                                    │
│         [SHORTS FEED]              │
│                                    │
│  ┌──────────────────────────────┐ │
│  │                              │ │
│  │     [Auto-playing Video]     │ │
│  │                              │ │
│  │   "Did you know 2025 is...   │ │
│  │    an AI inflection point?"  │ │
│  │                              │ │
│  │   💬 1.2K  ❤️ 45K  ↗️ Share │ │
│  │                              │ │
│  │   [Read Full Lesson →]       │ │
│  │                              │ │
│  └──────────────────────────────┘ │
│                                    │
│  ↓ Scroll for more shorts ↓        │
│                                    │
└────────────────────────────────────┘
```

## 🔐 Integration Points

### With Existing Features
1. **TeachMePanel**: Add "Watch Short" before starting lesson
2. **Flashcards**: Generate shorts from difficult flashcards
3. **Quizzes**: Show short as hint before quiz question
4. **Progress Dashboard**: Track shorts watched alongside lessons
5. **Lesson Pages**: Embed related shorts at top

### External Sharing
1. **Social Media**: Download buttons for TikTok/Reels/Shorts
2. **Embed**: Allow embedding in other sites
3. **RSS**: Auto-publish to social platforms via API

## 🎯 Competitive Advantages

| Feature | Traditional | Agent Factory Shorts |
|---------|-------------|---------------------|
| Source | Manual creation | AI auto-generated |
| Speed | Hours per video | Minutes per video |
| Scale | Limited by team | Unlimited (1000+ lessons) |
| Consistency | Varies | Brand-consistent |
| Personalization | None | Per-lesson, per-user |
| Cost | High (editors) | Low (API calls) |

## 🎬 Example Script: "The 2025 Inflection Point"

```markdown
# Script: The 2025 AI Inflection Point (60 seconds)

## Hook (0-5s)
"Did you know we just lived through the biggest technology shift since the iPhone?"

## Concept 1 (5-20s)
"Three things happened in 2025 that changed everything forever.
Number one: AI can now write code better than most humans.
Number two: 84% of developers are already using AI every day.
Number three: Enterprises spent $3 trillion on AI infrastructure."

## Concept 2 (20-40s)
"This isn't hype. An AI system got a perfect score at the ICPC programming competition -
something no human has ever achieved.
The question isn't whether AI will replace developers.
It's whether you'll learn to work with it or get left behind."

## CTA (40-60s)
"I'm building something that teaches you exactly how to thrive in this new world.
Read the full lesson to understand why 2025 is the AI inflection point."
```

## 🚦 Next Steps

### Immediate (Week 1)
1. **Feasibility Test**: Generate 3 sample shorts manually
2. **Cost Validation**: Test with actual API calls
3. **Tech Stack Decision**: Choose Remotion vs FFmpeg

### Short-term (Weeks 2-4)
4. **User Research**: Survey students on short-form learning
5. **MVP Build**: Start Phase 1 development
6. **Design System**: Create visual templates

### Medium-term (Months 2-3)
7. **Pipeline Build**: Phase 2 automated service
8. **Feed Development**: Phase 3 user interface
9. **Beta Launch**: Test with small user group

### Long-term (Months 4-6)
10. **Advanced Features**: Phase 4 engagement features
11. **Analytics**: Measure and optimize
12. **Scale**: Generate shorts for all lessons

---

## 📚 Additional Resources

### Similar Projects for Reference
- [Summarize.tech](https://summarize.tech) - AI video summaries
- [Opus Clip](https://opus.pro) - Repurpose long videos to shorts
- [Munch](https://getmunch.com) - AI video repurposing

### APIs & Services
- OpenAI API (GPT-4, DALL-E 3, TTS)
- ElevenLabs (High-quality TTS)
- Stability AI (Stable Diffusion)
- Remotion (React-based video)
- Carbon (Beautiful code images)

---

**Status**: Design Complete | Ready for Implementation Planning

**Created**: 2025-02-24
**Author**: Agent Factory Team
