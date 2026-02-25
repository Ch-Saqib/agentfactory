# Lesson Shorts - Cost Optimization Strategies

> **Reduce per-video cost from ~$0.35 to ~$0.05 or less**

## 📊 Current Cost Breakdown

| Component | Service | Current Cost | % of Total |
|-----------|---------|--------------|------------|
| Script Generation | GPT-4 | $0.10 | 29% |
| Image Generation | DALL-E 3 | $0.20 (5 images) | 57% |
| Voiceover | OpenAI TTS | $0.015 | 4% |
| Storage/CDN | Cloud | $0.01 | 10% |
| **Total** | | **$0.35** | 100% |

**Images (DALL-E 3) are the biggest cost driver at 57% of total cost.**

---

## 🎯 Optimization Strategies (Ranked by Impact)

### 1. Replace DALL-E 3 with Stable Diffusion (Save 85% on images)

**Current**: DALL-E 3 at $0.04 per image × 5 = $0.20
**Optimized**: Stable Diffusion XL or Flux at ~$0.003 per image × 5 = $0.015

| Option | Cost per Image | Quality | Speed | Setup |
|--------|----------------|---------|-------|-------|
| DALL-E 3 | $0.04 | Excellent | Fast | None |
| Stable Diffusion XL | $0.003 (Replicate) | Very Good | Medium | API key |
| Flux.1 | $0.002 (Replicate) | Excellent | Fast | API key |
| Self-hosted SDXL | $0.0001 | Very Good | Slow | Server needed |

**Recommendation**: Use **Flux.1 via Replicate API** for best quality/cost ratio.

**Savings**: $0.20 → $0.01 = **$0.19 saved (54% reduction)**

---

### 2. Use Google Gemini for Script Generation (Save 92% on scripts) ⭐ RECOMMENDED

**Current**: GPT-4 at $0.10 per script
**Optimized**: Google Gemini models

| Model | Cost per Script | Quality | Best For |
|-------|-----------------|---------|----------|
| GPT-4 | $0.10 | Excellent | Complex topics |
| Gemini 2.0 Flash | $0.0025 | Excellent | **Most content (RECOMMENDED)** |
| Gemini 1.5 Flash | $0.0015 | Very Good | Simple lessons |
| GPT-4o-mini | $0.015 | Very Good | Fallback |
| Claude Haiku | $0.008 | Good | Alternative |
| Llama 3.1 70B (Groq) | $0.0003 | Good | Batch generation |

**Why Gemini 2.0 Flash?**
- **94% cheaper** than GPT-4 ($0.0025 vs $0.10)
- **Excellent quality** - competitive with GPT-4o
- **Fast** - sub-second response times
- **1M token context** - can process entire lessons at once
- **Free tier available** - up to 1,500 requests/day free

**Smart Strategy**: Use model routing based on content complexity

```python
def generate_script(lesson_complexity):
    if lesson_complexity == "high":
        return gemini_2_flash_generate(lesson)  # $0.0025
    elif lesson_complexity == "medium":
        return gemini_1_5_flash_generate(lesson)  # $0.0015
    else:
        return gemini_1_5_flash_generate(lesson)  # $0.0015

# Average cost: ~$0.002 per script (98% savings from GPT-4)
```

**Gemini API Pricing (as of 2025)**:
| Model | Input | Output | Typical Script Cost |
|-------|-------|--------|---------------------|
| Gemini 2.0 Flash | $0.075/M tokens | $0.30/M tokens | ~$0.0025 |
| Gemini 1.5 Flash | $0.075/M tokens | $0.15/M tokens | ~$0.0015 |
| Gemini 1.5 Pro | $1.25/M tokens | $5.00/M tokens | ~$0.012 |

**Savings**: $0.10 → $0.002 = **$0.098 saved (98% reduction)** ⭐

---

### 3. Reduce Image Count with Smart Generation (Save 40% on images)

**Current**: 5 images per short (hook, concept1, concept2, example, CTA)

**Optimized**: Generate only 2-3 images; reuse and transform

```python
# Smart image strategy
scenes = [
    {"type": "hook", "image": "generate"},           # New image
    {"type": "concept", "image": "reuse_hook"},      # Reuse with zoom
    {"type": "example", "image": "code_screenshot"}, # Free (carbon)
    {"type": "cta", "image": "brand_template"},      # Template (free)
]

# Cost: 1 image instead of 5
```

**Use code screenshots (free via carbon.now.sh)** for technical content
**Use branded templates** for intro/outro (one-time cost)

**Savings**: $0.01 → $0.003 = **$0.007 saved (2% reduction)**

---

### 4. Batch Generation with Volume Discounts (Save 20-30%)

**Current**: Per-video pricing on all APIs

**Optimized**: Use bulk processing

| Service | Volume Discount | Requirement |
|---------|-----------------|-------------|
| Replicate (SDXL/Flux) | Up to 30% off | 1000+ images/month |
| Together AI | 50% cheaper base | Already discounted |
| Groq | Free for Llama | Rate limited |
| OpenAI TTS | No discount | Consider alternatives |

**Recommendation**: Generate shorts in batches of 50+ to qualify for discounts

**Savings**: Additional **10-15% on API costs**

---

### 5. Cache and Reuse Generations (Save 50%+ on repeat content)

**Problem**: Regenerating same scripts/images for similar lessons

**Solution**: Intelligent caching system

```python
# Cache similar concepts
cache_key = f"concept:{hash(concept)}"

if cached := cache.get(cache_key):
    return cached["image"]

# Only generate if not in cache
image = generate_image(concept)
cache.set(cache_key, image, ttl=86400*30)  # 30 days
```

**Benefits**:
- Similar lessons share generated images
- Script templates reused for same structure
- Narration segments cached for common phrases

**Savings**: **20-30% on repeat content**

---

### 6. Free/Low-Cost Alternatives for Specific Components

### Voiceover Options
| Service | Cost | Quality | Notes |
|---------|------|---------|-------|
| OpenAI TTS | $0.015 | Excellent | Current |
| ElevenLabs | $0.05 | Best | Too expensive |
| Coqui TTS (open source) | $0 | Very Good | Self-host |
| Edge-TTS (Microsoft) | $0 | Good | Free API |
| Bark (open source) | $0 | Good | Self-host |

**Recommendation**: **Edge-TTS** (free) or **self-host Coqui** for best value

**Savings**: $0.015 → $0 = **$0.015 saved (4% reduction)**

### Storage Options
| Service | Cost | Best For |
|---------|------|----------|
| Vercel Blob | $0.15/GB | Convenience |
| Cloudflare R2 | $0.015/GB | Cost-effective |
| Backblaze B2 | $0.005/GB | Cheapest |
| Self-hosted S3 | $0.005/GB | Full control |

**Recommendation**: **Cloudflare R2** or **Backblaze B2**

**Savings**: $0.01 → $0.001 = **$0.009 saved (2.5% reduction)**

---

## 🎯 Optimized Cost Structure

### Before Optimization
| Component | Cost |
|-----------|------|
| Images (DALL-E 3) | $0.20 |
| Script (GPT-4) | $0.10 |
| Voiceover (OpenAI) | $0.015 |
| Storage | $0.01 |
| **Total** | **$0.35** |

### After All Optimizations (with Gemini)
| Component | Original | Optimized | Savings |
|-----------|----------|-----------|---------|
| Images (Flux.1 + fewer) | $0.20 | $0.003 | 98.5% |
| **Script (Gemini 2.0 Flash)** | $0.10 | **$0.002** | **98%** ⭐ |
| Voiceover (Edge-TTS) | $0.015 | $0 | 100% |
| Storage (Cloudflare R2) | $0.01 | $0.001 | 90% |
| **Total** | **$0.35** | **$0.006** | **98.3%** ⭐ |

### With Caching (30% additional savings)
**Final cost: ~$0.004 per short** (99% reduction) ⭐

---

## 📈 Scale Comparison (with Gemini)

| Scale | Original Cost | Optimized Cost | Annual Savings |
|-------|---------------|----------------|----------------|
| 100 shorts | $35 | $0.40 | $34.60 |
| 500 shorts | $175 | $2.00 | $173.00 |
| 1,000 shorts | $350 | $4.00 | $346.00 |
| 10,000 shorts | $3,500 | $40.00 | $3,460.00 |

---

## 🚀 Implementation Roadmap

### Phase 1: Quick Wins (Week 1)
1. ✅ Switch DALL-E 3 → Flux.1 via Replicate
2. ✅ Switch OpenAI TTS → Edge-TTS
3. ✅ Use carbon.now.sh for code screenshots
4. ✅ Implement image reuse strategy

**Impact**: 90% cost reduction → $0.035 per video

### Phase 2: Smart Routing (Week 2)
1. ✅ Implement model routing (GPT-4o-mini for most)
2. ✅ Add complexity detection
3. ✅ Set up caching layer

**Impact**: Additional 5% → $0.020 per video

### Phase 3: Infrastructure (Week 3-4)
1. ✅ Migrate storage to Cloudflare R2
2. ✅ Set up batch processing pipeline
3. ✅ Implement volume discount optimization

**Impact**: Additional 2% → $0.013 per video

### Phase 4: Advanced (Optional)
1. ⚡ Self-host Stable Diffusion (one-time server cost)
2. ⚡ Self-host TTS for full control
3. ⚡ CDN optimization

**Impact**: Near-zero marginal cost → $0.003 per video

---

## 💡 Hybrid Strategy for Maximum Value

### Tier 1: Marketing Shorts (Premium)
- Use: GPT-4 + DALL-E 3 + OpenAI TTS
- Cost: $0.35 per video
- Usage: Featured lessons, social media promo
- Volume: ~5% of content

### Tier 2: Standard Shorts (Optimized) ⭐
- Use: **Gemini 2.0 Flash** + Flux.1 + Edge-TTS
- Cost: **$0.006 per video**
- Usage: Regular lessons
- Volume: ~80% of content

### Tier 3: Batch Shorts (Economy)
- Use: Gemini 1.5 Flash + Cached images + Edge-TTS
- Cost: **$0.002 per video**
- Usage: Supplementary content, older lessons
- Volume: ~15% of content

### Blended Cost
```
(50 × $0.35) + (800 × $0.006) + (150 × $0.002) = $20.30
For 1000 shorts: $20.30 total (~$0.020 per short average)
```

---

## 🎓 Free/Open Source Alternatives (Full Self-Hosting)

For near-zero marginal costs after initial setup:

| Component | Self-Hosted Option | Setup Complexity | One-Time Cost |
|-----------|-------------------|------------------|---------------|
| Images | Automatic1111 (SDXL) | Medium | $50-100 server |
| Scripts | Llama 3.1 70B | Low | Free (Groq) |
| Voiceover | Coqui TTS | Medium | $20-50 server |
| Storage | MinIO (S3 compatible) | Low | $10-20 server |
| Assembly | FFmpeg | Low | Free |

**Total Setup**: ~$100-200 one-time
**Marginal Cost**: ~$0.003 per video (electricity)

---

## 📋 Cost Optimization Checklist

- [ ] Replace DALL-E 3 with Flux.1/Stable Diffusion
- [ ] Use GPT-4o-mini instead of GPT-4
- [ ] Switch to Edge-TTS for narration
- [ ] Implement image reuse strategy
- [ ] Use carbon.now.sh for code screenshots
- [ ] Set up Redis cache for generations
- [ ] Move storage to Cloudflare R2/Backblaze
- [ ] Implement model routing by complexity
- [ ] Generate in batches of 50+
- [ ] Use branded templates for intro/outro

---

## 🔍 Monitoring & Alerts

Set up cost tracking to prevent overruns:

```python
# Cost tracking
class CostTracker:
    daily_budget = 10  # $10/day
    alert_threshold = 0.8  # Alert at 80%

    def track_generation(self, cost):
        self.daily_cost += cost
        if self.daily_cost >= self.daily_budget * self.alert_threshold:
            send_alert(f"Cost at ${self.daily_cost:.2f}")
```

---

## 🎯 Recommended Starting Point

**Minimum Viable Optimization (98% cost reduction)**:

1. **Flux.1 via Replicate** for images ($0.002/image)
2. **Google Gemini 2.0 Flash** for scripts ($0.002/script) ⭐
3. **Edge-TTS** for narration (free)
4. **Carbon.now.sh** for code screenshots (free)
5. **Cloudflare R2** for storage ($0.015/GB)

**Result**: $0.006 per short (down from $0.35)
**ROI**: 58x cost reduction with minimal quality loss ⭐

**Plus**: Gemini has a **generous free tier** (1,500 requests/day) - ideal for testing!

---

## 🔧 Gemini Implementation Guide

### Quick Setup (5 minutes)

```bash
# Install Gemini SDK
pip install google-generativeai

# Or use the official Python client
pip install -q google.generativeai
```

### API Configuration

```python
# shorts_generator/src/scripter.py
import google.generativeai as genai
import os

# Configure API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model (2.0 Flash for best quality/speed balance)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Or use 1.5 Flash for even cheaper scripts
# model = genai.GenerativeModel('gemini-1.5-flash')
```

### Script Generation Function

```python
def generate_script_with_gemini(lesson_content: dict) -> dict:
    """
    Generate a 60-second short script from lesson content using Gemini.

    Cost: ~$0.002 per script
    Speed: <1 second
    """

    prompt = f"""
    You are an expert educational content creator specializing in short-form videos.

    Create a 60-second TikTok/Shorts-style script from this lesson:

    Title: {lesson_content['title']}
    Key Concepts: {lesson_content['concepts']}
    Difficulty: {lesson_content['level']}

    Requirements:
    - 60 seconds maximum (~150 words spoken)
    - Hook: Attention-grabbing opening (5 seconds)
    - Content: One key concept explained simply (35 seconds)
    - Example: Concrete proof or code snippet (15 seconds)
    - CTA: Call to action to read full lesson (5 seconds)

    Format as JSON:
    {{
        "hook": "text",
        "concept": "text",
        "visual_description": "for AI image generator",
        "example": "text",
        "cta": "text",
        "estimated_duration": 60
    }}
    """

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            max_output_tokens=500,
            response_mime_type="application/json"
        )
    )

    import json
    return json.loads(response.text)

# Usage
lesson = {
    "title": "The 2025 AI Inflection Point",
    "concepts": ["AI capability", "adoption rates", "enterprise spending"],
    "level": "beginner"
}

script = generate_script_with_gemini(lesson)
```

### Batch Processing (for cost efficiency)

```python
def generate_scripts_batch(lessons: list[dict]) -> list[dict]:
    """
    Generate multiple scripts efficiently using Gemini's batch API.
    Even cheaper when processing multiple lessons.
    """

    prompts = [
        f"Create a 60-second script for: {lesson['title']}"
        for lesson in lessons
    ]

    # Process in parallel using async
    import asyncio

    async def generate_all():
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        tasks = [model.generate_content_async(p) for p in prompts]
        return await asyncio.gather(*tasks)

    scripts = asyncio.run(generate_all())
    return scripts
```

### Free Tier Benefits

**Gemini 2.0 Flash Free Tier**:
- **1,500 requests per day** (up from 15 on GPT-4)
- Enough for ~50 shorts per day during development
- Perfect for MVP and testing

```python
# Check free tier usage
from google.generativeai import get_default_client

client = get_default_client()
# Returns remaining quota for the day
```

### Model Comparison for Scripts

| Model | Cost | Speed | Quality | Context | Best For |
|-------|------|-------|---------|---------|----------|
| Gemini 2.0 Flash | $0.0025 | ⚡ Fast | Excellent | 1M tokens | **Production** |
| Gemini 1.5 Flash | $0.0015 | ⚡ Fast | Very Good | 1M tokens | Batch/simple |
| Gemini 1.5 Pro | $0.012 | 🐢 Slow | Excellent | 2M tokens | Complex topics |
| GPT-4o-mini | $0.015 | ⚡ Fast | Very Good | 128K tokens | Fallback |

### Cost Comparison: Script Generation

| Model | Cost per Script | 100 scripts | 1,000 scripts | 10,000 scripts |
|-------|-----------------|-------------|---------------|----------------|
| GPT-4 | $0.10 | $10 | $100 | $1,000 |
| GPT-4o-mini | $0.015 | $1.50 | $15 | $150 |
| **Gemini 2.0 Flash** | **$0.0025** | **$0.25** | **$2.50** | **$25** |
| **Gemini 1.5 Flash** | **$0.0015** | **$0.15** | **$1.50** | **$15** |

**Gemini is 40x cheaper than GPT-4!** ⭐

### Environment Setup

```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
# Get free API key: https://aistudio.google.com/app/apikey
```

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-2.0-flash-exp")
```

---

**Status**: Optimization Strategy Complete | Gemini Integration Added
**Next**: Implement Phase 1 optimizations with Gemini
