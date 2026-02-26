# Learner Profile System — Specification v1.0

**Status:** Phase 3 — Refinement Complete (all QA blockers resolved)
**Date:** 2026-02-26
**Scope:** Profile CRUD, onboarding, storage, PHM sync, progressive profiling
**Out of Scope:** Personalization engine (LLM calls, content transformation) — separate build

---

## 1. System Overview

### What We're Building

The Learner Profile System is the foundational data layer for all AI-native learning features in AgentFactory. It stores, manages, and serves learner profiles that downstream systems (TutorClaw, Teach Me Mode, Personalized Content Tab) consume to personalize the learning experience.

### System Responsibilities

1. **Profile CRUD** — Create, read, update, and delete learner profiles
2. **Onboarding** — Hybrid wizard (form + optional AI follow-up) that collects the minimum viable profile
3. **Progressive Profiling** — Infer and update profile fields from learner behavior over time
4. **PHM Sync** — Auto-update profile from tutoring session data (Appendix A mapping)
5. **Profile Serving** — Expose profiles via API for downstream personalization consumers
6. **GDPR Compliance** — Hard delete, consent tracking, data retention

### What's NOT This System

- **Personalization Engine** — The LLM-based content transformation system that takes profile + lesson → personalized output. Separate build, separate service.
- **Assessment/Grading** — Profile drives presentation, not evaluation
- **Content Authoring** — We personalize existing lessons, not create new ones
- **ML-based Inference** — Progressive profiling in v1 is rule-based, not ML

### Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (learn-app)                     │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────────┐   │
│  │ Onboarding   │  │ Personalized    │  │ TutorClaw /       │   │
│  │ Wizard       │  │ Content Tab     │  │ Teach Me Mode     │   │
│  └──────┬───────┘  └───────┬─────────┘  └──────┬────────────┘   │
└─────────┼──────────────────┼───────────────────┼────────────────┘
          │                  │                   │
          │ JWT Bearer       │ JWT Bearer        │ JWT Bearer
          ▼                  ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNER PROFILE API (this service)             │
│                    Port 8004                                      │
│                                                                   │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────────┐   │
│  │ Profile CRUD │  │ Onboarding      │  │ PHM Sync          │   │
│  │ /api/v1/     │  │ State mgmt      │  │ /me/sync-from-phm │   │
│  │ profiles/    │  │                  │  │                    │   │
│  └──────┬───────┘  └─────────────────┘  └──────┬────────────┘   │
│         │                                       │                 │
│         ▼                                       ▼                 │
│  ┌──────────────┐                        ┌───────────────────┐   │
│  │ PostgreSQL   │                        │ httpx Client      │   │
│  │ (Neon)       │                        │ (Study Mode API)  │   │
│  │ profiles     │                        │                    │   │
│  └──────────────┘                        └───────────────────┘   │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────┐                                                │
│  │ Redis Cache  │                                                │
│  │ (shared)     │                                                │
│  └──────────────┘                                                │
└──────────────────────────────────────────────────────────────────┘

EXTERNAL DEPENDENCIES:
┌──────────────┐    ┌────────────────┐    ┌────────────────┐
│ SSO          │    │ Content API    │    │ Study Mode API │
│ (JWKS auth)  │    │ (lesson source)│    │ (PHM sessions) │
│ port 3001    │    │ port 8003      │    │ port 8000      │
└──────────────┘    └────────────────┘    └────────────────┘
```

- **SSO** → JWT/JWKS authentication. `learner_id = user.sub` from JWT (no mapping table)
- **Content API** → Serves lesson content. Frontend orchestrates: gets lesson from content-api, gets profile from this service, sends both to personalization engine
- **Study Mode API** → PHM session data. This service pulls PHM data to update profiles
- **Redis** → Shared instance. Profile cache with `lp:` namespace prefix

---

## 2. Schema v1.1

This is the evolved schema incorporating all Phase 1 research findings and user decisions. Changes from v1.0 are marked with `[NEW]`, `[MODIFIED]`, or `[REMOVED]`.

### SECTION 1 — Identity and Context

```json
{
  "learner_id": "string — UUID v4, auto-generated on profile creation",
  "name": "string | null",
  "profile_created": "ISO-8601 datetime",
  "last_updated": "ISO-8601 datetime",
  "profile_version": "1.1",
  "consent_given": "boolean — GDPR consent for profile data storage",
  "consent_date": "ISO-8601 datetime | null"
}
```

| Field | Status | Notes |
|---|---|---|
| `learner_id` | MODIFIED | Now explicitly UUID v4 (was ambiguous "uuid or human-readable") |
| `last_updated` | `[NEW]` | Staleness detection. Updated on every profile modification |
| `consent_given` | `[NEW]` | GDPR requirement. Must be `true` for profile to be stored |
| `consent_date` | `[NEW]` | When consent was granted |

### SECTION 2 — Expertise Profile

```json
{
  "expertise": {
    "domain": [
      {
        "level": "none | beginner | intermediate | advanced | expert",
        "domain_name": "string | null — required when level is beginner or above",
        "is_primary": "boolean — true for the primary domain",
        "notes": "string | null (max 300 chars)"
      }
    ],
    "programming": {
      "level": "none | beginner | intermediate | advanced | expert",
      "languages": ["string"],
      "notes": "string | null (max 300 chars)"
    },
    "ai_ml": {
      "level": "none | beginner | intermediate | advanced | expert",
      "notes": "string | null (max 300 chars)"
    },
    "business": {
      "level": "none | beginner | intermediate | advanced | expert",
      "notes": "string | null (max 300 chars)"
    },
    "subject_specific": {
      "topics_already_mastered": [
        {
          "topic": "string",
          "treatment": "reference | skip"
        }
      ],
      "topics_partially_known": [
        {
          "topic": "string",
          "knowledge_state": "string (max 300 chars)"
        }
      ],
      "known_misconceptions": [
        {
          "topic": "string",
          "misconception": "string (max 500 chars)"
        }
      ]
    }
  }
}
```

| Field | Status | Notes |
|---|---|---|
| `domain` | MODIFIED | Now an **array** with `is_primary` flag (was single object) |
| `domain.domain_name` | MODIFIED | Nullable, required only when `level >= beginner` |
| `ai_ml.level` | MODIFIED | Enum standardized to `none\|beginner\|intermediate\|advanced\|expert` (was `conceptual`) |
| `topics_to_skip` | `[REMOVED]` | Merged into `topics_already_mastered` with `treatment: reference\|skip` |
| All `notes` fields | MODIFIED | Max 300 chars enforced |
| `known_misconceptions` | MODIFIED | Capped at 5 entries max |
| All expertise `level` defaults | MODIFIED | Default is `beginner` (was `intermediate`) |

### SECTION 3 — Professional Context

```json
{
  "professional_context": {
    "current_role": "string | null (max 100 chars)",
    "industry": "string | null (max 100 chars)",
    "organization_type": "string | null — e.g. 'enterprise', 'startup', 'university', 'freelance'",
    "team_context": "string | null (max 200 chars)",
    "real_projects": [
      {
        "project_name": "string (max 100 chars)",
        "description": "string (max 500 chars)"
      }
    ],
    "tools_in_use": ["string (max 50 chars each, max 20 items)"],
    "constraints": "string | null (max 300 chars)"
  }
}
```

| Field | Status | Notes |
|---|---|---|
| `real_projects[].relevance` | `[REMOVED]` | Engine infers relevance from description + lesson topic |
| `real_projects` | MODIFIED | Capped at 5 entries max |
| `tools_in_use` | MODIFIED | Max 20 items, each max 50 chars |
| All freetext fields | MODIFIED | Character limits enforced |

### SECTION 4 — Goals and Motivation

```json
{
  "goals": {
    "primary_learning_goal": "string (max 500 chars)",
    "secondary_goals": ["string (max 200 chars each, max 5 items)"],
    "urgency": "low | medium | high",
    "urgency_note": "string | null (max 200 chars)",
    "career_goal": "string | null (max 300 chars)",
    "immediate_application": "string | null (max 300 chars)"
  }
}
```

| Field | Status | Notes |
|---|---|---|
| `urgency_context` | MODIFIED | Renamed to `urgency_note` to signal it's supplementary |
| All freetext fields | MODIFIED | Character limits enforced |

### SECTION 5 — Communication Preferences

```json
{
  "communication": {
    "language_complexity": "plain | professional | technical | expert",
    "preferred_structure": "examples-first | theory-first | story-narrative | reference-lookup | problem-first",
    "verbosity": "concise | moderate | detailed",
    "analogy_domain": "string | null (max 100 chars)",
    "tone": "formal | professional | conversational | peer-to-peer",
    "wants_summaries": "boolean",
    "wants_check_in_questions": "boolean",
    "format_notes": "string | null (max 200 chars)"
  }
}
```

| Field | Status | Notes |
|---|---|---|
| No structural changes | — | Strongest section per Schema Analyst audit. Defaults added to Appendix B |

**Defaults (Appendix B updates):**
- `language_complexity` → `professional`
- `preferred_structure` → `examples-first`
- `verbosity` → `moderate`
- `tone` → `professional`
- `wants_summaries` → `true`
- `wants_check_in_questions` → `true`

### SECTION 6 — Content Delivery Preferences

```json
{
  "delivery": {
    "output_format": "prose | structured-with-headers | mixed",
    "target_length": "short | medium | long | match-source",
    "include_code_samples": "boolean",
    "code_verbosity": "minimal | annotated | fully-explained",
    "include_visual_descriptions": "boolean",
    "language": "string — default 'English'",
    "language_proficiency": "native | fluent | intermediate | basic"
  }
}
```

| Field | Status | Notes |
|---|---|---|
| `target_length` | MODIFIED | Clean enum values (word count ranges moved to documentation, not stored) |
| `visual_description_notes` | `[REMOVED]` | Absorbed into accessibility section |
| `language_proficiency` | `[NEW]` | Separates "what language" from "how well they know it" |
| `include_code_samples` default | MODIFIED | Conditional: `false` when `programming.level == none`, `true` otherwise |
| `code_verbosity` | MODIFIED | Only relevant when `include_code_samples == true` (documented dependency) |

### SECTION 7 — Accessibility `[NEW SECTION]`

```json
{
  "accessibility": {
    "screen_reader": "boolean — default false",
    "cognitive_load_preference": "standard | reduced",
    "color_blind_safe": "boolean — default false",
    "dyslexia_friendly": "boolean — default false",
    "notes": "string | null (max 300 chars)"
  }
}
```

All fields optional. Defaults are conservative (standard, no special needs assumed). This section consolidates accessibility concerns that were previously scattered or missing.

### Field Resolution Rules (Cross-Field Dependencies)

| Rule | Condition | Behavior |
|---|---|---|
| `analogy_domain` fallback | Field is null | Use `professional_context.industry`. If also null, use generic everyday analogies |
| `include_code_samples` conditional default | `programming.level` is `none` or absent | Default to `false` |
| `code_verbosity` dependency | `include_code_samples` is `false` | `code_verbosity` is ignored |
| `domain_name` conditional | `domain.level` is `none` | `domain_name` should be null |
| Inferred `language_complexity` | Not set by learner | Derive from expertise levels (see Onboarding Inference Rules) |
| Inferred `tone` | Not set by learner | Derive from `language_complexity` |
| Inferred `code_verbosity` | Not set by learner | `programming.level: none→N/A, beginner→fully-explained, intermediate→annotated, advanced/expert→minimal` |

### Validation Rules

| Rule | Enforcement |
|---|---|
| All freetext fields | Max character limits as documented per field |
| All arrays | Max item limits as documented per field |
| `learner_id` | UUID v4 format |
| `profile_version` | Semver string, set by system (not user) |
| Expertise level enums | Must be one of: `none\|beginner\|intermediate\|advanced\|expert` |
| `consent_given` | Must be `true` for profile creation |
| `known_misconceptions` | Max 5 entries |
| `real_projects` | Max 5 entries |
| `domain` array | Max 5 entries, exactly one `is_primary: true` |
| Duplicate detection | `topics_already_mastered[].topic` — deduplicated, case-normalized |

### Security: Freetext Field Handling

All freetext fields (`notes`, `misconception`, `description`, `constraints`, `analogy_domain`, `format_notes`, `knowledge_state`, `accessibility.notes`) are potential prompt injection vectors when passed to downstream LLM-based systems.

**This system's responsibility:**
1. Enforce max character limits at API validation layer
2. Store values as-is (no sanitization at storage — that's the consumer's job)
3. Document in API contract that all freetext values are user-provided and MUST be sandwiched in consuming system prompts

**Consumer's responsibility (personalization engine, TutorClaw):**
1. Sandwich pattern: system instructions ABOVE and BELOW profile data
2. Inject profile fields as data, not as instructions
3. Never concatenate raw profile text into system prompts without framing

---

## 3. Personalization Engine Requirements (Separate Build — Schema Support)

This section documents what the schema must support for the future personalization engine. The engine is out of scope for this build, but schema design decisions were informed by these requirements.

### Five Personalization Dimensions

| Dimension | What Changes | Primary Schema Fields |
|---|---|---|
| **Vocabulary** | Word choice, jargon level, term definitions | `communication.language_complexity`, `expertise.*` |
| **Examples** | Analogies, case studies, illustration domain | `professional_context.*`, `communication.analogy_domain`, `expertise.domain` |
| **Depth** | Expansion vs compression of sections | `expertise.subject_specific.*`, `goals.*`, `communication.verbosity` |
| **Structure** | Organization, flow, formatting | `communication.preferred_structure`, `delivery.output_format`, `delivery.target_length` |
| **Tone** | Voice, register, interpersonal style | `communication.tone`, `communication.language_complexity` |

### Engine Invariants (Schema Must Support)

1. Every schema field drives at least one personalization dimension
2. Partial profiles produce progressively better output (never worse than no profile)
3. Personalization changes presentation, never accuracy
4. Conflict resolution follows: Invariants > Explicit preferences > Inferred/defaults > Source fidelity

### Engine Input Contract (What This API Serves)

The profile API serves the complete profile JSON. The consuming engine is responsible for:
- Applying transformation rules per field
- Resolving field conflicts
- Applying defaults for missing fields
- Generating the personalization manifest

Full transformation rules, conflict resolution matrix, quality gates, and worked examples are documented in `specs/learner-profile/research/engine-spec.md` (656 lines).

---

## 4. Onboarding Specification

### Approach: Hybrid (Option C)

Structured form for fields with clear answer spaces (dropdowns, selects) + optional AI conversation for open-ended enrichment.

### Onboarding Flow

**Phase 1: Goals (45-60 seconds)**
1. `goals.primary_learning_goal` — open text: "What do you want to achieve with Agent Factory?"
2. `goals.urgency` — 3-option select: Low / Medium / High

**Phase 2: Background (30-60 seconds)**
3. `expertise.programming.level` — 5-option dropdown
4. `expertise.ai_ml.level` — 5-option dropdown
5. `expertise.domain[0].level` + `domain_name` — dropdown + text input
6. `expertise.business.level` — 5-option dropdown

**Phase 3: Professional Context (20-45 seconds)**
7. `professional_context.current_role` — text input
8. `professional_context.industry` — text input / dropdown
9. `professional_context.organization_type` — dropdown (optional)

**Phase 4: AI Enrichment (optional, 0-5 minutes)**
After the form, an optional AI conversation enriches open-ended fields:
- "Tell me about a project you'd like to apply this to" → `real_projects`
- "Any specific career goals?" → `career_goal`
- "Anything you've already learned about AI?" → `subject_specific` fields

### Fields NEVER Asked in Onboarding (Inferred or Deferred)

| Field | Handling |
|---|---|
| `communication.language_complexity` | Inferred from expertise levels |
| `communication.preferred_structure` | Default `examples-first`, adjusted from engagement data |
| `communication.verbosity` | Inferred from expertise levels |
| `communication.tone` | Inferred from `language_complexity` |
| `communication.analogy_domain` | Inferred from `industry` |
| `delivery.*` | All defaults or inferred |
| `accessibility.*` | Settings page only (not onboarding) |
| `expertise.subject_specific.*` | Inferred from quiz performance and engagement |
| `known_misconceptions` | Detected through assessment, never asked |

### Inference Rules (Communication/Delivery from Expertise) — `[B-7 FIX]`

**Algorithm:** Take the **maximum** expertise level across `programming`, `ai_ml`, `domain[primary]`, and `business`. Map to communication/delivery fields using the table below. User-set values ALWAYS override inferences. Inferred values are stored in the DB on profile creation/update (not computed on-the-fly).

**When inference runs:** On profile creation (`POST /`), on section update (`PATCH /me/sections/expertise`), and on PHM sync. Inference does NOT overwrite fields the user has explicitly set.

**Override rule:** If a user manually sets `language_complexity = expert` but their expertise says `beginner`, the manual value sticks. Inferred values have a lower priority than explicit values. Track which fields were user-set vs inferred via a `_inferred_fields: list[str]` metadata array stored in the profile (not exposed in API responses).

| Max Expertise Level | Inferred `language_complexity` | Inferred `tone` | Inferred `verbosity` | Inferred `code_verbosity` | Inferred `include_code_samples` |
|---|---|---|---|---|---|
| `none` | `plain` | `conversational` | `detailed` | `fully-explained` | `false` |
| `beginner` | `plain` | `conversational` | `detailed` | `fully-explained` | `true` |
| `intermediate` | `professional` | `professional` | `moderate` | `annotated` | `true` |
| `advanced` | `technical` | `peer-to-peer` | `concise` | `minimal` | `true` |
| `expert` | `expert` | `peer-to-peer` | `concise` | `minimal` | `true` |

**Special cases:**
- If `programming.level = none` regardless of other expertise: `include_code_samples = false`, `code_verbosity = N/A`
- If `programming.level = beginner` but max expertise is `advanced` (e.g., domain expert learning to code): `language_complexity = professional` (not `technical`), but `code_verbosity = fully-explained`
- If `business.level = advanced` but `programming.level = none`: `language_complexity = professional` (business vocabulary, not technical)

### Skip Behavior

- Every section is skippable. "Skip for now" (de-emphasized text link, not button)
- Skipping applies defaults for that section (Appendix B)
- `consent_given` is the ONLY required field (GDPR)

### Onboarding Abandonment

- Save whatever was completed. Profile is valid even with 1 section
- Content served with defaults for missing sections
- Banner: "Profile X% complete — finish for better personalization"
- Profile settings page always accessible from user menu

### Progressive Profiling Triggers (v1)

| Trigger | What Gets Resurfaced | UX |
|---|---|---|
| After first lesson | "Was this the right level?" | In-lesson feedback widget (too easy / just right / too hard) |
| After 3 lessons | Communication preferences | Quick 2-option prompt ("More examples or more theory?") |
| When learner starts a project | Professional context | Project creation form collects `real_projects` |
| After quiz/assessment | `topics_already_mastered` | Auto-populated when assessment data available (no assessment system in this build — trigger activates when external assessment data is provided via API) |
| Manually anytime | All fields | "Edit profile" in settings |

### Onboarding State Tracking — `[B-4 FIX]`

**Onboarding phases map to schema sections as follows:**

| Onboarding Phase | Schema Section(s) Updated | Tracking Key |
|---|---|---|
| Phase 1: Goals | `goals` | `goals` |
| Phase 2: Background | `expertise` | `expertise` |
| Phase 3: Professional Context | `professional_context` | `professional_context` |
| Phase 4: AI Enrichment | `goals` (career_goal, immediate_application), `professional_context` (real_projects), `expertise` (subject_specific) | `ai_enrichment` |

**Sections NOT tracked in onboarding** (inferred or deferred): `communication`, `delivery`, `accessibility`. These are populated by inference rules or via the settings page.

The `onboarding_sections_completed` keys are the 4 **onboarding phases**, not the 7 schema sections:
```json
{
  "onboarding_sections_completed": {
    "goals": true,
    "expertise": true,
    "professional_context": false,
    "ai_enrichment": false
  },
  "onboarding_completed": false,
  "profile_completeness": 0.55
}
```

`next_section` in `OnboardingStatus` returns one of: `"goals"`, `"expertise"`, `"professional_context"`, `"ai_enrichment"`, or `null` (all complete).

---

## 5. Technical Specification

### Stack

| Component | Technology | Rationale |
|---|---|---|
| Framework | FastAPI 0.115+ | Matches content-api; async-native |
| ORM | SQLModel 0.0.22+ + SQLAlchemy 2.0 async | Type-safe, Pydantic integration |
| Database | PostgreSQL 16+ (Neon serverless) | JSONB support, zero ops |
| Async Driver | asyncpg | Fastest Python PG async driver |
| Migrations | Alembic 1.14+ | Standard, async support |
| Cache | Redis (shared instance) | Already deployed, `lp:` prefix |
| HTTP Client | httpx (async) | PHM sync client |
| Auth | api_infra/auth.py (shared) | JWT/JWKS, dev_mode bypass |
| Testing | pytest + pytest-asyncio + fakeredis + respx | Matches content-api |
| Port | 8004 | Next available |

### Project Structure

```
apps/learner-profile-api/
├── Dockerfile
├── pyproject.toml
├── project.json
├── src/
│   ├── api_infra/                  # Shared auth, rate limiting, Redis
│   └── learner_profile_api/
│       ├── main.py                 # FastAPI app, CORS, lifespan, health
│       ├── config.py               # pydantic-settings from env
│       ├── core/
│       │   ├── lifespan.py         # Startup: Redis + DB; Shutdown: close
│       │   └── database.py         # SQLModel async engine, session factory
│       ├── models/
│       │   └── profile.py          # SQLModel table models
│       ├── schemas/
│       │   └── profile.py          # Pydantic request/response models
│       ├── routes/
│       │   └── profile.py          # Profile CRUD + onboarding
│       └── services/
│           ├── profile_service.py  # Business logic, CRUD
│           ├── inference.py        # Communication/delivery inference rules
│           └── phm_client.py       # HTTP client for PHM sync
└── tests/
    ├── conftest.py
    ├── test_profile_crud.py
    ├── test_profile_routes.py
    ├── test_schema_validation.py
    ├── test_inference_rules.py
    └── e2e/
        ├── conftest.py
        ├── test_profile_flow.py
        └── test_onboarding_flow.py
```

### Database Schema (Hybrid: Core Columns + JSONB)

```python
class LearnerProfile(SQLModel, table=True):
    __tablename__ = "learner_profiles"

    # Identity (relational columns, indexed)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    learner_id: str = Field(index=True, unique=True, max_length=255)
    name: str | None = Field(default=None, max_length=255)
    profile_version: str = Field(default="1.1", max_length=10)

    # GDPR
    consent_given: bool = Field(default=False)
    consent_date: datetime | None = Field(default=None)

    # Profile Sections (JSONB)
    expertise: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))
    professional_context: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))
    goals: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))
    communication: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))
    delivery: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))
    accessibility: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))

    # Onboarding State
    onboarding_completed: bool = Field(default=False)
    onboarding_sections_completed: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))

    # Timestamps (M-8: use timezone-aware UTC, not deprecated utcnow)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Soft Delete (for normal ops; GDPR uses hard delete)
    deleted_at: datetime | None = Field(default=None)


class ProfileAuditLog(SQLModel, table=True):
    __tablename__ = "profile_audit_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    learner_id: str = Field(index=True, max_length=255)
    action: str = Field(max_length=50)  # created, updated, section_updated, deleted, gdpr_erased
    changed_sections: list[str] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'[]'")))
    previous_values: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))
    source: str = Field(max_length=50, default="api")  # api, onboarding, phm_sync, progressive, admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Indexes

```sql
CREATE UNIQUE INDEX idx_profiles_learner_id ON learner_profiles (learner_id);
CREATE INDEX idx_profiles_not_deleted ON learner_profiles (learner_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_audit_learner_id ON profile_audit_log (learner_id, created_at DESC);
```

### API Endpoints

All endpoints prefixed with `/api/v1/profiles`.

| Method | Path | Purpose | Auth | Success | Error |
|---|---|---|---|---|---|
| `GET` | `/health` | Health check (Redis + DB ping) | None | 200 | 503 |
| `POST` | `/` | Create profile (requires `consent_given: true`) | Required | 201 | 400 (no consent), 409 (duplicate) |
| `GET` | `/me` | Get current user's profile | Required | 200 | 404 (no profile) |
| `GET` | `/{learner_id}` | Get profile by ID (admin/service) | Required (admin) | 200 | 403, 404 |
| `PATCH` | `/me` | Update profile (partial, replace semantics per section) | Required | 200 | 404, 422 |
| `PATCH` | `/me/sections/{section}` | Update single JSONB section | Required | 200 | 404 (section or profile) |
| `DELETE` | `/me` | Soft-delete profile | Required | 204 | 404 |
| `DELETE` | `/me/gdpr-erase` | Hard delete — true erasure (GDPR) | Required | 204 | 404 |
| `GET` | `/me/onboarding-status` | Onboarding completion state | Required | 200 | 404 |
| `PATCH` | `/me/onboarding/{section}` | Mark section complete + store data | Required | 200 | 404, 422 |
| `POST` | `/me/sync-from-phm` | Pull PHM data into profile | Required | 200 | 404, 502 (PHM unavailable) |
| `GET` | `/me/completeness` | Profile completeness score + next recommended field | Required | 200 | 404 |

**Duplicate handling (I-3):** `POST /` returns 409 Conflict if a profile already exists for this user's JWT `sub`. Use `PATCH /me` to update.

**Valid section names for `/me/sections/{section}` (I-5):** `expertise`, `professional_context`, `goals`, `communication`, `delivery`, `accessibility`. Case-sensitive, lowercase. Returns 404 for unknown sections.

**PATCH semantics (M-4):** JSONB sections use **replace** semantics, not deep merge. Sending `{ "expertise": { "programming": { "level": "advanced" } } }` replaces the entire `expertise` section. Concurrent updates to the same section may lose changes. Acceptable for v1 (single-user profiles).

**Delete lifecycle (I-4):**
- Soft delete (`DELETE /me`): sets `deleted_at`, profile hidden from `GET /me`. Recoverable.
- GDPR erase (`DELETE /me/gdpr-erase`): works on both active AND soft-deleted profiles. Irreversible.
- After soft delete: `POST /` creates a new profile (old record stays soft-deleted unless GDPR erased).

### Rate Limits — `[B-6 FIX]`

| Endpoint | Rate Limit | Window |
|---|---|---|
| `GET /me` | 120 requests | 1 minute |
| `PATCH /me` | 30 requests | 1 hour |
| `PATCH /me/sections/*` | 60 requests | 1 hour |
| `PATCH /me/onboarding/*` | 60 requests | 1 hour |
| `POST /me/sync-from-phm` | 5 requests | 1 hour |
| `GET /me/completeness` | 60 requests | 1 minute |
| `POST /` | 1 per user | Lifetime (unique constraint) |

Uses the same Redis Lua-based atomic rate limiting from `api_infra/core/rate_limit.py`.

### Request Schemas — `[B-1 FIX]`

```python
from pydantic import BaseModel, Field, field_validator
from typing import Any

# === Typed section schemas (shared by request and response) ===

class DomainExpertise(BaseModel):
    level: Literal["none", "beginner", "intermediate", "advanced", "expert"] = "beginner"
    domain_name: str | None = Field(None, max_length=100)
    is_primary: bool = False
    notes: str | None = Field(None, max_length=300)

class ProgrammingExpertise(BaseModel):
    level: Literal["none", "beginner", "intermediate", "advanced", "expert"] = "beginner"
    languages: list[str] = Field(default_factory=list, max_length=10)
    notes: str | None = Field(None, max_length=300)

class AiMlExpertise(BaseModel):
    level: Literal["none", "beginner", "intermediate", "advanced", "expert"] = "beginner"
    notes: str | None = Field(None, max_length=300)

class BusinessExpertise(BaseModel):
    level: Literal["none", "beginner", "intermediate", "advanced", "expert"] = "beginner"
    notes: str | None = Field(None, max_length=300)

class MasteredTopic(BaseModel):
    topic: str = Field(max_length=200)
    treatment: Literal["reference", "skip"] = "reference"

class PartialTopic(BaseModel):
    topic: str = Field(max_length=200)
    knowledge_state: str = Field(max_length=300)

class Misconception(BaseModel):
    topic: str = Field(max_length=200)
    misconception: str = Field(max_length=500)

class SubjectSpecific(BaseModel):
    topics_already_mastered: list[MasteredTopic] = Field(default_factory=list, max_length=50)
    topics_partially_known: list[PartialTopic] = Field(default_factory=list, max_length=20)
    known_misconceptions: list[Misconception] = Field(default_factory=list, max_length=5)

class ExpertiseSection(BaseModel):
    domain: list[DomainExpertise] = Field(default_factory=list, max_length=5)
    programming: ProgrammingExpertise = Field(default_factory=ProgrammingExpertise)
    ai_ml: AiMlExpertise = Field(default_factory=AiMlExpertise)
    business: BusinessExpertise = Field(default_factory=BusinessExpertise)
    subject_specific: SubjectSpecific = Field(default_factory=SubjectSpecific)

class RealProject(BaseModel):
    project_name: str = Field(max_length=100)
    description: str = Field(max_length=500)

class ProfessionalContextSection(BaseModel):
    current_role: str | None = Field(None, max_length=100)
    industry: str | None = Field(None, max_length=100)
    organization_type: str | None = Field(None, max_length=50)
    team_context: str | None = Field(None, max_length=200)
    real_projects: list[RealProject] = Field(default_factory=list, max_length=5)
    tools_in_use: list[str] = Field(default_factory=list, max_length=20)
    constraints: str | None = Field(None, max_length=300)

class GoalsSection(BaseModel):
    primary_learning_goal: str | None = Field(None, max_length=500)
    secondary_goals: list[str] = Field(default_factory=list, max_length=5)
    urgency: Literal["low", "medium", "high"] | None = None
    urgency_note: str | None = Field(None, max_length=200)
    career_goal: str | None = Field(None, max_length=300)
    immediate_application: str | None = Field(None, max_length=300)

class CommunicationSection(BaseModel):
    language_complexity: Literal["plain", "professional", "technical", "expert"] | None = None
    preferred_structure: Literal["examples-first", "theory-first", "story-narrative", "reference-lookup", "problem-first"] | None = None
    verbosity: Literal["concise", "moderate", "detailed"] | None = None
    analogy_domain: str | None = Field(None, max_length=100)
    tone: Literal["formal", "professional", "conversational", "peer-to-peer"] | None = None
    wants_summaries: bool | None = None
    wants_check_in_questions: bool | None = None
    format_notes: str | None = Field(None, max_length=200)

class DeliverySection(BaseModel):
    output_format: Literal["prose", "structured-with-headers", "mixed"] | None = None
    target_length: Literal["short", "medium", "long", "match-source"] | None = None
    include_code_samples: bool | None = None
    code_verbosity: Literal["minimal", "annotated", "fully-explained"] | None = None
    include_visual_descriptions: bool | None = None
    language: str = "English"
    language_proficiency: Literal["native", "fluent", "intermediate", "basic"] | None = None

class AccessibilitySection(BaseModel):
    screen_reader: bool = False
    cognitive_load_preference: Literal["standard", "reduced"] = "standard"
    color_blind_safe: bool = False
    dyslexia_friendly: bool = False
    notes: str | None = Field(None, max_length=300)

# === Request models ===

class ProfileCreate(BaseModel):
    consent_given: bool  # Must be True
    name: str | None = Field(None, max_length=255)
    expertise: ExpertiseSection = Field(default_factory=ExpertiseSection)
    professional_context: ProfessionalContextSection = Field(default_factory=ProfessionalContextSection)
    goals: GoalsSection = Field(default_factory=GoalsSection)
    communication: CommunicationSection = Field(default_factory=CommunicationSection)
    delivery: DeliverySection = Field(default_factory=DeliverySection)
    accessibility: AccessibilitySection = Field(default_factory=AccessibilitySection)

    @field_validator("consent_given")
    @classmethod
    def consent_must_be_true(cls, v):
        if not v:
            raise ValueError("consent_given must be True to create a profile")
        return v

class ProfileUpdate(BaseModel):
    """All fields optional. Only provided fields are updated."""
    name: str | None = None
    expertise: ExpertiseSection | None = None
    professional_context: ProfessionalContextSection | None = None
    goals: GoalsSection | None = None
    communication: CommunicationSection | None = None
    delivery: DeliverySection | None = None
    accessibility: AccessibilitySection | None = None
```

### Response Schemas

```python
class ProfileResponse(BaseModel):
    learner_id: str
    name: str | None
    profile_version: str
    consent_given: bool
    consent_date: datetime | None
    expertise: ExpertiseSection
    professional_context: ProfessionalContextSection
    goals: GoalsSection
    communication: CommunicationSection
    delivery: DeliverySection
    accessibility: AccessibilitySection
    onboarding_completed: bool
    profile_completeness: float  # 0.0 - 1.0
    created_at: datetime
    updated_at: datetime

class OnboardingStatus(BaseModel):
    learner_id: str
    sections_completed: dict[str, bool]  # keys: goals, expertise, professional_context, ai_enrichment
    overall_completed: bool
    next_section: str | None  # one of: goals, expertise, professional_context, ai_enrichment, or null
    profile_completeness: float

class CompletenessResponse(BaseModel):
    learner_id: str
    overall: float  # 0.0 - 1.0
    per_section: dict[str, float]
    highest_impact_missing: list[str]  # ordered by impact (see algorithm below)

class ErrorResponse(BaseModel):
    """Standard error response for all non-2xx responses."""
    error: str           # Machine-readable code: "consent_required", "profile_exists", "not_found", "validation_error", "forbidden"
    message: str         # Human-readable explanation
    details: dict[str, Any] | None = None  # Field-level errors for 422
```

**Error codes by status — `[B-2 FIX]`:**

| HTTP Status | `error` code | When |
|---|---|---|
| 400 | `consent_required` | `POST /` with `consent_given: false` or missing |
| 403 | `forbidden` | Accessing another user's profile without admin role |
| 404 | `not_found` | Profile doesn't exist, or unknown section name |
| 409 | `profile_exists` | `POST /` for a user that already has a profile |
| 422 | `validation_error` | Invalid enum value, exceeds max length, array too large. `details` contains per-field errors |
| 502 | `upstream_unavailable` | PHM sync failed due to Study Mode API being down |

### Profile Completeness Algorithm — `[B-3 FIX]`

**Section weights** (sum = 1.0):

| Section | Weight | Rationale |
|---|---|---|
| `expertise` | 0.25 | Drives vocabulary, depth, code inclusion — highest personalization impact |
| `goals` | 0.20 | Drives lesson framing and emphasis allocation |
| `professional_context` | 0.20 | Drives example selection and grounding |
| `communication` | 0.15 | Drives tone and structure (often inferred) |
| `delivery` | 0.10 | Drives format (often inferred or defaulted) |
| `accessibility` | 0.10 | Drives accessibility adaptations |

**Section "filled" definition:** A section is filled if at least one non-default, non-null value is set within it. Examples:
- `expertise` with `programming.level: "advanced"` → filled (non-default, since default is `beginner`)
- `goals` with only default values → not filled
- `communication` with all values inferred by the system → filled (inferred values count)

**`highest_impact_missing`:** Returns unfilled sections ordered by weight (highest first). Static priority within a section: `primary_learning_goal` > `programming.level` > `ai_ml.level` > `domain.level` > `current_role` > `industry` > remaining fields.

### Cache Strategy

| Data | Cache Key | TTL | Invalidation |
|---|---|---|---|
| Profile | `lp:profile:{learner_id}` | 30 min | Any profile update |
| Onboarding status | `lp:onboarding:{learner_id}` | 10 min | Section completion |

### GDPR Implementation

| Operation | Behavior |
|---|---|
| `DELETE /me` | Soft delete — sets `deleted_at`, profile excluded from queries. Recoverable. |
| `DELETE /me/gdpr-erase` | **Hard delete** — removes profile row entirely. Audit log retains anonymized record (see Appendix D for full protocol: SHA-256 hash of `learner_id`, `previous_values` cleared, `action` overwritten to `"gdpr_erased"`). Irreversible. |
| Consent tracking | `consent_given: true` required at profile creation. `consent_date` auto-set. |
| Data export | `GET /me` returns complete profile JSON (data portability). |

### Cold-Start Behavior

| Profile State | User Experience |
|---|---|
| No profile | Unpersonalized source content + banner: "Create your learner profile for personalized content" |
| Profile exists, incomplete | Content with defaults for missing sections + banner: "Profile X% complete" |
| Profile exists, complete | Full profile served to downstream consumers |

---

## 6. Test Scenarios

### P0 — Must Pass Before Any Deployment

| Test | What It Verifies |
|---|---|
| `test_create_profile_with_consent` | POST / with `consent_given: true` → 201. Without consent → 400. |
| `test_get_own_profile` | GET /me returns profile matching JWT sub |
| `test_patch_profile_updates_only_provided_fields` | PATCH /me with only `goals` → only goals updated |
| `test_section_update` | PATCH /me/sections/expertise → only expertise JSONB updated |
| `test_soft_delete` | DELETE /me → `deleted_at` set, GET /me returns 404 |
| `test_gdpr_hard_delete` | DELETE /me/gdpr-erase → row deleted, audit log has anonymized entry |
| `test_no_token_returns_401` | All endpoints without JWT → 401 |
| `test_user_cannot_access_other_profile` | GET /{other_id} → 403 for non-admin |
| `test_profile_defaults_applied` | Profile with only consent → all defaults from Appendix B applied correctly |
| `test_include_code_samples_conditional_default` | `programming.level: none` → `include_code_samples` defaults to `false` |
| `test_freetext_length_limits` | Notes field with 500+ chars → 422 validation error |
| `test_expertise_enum_validation` | `expertise.domain[0].level: "superexpert"` → 422 |

### P1 — Must Pass Before v1 Launch

| Test | What It Verifies |
|---|---|
| `test_onboarding_status_initially_incomplete` | New profile → all sections incomplete |
| `test_completing_all_sections_marks_done` | After all sections → `onboarding_completed: true` |
| `test_partial_onboarding_saves_progress` | Complete 2 of 4 sections, abandon → profile has 2 sections filled |
| `test_profile_completeness_score` | Profile with 3/7 sections → ~0.43 completeness |
| `test_completeness_highest_impact` | Missing expertise → `highest_impact_missing` includes expertise fields |
| `test_phm_sync_updates_profile` | PHM data maps to profile fields per Appendix A |
| `test_inference_rules_from_expertise` | `programming: none` → inferred `language_complexity: plain` |
| `test_domain_array_with_primary` | Create profile with 2 domains, exactly one `is_primary: true` |
| `test_misconceptions_capped_at_5` | Submitting 6 misconceptions → 422 or truncated |
| `test_dev_mode_bypasses_auth` | `DEV_MODE=true` → requests succeed without token |
| `test_cache_invalidated_on_update` | PATCH /me → Redis cache key deleted |

### P2 — Edge Cases

| Test | What It Verifies |
|---|---|
| `test_null_vs_missing_vs_empty` | `name: null`, omitting name, `name: ""` → all treated as unknown |
| `test_duplicate_topics_deduplicated` | `topics_already_mastered: ["Python", "python"]` → stored as one entry |
| `test_unicode_in_all_fields` | Arabic name, Urdu notes → stored and returned correctly |
| `test_profile_version_set_automatically` | Client cannot override `profile_version` |
| `test_create_after_soft_delete` | Can create new profile after soft-deleting old one |
| `test_audit_log_created_on_update` | Every PATCH creates an audit log entry |
| `test_concurrent_updates` | Two simultaneous PATCHes → no data loss (last write wins on JSONB sections) |

---

## 7. What NOT to Build

| # | Feature | Why Excluded | Reconsider When |
|---|---|---|---|
| 1 | Personalization engine | Separate system. This service stores/serves profiles. | Separate build phase |
| 2 | Real-time collaborative profile editing | Massive complexity for zero v1 value | Multi-instructor scenarios validated |
| 3 | ML-based profile inference | Progressive profiling is rule-based in v1 | After v1 data proves value |
| 4 | Custom lesson authoring | We personalize existing lessons, not create new ones | Never in this system |
| 5 | Profile sharing/export | No user need identified | Enterprise features scoped |
| 6 | A/B testing personalization | Need baseline first | After v1 quality metrics |
| 7 | Social/peer comparison | Privacy concerns outweigh value | Probably never |
| 8 | Automated profile decay | Profiles don't auto-expire | v2 progressive profiling |
| 9 | Multi-profile per learner | One profile per `learner_id` | Distinct learning contexts validated |
| 10 | Offline profile storage | Server-side only | If offline learning required |
| 11 | Profile-driven assessment | Profile drives presentation, not evaluation | Assessment system design |
| 12 | Cache warming / batch pre-generation | On-demand is sufficient for v1 | Latency issues at scale |

---

## 8. Decision Log

| # | Decision | Resolution | Rationale |
|---|---|---|---|
| D-1 | Onboarding approach | **Hybrid (Option C)** | Form for structured + AI for enrichment. Demos AI capability. |
| D-2 | Default expertise level | **`beginner`** | Under-estimating is less harmful than over-estimating |
| D-3 | `ai_ml.level` enum | **Standardize to `beginner`** | Cross-field consistency. Notes captures nuance. |
| D-4 | Accessibility section | **Include in v1** | Schemas don't change daily. Foundational. |
| D-5 | GDPR compliance | **Hard delete + consent flag** | Right to erasure. Audit log anonymized. |
| D-6 | Prompt injection | **Sandwich + length limits** | Length limits at API. Sandwich at consumer. |
| D-7 | Personalization engine | **Out of scope** | Separate build. Profile system serves data. |
| D-8 | Progressive profiling | **Basic triggers in v1** | After-lesson feedback, after-3-lessons prompt, settings page |
| D-9 | Multi-domain | **Array in v1** | Target audience is multi-domain experts |
| D-10 | Onboarding abandonment | **Save partial + nudge** | Never block content access |
| D-11 | Database hosting | **Neon (serverless PG)** | Zero ops, `pool_pre_ping` for cold starts |

---

## Appendix A — PHM Field Mapping

| PHM Field | Profile Field | Transform |
|---|---|---|
| `expertise_level.domain_expertise` | `expertise.domain[0].level` (primary) | Direct enum mapping |
| `expertise_level.programming_experience` | `expertise.programming.level` | Direct enum mapping |
| `expertise_level.ai_ml_familiarity` | `expertise.ai_ml.level` | Direct enum mapping |
| `expertise_level.business_experience` | `expertise.business.level` | Direct enum mapping |
| `knowledge_map.mastered[].topic` | `expertise.subject_specific.topics_already_mastered[]` | Each topic → `{ "topic": "<value>", "treatment": "reference" }`. Default `treatment` is `reference` (brief recap allowed). Deduplicate by case-normalized topic name. |
| `knowledge_map.topics_to_skip[]` | `expertise.subject_specific.topics_already_mastered[]` | Each topic → `{ "topic": "<value>", "treatment": "skip" }`. Merged into same array. If topic exists with `reference`, PHM `skip` overrides to `skip`. |
| `knowledge_map.known_misconceptions[]` | `expertise.subject_specific.known_misconceptions[]` | Direct string array. Capped at 5. |
| `professional_context.current_role` | `professional_context.current_role` | Direct string copy |
| `professional_context.industry` | `professional_context.industry` | Direct string copy |
| `professional_context.real_projects[]` | `professional_context.real_projects[]` | Direct array copy |
| `motivation_and_goals.primary_goal` | `goals.primary_learning_goal` | Direct string copy |
| `motivation_and_goals.urgency` | `goals.urgency` | Direct enum mapping |
| `communication_preferences.language_complexity` | `communication.language_complexity` | Direct enum mapping |
| `communication_preferences.preferred_analogy_domain` | `communication.analogy_domain` | Direct string copy |
| `communication_preferences.verbosity_preference` | `communication.verbosity` | Direct enum mapping |
| `learning_style_signals.prefers_examples_before_theory` | `communication.preferred_structure` | `true` → `examples-first`, `false` → `theory-first` |

**PHM Sync Conflict Rules:**
- PHM data **never overwrites** user-set values (fields that were set via API/onboarding).
- PHM data only fills **null/default** fields, OR updates `topics_already_mastered` (additive — new topics are appended, existing topics upgraded from `reference` → `skip` if PHM says skip, but never downgraded from `skip` → `reference`).
- If PHM and user disagree on an expertise level, user-set value wins.

---

## Appendix B — Complete Defaults Table (v1.1)

| Field | Default | Condition |
|---|---|---|
| `expertise.*.level` | `beginner` | All expertise fields |
| `communication.language_complexity` | `professional` | |
| `communication.preferred_structure` | `examples-first` | |
| `communication.verbosity` | `moderate` | |
| `communication.tone` | `professional` | |
| `communication.wants_summaries` | `true` | |
| `communication.wants_check_in_questions` | `true` | |
| `delivery.output_format` | `structured-with-headers` | |
| `delivery.target_length` | `match-source` | |
| `delivery.include_code_samples` | `false` | When `programming.level == none` or absent |
| `delivery.include_code_samples` | `true` | When `programming.level >= beginner` |
| `delivery.code_verbosity` | Inferred from `programming.level` | `beginner→fully-explained, intermediate→annotated, advanced/expert→minimal` |
| `delivery.language` | `English` | |
| `delivery.language_proficiency` | `native` | |
| `accessibility.screen_reader` | `false` | |
| `accessibility.cognitive_load_preference` | `standard` | |
| `accessibility.color_blind_safe` | `false` | |
| `accessibility.dyslexia_friendly` | `false` | |
| `goals.primary_learning_goal` | Inferred from lesson title | |
| `communication.analogy_domain` | `professional_context.industry` or generic | Cascading fallback |

---

## Appendix C — Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | Neon PostgreSQL connection string. Format: `postgresql+asyncpg://user:pass@host/db?sslmode=require` |
| `REDIS_URL` | Yes | — | Redis connection string. Format: `redis://host:6379/0` |
| `JWKS_URL` | Yes | — | SSO JWKS endpoint for JWT validation. Example: `http://sso:3001/.well-known/jwks.json` |
| `JWT_ISSUER` | Yes | — | Expected JWT issuer claim |
| `JWT_AUDIENCE` | Yes | — | Expected JWT audience claim |
| `STUDY_MODE_API_URL` | Yes | — | Study Mode API base URL for PHM sync. Example: `http://study-mode-api:8000` |
| `PORT` | No | `8004` | Service port |
| `DEV_MODE` | No | `false` | When `true`, bypasses JWT auth (development only — NEVER in production) |
| `LOG_LEVEL` | No | `info` | Logging level: `debug`, `info`, `warning`, `error` |
| `REDIS_NAMESPACE` | No | `lp:` | Redis key prefix for cache isolation |
| `DB_POOL_SIZE` | No | `5` | SQLAlchemy async pool size |
| `DB_POOL_PRE_PING` | No | `true` | Validate connections before use (required for Neon cold starts) |
| `RATE_LIMIT_ENABLED` | No | `true` | Enable/disable rate limiting |

**Secret management:** All secrets (`DATABASE_URL`, `REDIS_URL`, JWT config) via environment variables only. Never committed to git. `.env.example` provided with placeholder values.

---

## Appendix D — GDPR Erasure Protocol

### Hard Delete Procedure (`DELETE /me/gdpr-erase`)

1. **Load profile** by JWT `sub` (including soft-deleted records — `deleted_at IS NOT NULL` still eligible)
2. **Delete profile row** from `learner_profiles` table entirely (`DELETE FROM learner_profiles WHERE learner_id = ?`)
3. **Anonymize audit trail** — for all `profile_audit_log` entries for this `learner_id`:
   - Replace `learner_id` with SHA-256 hash: `sha256(learner_id + salt)` where salt = `GDPR_HASH_SALT` env var (or service-level constant)
   - Clear `previous_values` → `{}`
   - Clear `changed_sections` → `[]`
   - Set `action` → `"gdpr_erased"` (overwrite original action)
   - Keep `created_at` (timestamp retained for compliance audit counting)
   - Keep `source` → `"gdpr_erase"`
4. **Invalidate cache** — delete `lp:profile:{learner_id}` and `lp:onboarding:{learner_id}` from Redis
5. **Return 204** — empty response

### What's Retained After Erasure

| Field | Retained? | Value |
|---|---|---|
| `audit_log.id` | Yes | Original UUID (for counting) |
| `audit_log.learner_id` | Anonymized | SHA-256 hash (irreversible without salt) |
| `audit_log.action` | Overwritten | `"gdpr_erased"` |
| `audit_log.changed_sections` | Cleared | `[]` |
| `audit_log.previous_values` | Cleared | `{}` |
| `audit_log.source` | Overwritten | `"gdpr_erase"` |
| `audit_log.created_at` | Yes | Original timestamp |
| Profile row | Deleted | Nothing retained |

### Additional GDPR Environment Variable

| Variable | Required | Default | Description |
|---|---|---|---|
| `GDPR_HASH_SALT` | Yes | — | Salt for SHA-256 hashing of learner_id in anonymized audit records. Must be ≥32 chars. |

---

## References

- Schema Audit: `specs/learner-profile/research/schema-audit.md`
- Engine Spec: `specs/learner-profile/research/engine-spec.md`
- Onboarding UX: `specs/learner-profile/research/onboarding-ux.md`
- Technical Architecture: `specs/learner-profile/research/technical-architecture.md`
- QA Review: `specs/learner-profile/research/qa-review.md`
- Original Schema Research: `learner_profile_schema.md`
