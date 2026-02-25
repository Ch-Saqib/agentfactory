# Feature Specification: Lesson Shorts - Automated Short Video Generation System

**Feature Branch**: `001-lesson-shorts`
**Created**: 2025-02-24
**Status**: Draft
**Input**: User description: "Lesson Shorts - Automated Short Video Generation System. Feature: Create a comprehensive specification for an automated system that transforms lesson content into engaging 60-90 second short videos using AI automation. Key Requirements: Auto-generate videos from 1000+ lessons, Use Google Gemini 2.0 Flash for scripts ($0.002/video), Use Flux.1/Stable Diffusion for visuals, Use Edge-TTS for free narration, TikTok-style feed for viewing, Target cost: ~$0.006 per video, Implement all 4 phases in one go. Phases to cover: 1. MVP: Content extraction, script generation, video assembly, 2. Pipeline: Automated generation service with queue system, 3. Feed: TikTok-style UI with engagement features, 4. Advanced: Analytics, personalization, social sharing."

## User Scenarios & Testing

### User Story 1 - Generate Short from Lesson (Priority: P1)

A content administrator selects a lesson from the book and triggers short video generation. The system automatically extracts key concepts, generates an engaging script, creates visuals, adds narration, and produces a 60-90 second video ready for viewing.

**Why this priority**: This is the core value proposition - automated transformation of long-form content into engaging short-form videos without manual editing.

**Independent Test**: Can be fully tested by selecting any lesson, triggering generation, and verifying a complete video file is produced within 5 minutes. Delivers immediate value: one short video from existing content.

**Acceptance Scenarios**:

1. **Given** a published lesson with markdown content, **When** administrator clicks "Generate Short", **Then** system queues the job and returns confirmation with estimated completion time
2. **Given** a queued generation job, **When** processing completes, **Then** system produces a video file with proper metadata (lesson ID, title, duration, thumbnail) and stores it in CDN
3. **Given** a failed generation attempt, **When** error occurs, **Then** system logs specific error, notifies administrator, and allows retry with adjusted parameters

---

### User Story 2 - Browse and Watch Shorts Feed (Priority: P1)

A learner opens the Shorts section and encounters a TikTok-style vertical scrolling feed. Videos auto-play on scroll, with smooth transitions between shorts. Each short displays engagement metrics and links to the full lesson.

**Why this priority**: Without consumption, generated videos have no value. The feed is the primary user interface for viewing content.

**Independent Test**: Can be fully tested by opening the Shorts feed, scrolling through 5+ videos, verifying auto-play, and checking that each video plays smoothly with proper controls. Delivers immediate value: watchable short-form content.

**Acceptance Scenarios**:

1. **Given** a user opens the Shorts feed, **When** page loads, **Then** first short auto-plays with sound muted by default, showing like/comment/share buttons
2. **Given** a user scrolls down, **When** next video comes into view, **Then** previous video pauses, new video auto-plays, with smooth scroll-snap transition
3. **Given** a user is watching a short, **When** they click "Read Full Lesson", **Then** system navigates to the full lesson page with the short embedded at top

---

### User Story 3 - Batch Generate Shorts for Multiple Lessons (Priority: P2)

A content administrator selects multiple lessons (or entire chapters/parts) and triggers batch generation. The system processes videos in parallel with progress tracking, sending notification when all are complete.

**Why this priority**: Critical for scaling to 1000+ lessons. Manual generation of each short is impractical at scale.

**Independent Test**: Can be fully tested by selecting 10 lessons, triggering batch generation, and monitoring progress dashboard showing real-time status of each job. Delivers immediate value: 10 shorts generated with one action.

**Acceptance Scenarios**:

1. **Given** a user selects 25 lessons from chapter list, **When** clicking "Generate Shorts for Selected", **Then** system creates 25 queued jobs and displays progress dashboard with status bars
2. **Given** batch generation in progress, **When** user refreshes page, **Then** progress persists and continues with current jobs preserved
3. **Given** all batch jobs complete, **When** generation finishes, **Then** system sends notification with summary (X succeeded, Y failed) and links to generated shorts

---

### User Story 4 - Engage with Shorts (Like, Comment, Share) (Priority: P2)

A learner watching a short can double-tap or click heart to like, type comments for discussion, and share the short externally (download for social media or copy link).

**Why this priority**: Engagement features increase retention and create viral growth potential through social sharing.

**Independent Test**: Can be fully tested by watching a short, liking it, posting a comment, and using share button to copy link. Delivers immediate value: user engagement and social sharing capability.

**Acceptance Scenarios**:

1. **Given** a user is watching a short, **When** they double-tap or click heart, **Then** like counter increments, animation plays, and like persists across sessions
2. **Given** a user posts a comment, **When** comment is submitted, **Then** comment appears below video, notifications sent to relevant users, and thread supports replies
3. **Given** a user clicks share button, **When** they select "Download", **Then** system generates watermarked video file (if not authenticated) or clean version (if authenticated) and downloads to device

---

### User Story 5 - Discover Relevant Shorts (Priority: P2)

A learner can filter shorts by topic, part, chapter, or search by keywords. The system recommends shorts based on viewing history and current lesson progress.

**Why this priority**: Without discovery, users struggle to find relevant content among hundreds of shorts.

**Independent Test**: Can be fully tested by applying filters (e.g., "Part 5: Building Custom Agents") and verifying only matching shorts appear. Delivers immediate value: targeted content discovery.

**Acceptance Scenarios**:

1. **Given** a user opens Shorts feed, **When** they select "Part 5" filter, **Then** feed updates to show only shorts from Part 5 chapters
2. **Given** a user searches for "MCP", **When** search executes, **Then** feed shows shorts with "MCP" in title, script, or tags
3. **Given** a user has watched 3 shorts about Python, **When** they open feed, **Then** "Recommended for You" section shows similar Python-related shorts

---

### User Story 6 - Track Generation Progress and Costs (Priority: P3)

A content administrator views a dashboard showing all generation jobs, their status, costs incurred, and success rate. Can retry failed jobs with one click.

**Why this priority**: Operational visibility is essential for managing costs and troubleshooting at scale.

**Independent Test**: Can be fully tested by opening dashboard, verifying job history displays with costs, and retrying a failed job. Delivers immediate value: operational oversight.

**Acceptance Scenarios**:

1. **Given** a user opens Generation Dashboard, **When** page loads, **Then** display shows total jobs, success rate, total cost, and list of recent jobs with status
2. **Given** a failed job in dashboard, **When** user clicks "Retry", **Then** system re-queues the job with same parameters and tracks retry count
3. **Given** 50 jobs completed this week, **When** user views cost summary, **Then** display shows actual vs. estimated cost, per-job breakdown, and projection for full 1000-lesson generation

---

### User Story 7 - Personalize Short Recommendations (Priority: P3)

A learner receives personalized short recommendations based on their reading progress, quiz performance, and viewing history. The system adapts recommendations as they engage with content.

**Why this priority**: Personalization increases engagement and helps learners discover relevant content efficiently.

**Independent Test**: Can be fully tested by completing a lesson, then opening Shorts feed and verifying "Recommended for You" shows shorts from related topics. Delivers immediate value: personalized discovery.

**Acceptance Scenarios**:

1. **Given** a user completed Chapter 11 Lesson 3, **When** they open Shorts feed, **Then** "Continue Learning" section shows shorts from Chapter 11 Lesson 4 and related concepts
2. **Given** a user scored poorly on Python quiz, **When** they open feed, **Then** system recommends Python review shorts to reinforce concepts
3. **Given** a user watches 5 shorts about FastAPI, **When** they open feed, **Then** recommendations prioritize similar backend/agent development topics

---

### User Story 8 - Analyze Short Performance (Priority: P3)

A content administrator views analytics for each short including: view count, watch-through rate, click-through to full lesson, shares, and engagement score. Can compare performance across lessons.

**Why this priority**: Analytics enable data-driven decisions about which content resonates and where to improve generation quality.

**Independent Test**: Can be fully tested by opening analytics page, selecting a short, and viewing all performance metrics. Delivers immediate value: performance insights.

**Acceptance Scenarios**:

1. **Given** a user opens Short Analytics, **When** they select a specific short, **Then** display shows views, unique viewers, average watch duration, completion rate, and CTR to lesson
2. **Given** multiple shorts from same chapter, **When** user compares them, **Then** table displays side-by-side metrics highlighting best/worst performing
3. **Given** a short with low completion rate, **When** user views analytics, **Then** system highlights drop-off points and suggests script revisions

---

### Edge Cases

**Generation Failure Scenarios**:
- What happens when lesson content is too short (<100 words) to generate meaningful short?
- What happens when lesson content has no extractable key concepts or code examples?
- What happens when image generation API (Flux.1) is rate-limited or unavailable?
- What happens when TTS service (Edge-TTS) returns audio quality issues?
- What happens when generated script exceeds 90-second target duration?

**Content Quality Scenarios**:
- What happens when generated visuals don't match lesson domain (e.g., code lesson gets abstract art)?
- What happens when script misrepresents technical concepts (hallucination)?
- What happens when code screenshots contain syntax errors or outdated examples?

**Feed and Playback Scenarios**:
- What happens when video file is corrupted or fails to load?
- What happens when user has slow internet connection (buffering issues)?
- What happens when generated short has no audio (TTS failure)?

**Scale and Performance Scenarios**:
- What happens when 1000+ generation jobs are queued simultaneously?
- What happens when CDN delivery is slow for certain regions?
- What happens when storage quota is exceeded during batch generation?

**Cost Control Scenarios**:
- What happens when monthly cost budget is exceeded?
- What happens when API pricing changes unexpectedly?
- What happens when caching layer fails, causing duplicate generations?

## Requirements

### Functional Requirements

**Content Extraction and Processing**:
- **FR-001**: System MUST parse lesson markdown files and extract structured content (headings, paragraphs, code blocks, key points)
- **FR-002**: System MUST identify and extract key concepts suitable for short-form explanation (2-5 concepts per lesson)
- **FR-003**: System MUST extract code examples and generate syntax-highlighted screenshots
- **FR-004**: System MUST detect lesson difficulty level and adjust script complexity accordingly

**Script Generation**:
- **FR-005**: System MUST generate 60-90 second scripts following hook-concept-example-CTA structure
- **FR-006**: System MUST include visual descriptions for each scene to guide image generation
- **FR-007**: System MUST validate script timing to ensure spoken duration fits target length
- **FR-008**: System MUST include call-to-action directing viewers to full lesson

**Visual Generation**:
- **FR-009**: System MUST generate 2-5 scene images matching visual descriptions in script
- **FR-010**: System MUST maintain consistent visual style across all shorts (brand colors, typography, aesthetic)
- **FR-011**: System MUST format images for vertical video (9:16 aspect ratio, 1080x1920 minimum)
- **FR-012**: System MUST overlay text with kinetic typography animations for key phrases
- **FR-013**: System MUST reuse and transform images where possible to minimize generation costs

**Audio Generation**:
- **FR-014**: System MUST convert script narration to speech using text-to-speech
- **FR-015**: System MUST add background music at appropriate volume (doesn't compete with narration)
- **FR-016**: System MUST generate closed captions from narration script

**Video Assembly**:
- **FR-017**: System MUST composite images, animations, text overlays, and audio into video file
- **FR-018**: System MUST ensure smooth transitions between scenes
- **FR-019**: System MUST optimize video file size for web delivery (H.264 codec, appropriate bitrate)
- **FR-020**: System MUST generate thumbnail image from first scene

**Generation Pipeline**:
- **FR-021**: System MUST queue generation jobs and process them asynchronously
- **FR-022**: System MUST support batch generation of multiple lessons in one request
- **FR-023**: System MUST provide real-time progress updates for queued and running jobs
- **FR-024**: System MUST retry failed jobs with exponential backoff (max 3 attempts)
- **FR-025**: System MUST cache generated components (scripts, images) to avoid redundant API calls

**Feed and Discovery**:
- **FR-026**: System MUST display shorts in TikTok-style vertical scroll feed
- **FR-027**: System MUST auto-play videos when they come into viewport
- **FR-028**: System MUST pause videos when they leave viewport
- **FR-029**: System MUST support filtering by part, chapter, topic, and search
- **FR-030**: System MUST display metadata (lesson title, view count, like count) on each short

**Engagement Features**:
- **FR-031**: System MUST allow users to like shorts with persistence across sessions
- **FR-032**: System MUST allow users to comment on shorts with threading support
- **FR-033**: System MUST allow users to share shorts via link copying
- **FR-034**: System MUST allow authenticated users to download clean video files
- **FR-035**: System MUST watermark downloaded videos for unauthenticated users

**Progress Tracking and Recommendations**:
- **FR-036**: System MUST track which shorts each user has watched
- **FR-037**: System MUST recommend shorts based on lesson progress and quiz performance
- **FR-038**: System MUST display "Watch Full Lesson" CTA linking to source lesson

**Analytics and Operations**:
- **FR-039**: System MUST track view count, unique viewers, average watch duration, and completion rate for each short
- **FR-040**: System MUST track click-through rate from short to full lesson
- **FR-041**: System MUST display generation dashboard with job status, costs, and success rate
- **FR-042**: System MUST alert administrators when cost budget thresholds are exceeded

**Cost Control**:
- **FR-043**: System MUST target maximum cost of $0.006 per generated short
- **FR-044**: System MUST use caching to reduce repeat generation costs by minimum 30%
- **FR-045**: System MUST implement model routing to use cheaper models for simpler content

### Key Entities

**Short Video**:
- Represents a generated short video from a lesson
- Attributes: ID, lesson source, title, script, duration, thumbnail URL, video URL, generation status, cost, created timestamp
- Relationships: Belongs to one Lesson, has many Likes, has many Comments, has many ViewEvents

**Generation Job**:
- Represents a single generation request in the queue
- Attributes: ID, lesson ID, status (queued/processing/completed/failed), progress percentage, error message, retry count, created/updated timestamps
- Relationships: Belongs to one Short, has many JobAttempts

**Script**:
- Represents the generated narrative script for a short
- Attributes: ID, short video ID, hook text, concept sections, example section, CTA text, total duration, visual descriptions JSON
- Relationships: Belongs to one Short Video

**Scene**:
- Represents a single visual scene within a short
- Attributes: ID, short video ID, sequence number, visual description, image URL, text overlay, duration, transition type
- Relationships: Belongs to one Short Video

**User Engagement**:
- Like: ID, user ID, short video ID, timestamp
- Comment: ID, user ID, short video ID, parent comment ID (for replies), text, timestamp
- View Event: ID, user ID (optional for anonymous), short video ID, watch duration, completed (boolean), timestamp

**Analytics Aggregate**:
- Per-short metrics: short video ID, view count, unique viewers, average watch duration, completion rate, CTR to lesson
- Daily totals: date, jobs completed, total cost, average cost per video, success rate

## Success Criteria

### Measurable Outcomes

**Generation Quality and Cost**:
- **SC-001**: System generates a complete short video from lesson within 5 minutes of request
- **SC-002**: Generated shorts maintain average cost of $0.006 or less per video
- **SC-003**: 95% of generated shorts pass quality review (no visual artifacts, clear audio, accurate content)
- **SC-004**: System can process 100 generation jobs in parallel without degradation

**User Engagement**:
- **SC-005**: 70% of users who start a short watch it to completion
- **SC-006**: 15-25% of short viewers click through to read the full lesson
- **SC-007**: 5-10% of users share shorts externally (link copy or download)
- **SC-008**: Users watch an average of 5+ shorts per session

**Learning Impact**:
- **SC-009**: Students who watch shorts before lessons complete lessons 25% faster than those who don't
- **SC-010**: Quiz scores improve by minimum 10% for concepts reinforced through shorts
- **SC-011**: 80% of users report shorts help them decide which lessons to prioritize

**Scale and Performance**:
- **SC-012**: System can generate shorts for all 1000+ lessons within 30 days of batch initiation
- **SC-013**: Shorts feed loads first video within 2 seconds on 4G connections
- **SC-014**: Video playback has zero buffering for users on broadband connections
- **SC-015**: System maintains 99.5% uptime for generation pipeline and feed delivery

**Operational Efficiency**:
- **SC-016**: Content administrators can trigger batch generation of 50 lessons with single click
- **SC-017**: Dashboard displays real-time progress updates with <1 second latency
- **SC-018**: Failed jobs can be retried with single click, with 80% success rate on retry

## Assumptions

**Content Availability**:
- All lesson content exists in markdown format at predictable file paths
- Lessons contain sufficient content (headings, paragraphs, code) to extract meaningful concepts
- Lesson metadata (title, difficulty, tags) is accessible

**API Reliability and Pricing**:
- Google Gemini 2.0 Flash API maintains current pricing ($0.075/M input tokens)
- Flux.1 or Stable Diffusion API remains available at comparable pricing
- Edge-TTS remains free or low-cost for foreseeable future
- API rate limits allow for planned generation volume

**User Behavior**:
- Learners prefer 60-90 second format for introductory/reinforcement content
- Short-form consumption increases long-form content engagement
- TikTok-style UI is familiar and comfortable for target audience

**Technical Infrastructure**:
- Existing authentication system can be extended for short video permissions
- CDN can store and deliver ~1000 video files (estimated 2-5 GB total)
- Database can scale to handle millions of view events and engagement records

**Quality Expectations**:
- AI-generated visuals of "very good" quality are sufficient for educational content
- Synthesized voice quality from Edge-TTS meets minimum standards
- Minor content imperfections are acceptable given cost constraints

**Cost Budget**:
- Monthly generation budget of $50-100 is acceptable for initial 1000 shorts
- Ongoing costs for new lessons ($6-30/month for 1000 lessons) are sustainable
- CDN bandwidth costs remain under $50/month at projected usage

## Constraints

**Cost Limitations**:
- Maximum $0.006 per generated short video (hard limit)
- Monthly generation budget not to exceed $100 without explicit approval
- Caching must reduce repeat generation costs by minimum 30%

**Quality Standards**:
- All shorts must pass basic quality check (no corrupted videos, clear audio, readable text)
- Scripts must accurately represent lesson content (no hallucinations)
- Visuals must be appropriate to lesson domain (no distracting or mismatched images)

**Technical Limitations**:
- Generation jobs must complete within 10 minutes (timeout limit)
- Video files must not exceed 50MB each (storage and delivery constraint)
- Feed must support 100 concurrent viewers without performance degradation

**Content Boundaries**:
- Only generate shorts from published lessons (not drafts or future content)
- Maximum 1 short per lesson (no variations or A/B testing in MVP)
- Shorts focus on conceptual understanding, not comprehensive coverage

**Scope Exclusions** (What we're NOT building):
- Live streaming or real-time video editing
- User-generated short uploads (only system-generated from lessons)
- Advanced video editing features (trimming, filters, effects by users)
- Multi-language support in MVP (English only initially)
- Social features beyond basic engagement (no follows, profiles, direct messages)
- Monetization features (no ads, no premium shorts)

## Dependencies

**External Services**:
- Google Gemini 2.0 Flash API for script generation
- Flux.1 or Stable Diffusion API (via Replicate) for image generation
- Microsoft Edge-TTS API for narration
- Cloudflare R2 or Backblaze B2 for video storage and CDN

**Internal Systems**:
- Content API for lesson metadata and markdown content
- Authentication system for user identification and permissions
- Progress API for tracking lesson completion and quiz scores
- Existing analytics infrastructure for event tracking

**Content Structure**:
- Lesson files follow predictable directory structure
- Markdown parsing can extract structured content reliably
- Lesson frontmatter contains necessary metadata (title, difficulty, tags)

## Open Questions

**Content Quality Validation**:
- How do we measure "accurate representation" of lesson content in generated scripts?
- What is the acceptable threshold for visual relevance matching?
- How do we detect and handle hallucinations in generated content?

**Generation Priority**:
- Which lessons should get shorts first? (Most viewed? Most recent? Specific parts?)
- Should we regenerate shorts when lesson content changes significantly?

**Engagement Metrics**:
- What is the target watch-through rate we consider "successful"?
- How do we correlate short views with lesson completion in analytics?

[No critical blockers - can proceed with reasonable defaults and iterate]
