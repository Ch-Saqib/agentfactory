# Student Engagement Features

**Status**: Draft
**Level**: SDD Level 2 (Spec-Anchored)
**Related**: progress-api, study-mode-api, learn-app
**Effort**: 8-10 weeks (all 4 features)

---

## Problem

The AI Agent Factory book has solid learning content and basic gamification (XP, badges, leaderboards), but lacks features that drive daily engagement, social learning, and personalized learning paths. Students have little reason to return daily, no visual roadmap of their journey, no social accountability, and no AI-powered guidance for what to review next.

**User Symptoms**:
- Irregular learning patterns — long gaps between sessions
- Low completion rates on advanced chapters
- No sense of progress toward concrete goals
- No peer comparison beyond global leaderboard
- Passive reading without checkpoint verification

---

## Solution

Four interconnected features that leverage existing infrastructure:

1. **Daily Challenges** — Gamified daily/weekly goals tied to XP bonuses
2. **Achievement Roadmap** — Visual skill tree showing learning paths
3. **Study Buddies** — Social learning with friends and shared XP
4. **AI Learning Features** — Knowledge checkpoints + Smart Review scheduler

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Challenge rotation | Daily auto-rotate at midnight UTC | Creates global "same challenge" experience; reduces admin overhead |
| Challenge types | Quiz, lessons, flashcards, mixed | Leverages existing activity types; no new content formats |
| Roadmap visualization | React Flow (@xyflow/react) | Industry standard for skill trees; built-in zoom/pan; ~120KB gzipped; strong TypeScript support |
| Friend discovery | Username search only (v1) | Privacy-preserving; avoids contact book permission issues |
| Buddy XP bonus | +10 XP when both complete same activity | Social accountability reward; small enough to prevent farming |
| Checkpoint triggering | Scroll position (50%, 75%) + lesson tags | Non-intrusive; lets users read before checking understanding |
| Review scheduler | FSRS-style algorithm + weak area detection | Science-backed retention; personalized to user's performance |
| AI checkpoint questions | AI-generated per lesson (v1) | Scales to 100+ lessons; pre-written questions are maintenance burden |

---

## Data Model

### 1. Daily Challenges

```sql
-- Daily challenge definitions (auto-generated or curated)
CREATE TABLE daily_challenges (
    id              SERIAL PRIMARY KEY,
    date            DATE NOT NULL UNIQUE,
    challenge_type  VARCHAR NOT NULL, -- 'quiz', 'lessons', 'flashcards', 'streak', 'mixed'
    config          JSONB NOT NULL,   -- Flexible per-type config
    xp_bonus        INTEGER NOT NULL DEFAULT 50,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User progress on challenges
CREATE TABLE user_challenge_progress (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id),
    challenge_id    INTEGER NOT NULL REFERENCES daily_challenges(id),
    progress        JSONB NOT NULL DEFAULT '{}',
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at    TIMESTAMPTZ,
    xp_earned       INTEGER NOT NULL DEFAULT 0,
    created_at      TMSTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, challenge_id)
);

CREATE INDEX ix_user_challenges_user_date
    ON user_challenge_progress (user_id, created_at DESC);
```

### 2. Achievement Roadmap

```sql
-- Skill tree nodes
CREATE TABLE achievement_nodes (
    id              VARCHAR PRIMARY KEY,  -- e.g. "part_01_foundations", "ch01_complete"
    name            VARCHAR NOT NULL,
    description     TEXT,
    category        VARCHAR NOT NULL, -- 'part', 'chapter', 'milestone', 'capstone'
    part_number     INTEGER,
    chapter_slug    VARCHAR,
    parent_id       VARCHAR REFERENCES achievement_nodes(id),
    position_x      INTEGER NOT NULL,
    position_y      INTEGER NOT NULL,
    badge_id        VARCHAR REFERENCES badges(id), -- Optional: link to existing badge
    required_xp     INTEGER DEFAULT 0,
    required_badges TEXT[], -- Array of prerequisite node IDs
    created_at      TMSTAMPTZ NOT NULL DEFAULT NOW()
);

-- User's unlocked nodes
CREATE TABLE user_achievement_progress (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id),
    node_id         VARCHAR NOT NULL REFERENCES achievement_nodes(id),
    unlocked        BOOLEAN NOT NULL DEFAULT FALSE,
    unlocked_at     TMSTAMPTZ,
    UNIQUE(user_id, node_id)
);
```

### 3. Study Buddies

```sql
-- Friend relationships
CREATE TABLE friendships (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id),
    friend_id       VARCHAR NOT NULL REFERENCES users(id),
    status          VARCHAR NOT NULL DEFAULT 'pending', -- 'pending', 'accepted'
    created_at      TMSTAMPTZ NOT NULL DEFAULT NOW(),
    accepted_at     TMSTAMPTZ,
    UNIQUE(user_id, friend_id),
    CHECK (user_id != friend_id)
);

-- Shared activity tracking (for buddy XP)
CREATE TABLE shared_activities (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id),
    activity_type   VARCHAR NOT NULL, -- 'quiz', 'lesson', 'flashcard'
    activity_ref    VARCHAR NOT NULL, -- quiz_id, lesson_path, deck_id
    buddy_id        VARCHAR REFERENCES users(id),
    xp_bonus        INTEGER NOT NULL DEFAULT 10,
    created_at      TMSTAMPTZ NOT NULL DEFAULT NOW(),
    date            DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX ix_friendships_user ON friendships (user_id, status);
CREATE INDEX ix_shared_activities_date ON shared_activities (date, activity_ref);
```

### 4. AI Learning Features

```sql
-- Knowledge checkpoint questions (AI-generated or curated)
CREATE TABLE checkpoint_questions (
    id              SERIAL PRIMARY KEY,
    lesson_path     VARCHAR NOT NULL,
    position_pct    INTEGER NOT NULL, -- When to trigger (0-100% through lesson)
    question        TEXT NOT NULL,
    options         JSONB NOT NULL,    -- { "A": "...", "B": "...", "C": "...", "D": "..." }
    correct_answer  VARCHAR NOT NULL,  -- "A", "B", "C", or "D"
    explanation     TEXT,
    ai_generated    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TMSTAMPTZ NOT NULL DEFAULT NOW()
);

-- User checkpoint responses
CREATE TABLE user_checkpoint_attempts (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id),
    checkpoint_id   INTEGER NOT NULL REFERENCES checkpoint_questions(id),
    answer          VARCHAR NOT NULL,
    correct         BOOLEAN NOT NULL,
    created_at      TMSTAMPTZ NOT NULL DEFAULT NOW()
);

-- Review recommendations (smart scheduler output)
CREATE TABLE review_reminders (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id),
    item_type       VARCHAR NOT NULL, -- 'lesson', 'quiz', 'flashcard'
    item_ref        VARCHAR NOT NULL,
    due_date        DATE NOT NULL,
    priority        INTEGER NOT NULL DEFAULT 5, -- 1-10, higher = more urgent
    reason          VARCHAR, -- 'spaced_rep', 'weak_area', 'prerequisite'
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at    TMSTAMPTZ,
    created_at      TMSTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_checkpoints_lesson ON checkpoint_questions (lesson_path);
CREATE INDEX ix_review_reminders_user_date ON review_reminders (user_id, due_date);
```

---

## API

### Progress API Endpoints

#### Challenges

```
GET /api/v1/challenges/today
Response: { id, challenge_type, title, description, xp_bonus, progress, completed }

POST /api/v1/challenges/{challenge_id}/progress
Request: { progress: JSON }
Response: { progress, completed, xp_earned, new_badges }

GET /api/v1/challenges/history
Response: [{ date, challenge_type, completed, xp_earned }]
```

#### Roadmap

```
GET /api/v1/roadmap
Response: { nodes: [{ id, name, position, unlocked, locked_reason }], connections: [...] }

POST /api/v1/roadmap/sync
Response: { newly_unlocked: [...], total_unlocked, progress_pct }
```

#### Friends

```
POST /api/v1/friends/request
Request: { username_or_email: string }
Response: { friendship_id, status }

POST /api/v1/friends/{friend_id}/accept
Response: { friendship_id, status, xp_bonus_earned }

GET /api/v1/friends
Response: [{ id, username, display_name, avatar_url, total_xp, last_activity }]

GET /api/v1/friends/leaderboard
Response: { entries: [{ rank, friend, xp, badges }], my_rank }
```

#### Review

```
GET /api/v1/review/queue
Response: { items: [{ id, item_type, item_ref, priority, reason, due_date }] }

POST /api/v1/review/{item_id}/complete
Response: { xp_earned, streak_updated }
```

### Study Mode API Endpoints

#### Checkpoints

```
POST /checkpoint/verify
Request: { checkpoint_id: number, answer: string, lesson_path: string }
Response: { correct, explanation, xp_bonus, next_checkpoint_at }
```

---

## Frontend Components

### Daily Challenges

```tsx
// apps/learn-app/src/components/challenges/
DailyChallengeCard.tsx      // Hero card on dashboard/home
ChallengeProgress.tsx       // Progress ring/steps
ChallengeCompleteModal.tsx  // Celebration modal on completion
```

### Achievement Roadmap

```tsx
// apps/learn-app/src/components/roadmap/
AchievementRoadmap.tsx      // Main interactive skill tree (React Flow)
RoadmapNode.tsx             // Individual node component
RoadmapLegend.tsx           // Filter by category/progress
```

### Study Buddies

```tsx
// apps/learn-app/src/components/friends/
FriendCard.tsx              // Mini profile card
FriendList.tsx              // List of friends with activity
FriendsLeaderboard.tsx      // Side-by-side comparison
AddFriendModal.tsx          // Friend request flow
FriendActivityFeed.tsx      // Recent buddy activity
```

### AI Learning

```tsx
// apps/learn-app/src/components/checkpoints/
KnowledgeCheckpoint.tsx     // Inline quiz popup

// apps/learn-app/src/components/review/
ReviewQueue.tsx             // List of recommended reviews
ReviewCard.tsx              // Individual review item
```

---

## Challenge Templates

Daily challenges are generated from templates with randomized parameters:

```python
# apps/progress-api/src/progress_api/services/challenges/templates.py

CHALLENGE_TEMPLATES = {
    "quiz_master": {
        "type": "quiz",
        "title": "Quiz Master",
        "description": "Score {min_score}%+ on any quiz from Part {part_num}",
        "config": {"min_score": [80, 85, 90], "parts": [1, 2, 3, 4, 5, 6]},
        "xp_bonus": 50
    },
    "learning_spree": {
        "type": "lessons",
        "title": "Learning Spree",
        "description": "Complete {count} lessons today",
        "config": {"count": [3, 5, 7]},
        "xp_bonus": 30
    },
    "memory_keeper": {
        "type": "flashcards",
        "title": "Memory Keeper",
        "description": "Review {count} flashcards with {accuracy}%+ accuracy",
        "config": {"count": [20, 30, 50], "accuracy": [70, 80, 90]},
        "xp_bonus": 40
    },
    "streak_protector": {
        "type": "streak",
        "title": "Streak Protector",
        "description": "Complete any activity to maintain your streak",
        "config": {"any_activity": 1},
        "xp_bonus": 20
    },
    "mixed_monday": {
        "type": "mixed",
        "title": "Mixed Monday",
        "description": "Complete a quiz AND 2 lessons AND review flashcards",
        "config": {"quiz": 1, "lessons": 2, "flashcards": 1},
        "xp_bonus": 75
    }
}
```

**Auto-generation**: A daily cron job (or manual trigger) generates `daily_challenges` rows 7 days in advance using randomized template parameters.

---

## Roadmap Structure

The skill tree mirrors the book structure:

```
Level 1: Parts (9 total)
├── Part 1: General Agents Foundations
├── Part 2: Applied Agent Workflows
├── Part 3: SDD-RI Fundamentals
├── Part 4: Programming in the AI Era
├── Part 5: Building Custom Agents
├── Part 6: AI Cloud-Native Development
├── Part 7: Turing LLMOps
├── Part 8: TypeScript Realtime
└── Part 9: Realtime Voice Agents

Level 2: Chapters (children of parts)
Level 3: Milestones (quiz 80%+, all lessons read, flashcards complete)
Level 4: Capstone badges (complete all quizzes in part)
```

Unlock rules:
- XP threshold unlocks next part
- Complete all chapter nodes → part complete badge
- Linear progression through parts (no skipping)

---

## Smart Review Algorithm

Review items are generated using a modified FSRS-style scheduler:

```python
# apps/progress-api/src/progress_api/services/review/scheduler.py

async def generate_review_queue(user_id: str) -> List[ReviewItem]:
    """Generate personalized review recommendations."""

    items = []

    # 1. Spaced repetition: lessons/quizzes due for review
    # Based on last study date + interval formula
    due_items = await get_due_spaced_rep_items(user_id)
    for item in due_items:
        items.append(ReviewItem(
            item_type=item.type,
            item_ref=item.ref,
            priority=7,
            reason="spaced_rep",
            due_date=item.due_date
        ))

    # 2. Weak areas: chapters with <70% quiz scores
    weak_chapters = await get_weak_chapters(user_id, threshold=70)
    for chapter in weak_chapters:
        items.append(ReviewItem(
            item_type="quiz",
            item_ref=chapter.slug,
            priority=8,
            reason="weak_area",
            due_date=today()
        ))

    # 3. Prerequisites: upcoming lessons require earlier knowledge
    next_lesson = await get_next_lesson(user_id)
    if next_lesson:
        prerequisites = await get_prerequisite_lessons(next_lesson.slug)
        for prereq in prerequisites:
            if not await is_lesson_completed(user_id, prereq.slug):
                items.append(ReviewItem(
                    item_type="lesson",
                    item_ref=prereq.slug,
                    priority=9,
                    reason="prerequisite",
                    due_date=today()
                ))

    return sorted(items, key=lambda x: (x.due_date, -x.priority))
```

---

## Files to Create

### Progress API (new)

```
src/progress_api/routes/
├── challenges.py
├── roadmap.py
├── friends.py
└── review.py

src/progress_api/services/
├── challenges/
│   ├── templates.py
│   └── engine.py
├── roadmap/
│   └── definition.py
├── friends/
│   └── bonus.py
└── review/
    └── scheduler.py

src/progress_api/schemas/
├── challenges.py
├── roadmap.py
├── friends.py
└── review.py

src/progress_api/models/
├── challenge.py
├── roadmap.py
├── friendship.py
└── review.py

migrations/
├── 002_daily_challenges.sql
├── 003_achievement_roadmap.sql
├── 004_friendships.sql
├── 005_checkpoints.sql
└── 006_review_reminders.sql
```

### Learn App (new)

```
src/components/challenges/
├── DailyChallengeCard.tsx
├── ChallengeProgress.tsx
└── ChallengeCompleteModal.tsx

src/components/roadmap/
├── AchievementRoadmap.tsx
├── RoadmapNode.tsx
└── RoadmapLegend.tsx

src/components/friends/
├── FriendCard.tsx
├── FriendList.tsx
├── FriendsLeaderboard.tsx
├── AddFriendModal.tsx
└── FriendActivityFeed.tsx

src/components/checkpoints/
└── KnowledgeCheckpoint.tsx

src/components/review/
├── ReviewQueue.tsx
└── ReviewCard.tsx

src/lib/
└── engagement-api.ts  # API client functions
```

### Study Mode API (new)

```
src/study_mode_api/routes/
└── checkpoints.py
```

---

## Clarifications

### Session 2026-03-02

- Q: What are the performance targets for new engagement features? → A: API endpoints: <200ms p95, Page loads: <1s, Roadmap render: <500ms
- Q: What is the authorization model for viewing progress and friendships? → A: Users view only own progress; friendships bidirectional (mutual accept); friends see each other's activity; no public profile discovery
- Q: What are the rate limits for new endpoints? → A: Friend requests: 10/hour; Challenge updates: 60/minute; Roadmap sync: 30/minute; Review queue: 10/minute
- Q: What is the data retention policy for new tables? → A: Checkpoint attempts: 90 days; Shared activities: 180 days; Challenge progress: 365 days; Roadmap progress: forever
- Q: Which visualization library for the roadmap skill tree? → A: React Flow - Declarative, React-native, built-in zoom/pan, ~120KB gzipped

---

## Non-Functional Requirements

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API latency (p95) | <200ms | All new engagement endpoints |
| Page load time | <1s | Challenge card, roadmap, friends list |
| Roadmap render | <500ms | Initial skill tree visualization |
| Review queue gen | <1s | Smart scheduler queue generation |

### Scalability

| Dimension | Assumption | Notes |
|-----------|------------|-------|
| Concurrent users | 1,000 | Baseline for v1 |
| Daily active users | 5,000 | Serves as capacity planning target |
| Challenge rows | 365/year | Auto-generated 7 days ahead |
| Friendship edges | 50 avg/user | Assumes students connect with classmates |

### Observability

- All new endpoints log: `user_id`, `operation`, `duration_ms`, `status`
- Errors logged with full stack trace and request context
- Metrics exported for: challenge_completions, roadmap_unlocks, friend_requests, review_generations

### Error Handling

- **API failures**: Return 500 with generic error message; log details; never expose internal state
- **Empty states**: Show friendly UI with CTA (e.g., "No friends yet — add classmates!")
- **Loading states**: Skeleton screens for cards, spinners for actions
- **Network timeout**: 30s default; retry with exponential backoff for non-idempotent operations

### Security & Authorization

**Authentication**: All new endpoints require valid JWT via existing Better Auth SSO. No anonymous access.

**Authorization Model** (privacy-first):

| Feature | Access Rule |
|---------|-------------|
| Challenges | Users view only their own challenges; no cross-user visibility |
| Roadmap | Users view only their own roadmap progress; no public leaderboards for roadmap |
| Friends | Bidirectional only; both users must accept; username search exists for discovery |
| Friends Leaderboard | Users see only their friends; no global browsing |
| Checkpoints | Users view only their own checkpoint history |
| Review Queue | Users view only their own review recommendations |

**Friendship Lifecycle**:
1. User A searches for User B by username → `POST /friends/request`
2. User B sees pending request → can accept or decline
3. Once accepted, both users see each other in friends list
4. Either user can remove friendship (not in v1)

**Data Visibility Matrix**:

| Data Type | Owner | Friends | Public |
|-----------|-------|---------|--------|
| XP total | ✓ | ✓ | ✗ |
| Roadmap progress | ✓ | ✗ | ✗ |
| Challenge history | ✓ | ✗ | ✗ |
| Friend activity | ✓ | ✓ | ✗ |
| Badge collection | ✓ | ✓ | ✓ (global leaderboard only) |

### Rate Limiting

All new endpoints use Redis-based rate limiting (existing pattern: `api_infra.core.rate_limit`).

| Endpoint | Limit | Window | Rationale |
|----------|-------|--------|-----------|
| `POST /friends/request` | 10 | 1 hour | Prevent friendship spam |
| `POST /challenges/{id}/progress` | 60 | 1 minute | Allow rapid progress updates |
| `POST /roadmap/sync` | 30 | 1 minute | Prevent excessive sync calls |
| `GET /review/queue` | 10 | 1 minute | Limit queue refreshes |
| `POST /checkpoint/verify` | 20 | 1 day | Match existing chat rate limit |

**Rate Limit Response** (exceeded):

```json
{
  "error": "Rate limit exceeded",
  "limit": 10,
  "reset_after_ms": 3600000,
  "message": "Too many friend requests. Try again later."
}
```

### Data Retention

High-volume tables have retention policies to prevent unbounded growth:

| Table | Retention | Rationale |
|-------|-----------|-----------|
| `user_checkpoint_attempts` | 90 days | Analytics only; individual answers not needed long-term |
| `shared_activities` | 180 days | Buddy XP calculation window |
| `user_challenge_progress` | 365 days | Challenge history for user reference |
| `daily_challenges` | 365 days | Archive for analytics/template improvement |
| `friendships` | Forever | Core relationship data |
| `user_achievement_progress` | Forever | User's unlocked nodes |
| `achievement_nodes` | Forever | Static roadmap definition |
| `checkpoint_questions` | Forever | Question bank (may be cached) |
| `review_reminders` | 30 days after completed | Completed reviews; active queue kept indefinitely |

**Implementation**: PostgreSQL scheduled job via `pg_cron` extension:

```sql
-- Run daily at 2 AM UTC
DELETE FROM user_checkpoint_attempts WHERE created_at < NOW() - INTERVAL '90 days';
DELETE FROM shared_activities WHERE created_at < NOW() - INTERVAL '180 days';
DELETE FROM user_challenge_progress WHERE created_at < NOW() - INTERVAL '365 days';
DELETE FROM daily_challenges WHERE date < CURRENT_DATE - INTERVAL '365 days';
DELETE FROM review_reminders WHERE completed = TRUE AND completed_at < NOW() - INTERVAL '30 days';
```

---

## Constraints

1. **No new infrastructure** — reuse existing progress-api, study-mode-api, PostgreSQL, Redis
2. **No breaking changes** — all features additive, existing flows unchanged
3. **Privacy-first** — friends require mutual opt-in; no automatic social connections
4. **Mobile-responsive** — roadmap must work on small screens (zoom/pan)
5. **Offline-first for flashcards** — FSRS stays in localStorage; server only gets aggregates
6. **No new auth flows** — use existing Better Auth SSO/JWT
7. **No external dependencies for roadmap** — use React Flow or D3 (already in monorepo)

---

## Success Criteria

### Daily Challenges
- [ ] Challenge appears on dashboard at midnight UTC
- [ ] Completing challenge awards bonus XP + badge progress
- [ ] Challenge history shows past 7 days
- [ ] Streak-protector challenge prevents streak loss

### Achievement Roadmap
- [ ] Visual skill tree displays all 9 parts + chapters
- [ ] Nodes unlock automatically based on existing progress
- [ ] Clicking node navigates to relevant content
- [ ] Progress percentage displays overall completion

### Study Buddies
- [ ] User can send/receive friend requests
- [ ] Friends leaderboard shows side-by-side comparison
- [ ] Buddy XP awarded when both complete same activity
- [ ] Friend activity feed shows recent completions

### AI Learning Features
- [ ] Checkpoint questions appear at 50%, 75% scroll position
- [ ] Review queue prioritizes weak areas + spaced repetition
- [ ] Marking review complete updates queue
- [ ] Checkpoint answers stored for analytics

---

## Open Questions

The following remain open and will be resolved during planning/implementation:

1. **Challenge curation vs auto-generation** — Start with auto, add curated for special events? (deferred to planning)
2. **Friend request notifications** — Email? In-app only? (v1: in-app only - noted in spec)
3. **Checkpoint question quality** — AI-generated vs pre-written? (v1: AI with fallback - noted in spec)
4. **Review queue frequency** — Daily refresh vs real-time? (v1: daily refresh - noted in spec)

---

## Implementation Phases

| Phase | Duration | Feature | Deliverable |
|-------|----------|---------|-------------|
| 1 | 2 weeks | Daily Challenges | DB + API + frontend card |
| 2 | 3 weeks | Achievement Roadmap | Roadmap data + visualization |
| 3 | 2 weeks | Study Buddies | Friend system + social feed |
| 4 | 2 weeks | Checkpoints | Lesson integration + AI questions |
| 5 | 2 weeks | Smart Review | Scheduler + queue UI |

**Total**: 11 weeks (can run phases 3-5 in parallel)
