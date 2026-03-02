-- Migration: Daily Challenges System
-- Adds daily/weekly challenge system for gamified learning goals
-- Safe to re-run — all statements are idempotent

-- 1. New table: daily_challenges
-- Pre-generated challenges for each day with templates
CREATE TABLE IF NOT EXISTS daily_challenges (
    id              SERIAL PRIMARY KEY,
    challenge_date  DATE NOT NULL UNIQUE,
    challenge_type  VARCHAR(50) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    config          JSONB NOT NULL DEFAULT '{}',
    xp_bonus        INTEGER NOT NULL DEFAULT 50 CHECK (xp_bonus >= 0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for date-based lookups
CREATE INDEX IF NOT EXISTS ix_daily_challenges_date
    ON daily_challenges (challenge_date);

-- Index for active challenges (today and future)
CREATE INDEX IF NOT EXISTS ix_daily_challenges_active
    ON daily_challenges (challenge_date)
    WHERE challenge_date >= CURRENT_DATE;

-- 2. New table: user_challenge_progress
-- Tracks each user's progress on daily challenges
CREATE TABLE IF NOT EXISTS user_challenge_progress (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id    INTEGER NOT NULL REFERENCES daily_challenges(id) ON DELETE CASCADE,
    progress        JSONB NOT NULL DEFAULT '{}',
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    xp_awarded      INTEGER NOT NULL DEFAULT 0,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    UNIQUE(user_id, challenge_id)
);

-- Index for user's active challenges
CREATE INDEX IF NOT EXISTS ix_user_challenge_progress_user
    ON user_challenge_progress (user_id, completed);

-- Index for completed challenges (cleanup)
CREATE INDEX IF NOT EXISTS ix_user_challenge_progress_completed
    ON user_challenge_progress (completed_at)
    WHERE completed = TRUE;

-- 3. New table: challenge_templates
-- Stores reusable challenge templates
CREATE TABLE IF NOT EXISTS challenge_templates (
    id              VARCHAR(50) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    description     TEXT NOT NULL,
    config_schema   JSONB NOT NULL DEFAULT '{}',
    xp_bonus        INTEGER NOT NULL DEFAULT 50,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Insert default challenge templates
INSERT INTO challenge_templates (id, name, description, config_schema, xp_bonus)
VALUES
    ('quiz_master', 'Quiz Master', 'Complete 3 quizzes with 80%+ score', '{"target_count": 3, "min_score": 80}', 50),
    ('learning_spree', 'Learning Spree', 'Complete 5 lessons in a single day', '{"target_count": 5}', 75),
    ('perfect_week', 'Perfect Week', 'Maintain a 7-day streak', '{"target_streak": 7}', 100),
    ('explorer', 'Explorer', 'Complete activities from 3 different parts', '{"target_parts": 3}', 60),
    ('night_owl', 'Night Owl', 'Complete a quiz after 10 PM', '{"after_hour": 22}', 30),
    ('early_bird', 'Early Bird', 'Complete a quiz before 8 AM', '{"before_hour": 8}', 30),
    ('flashcard_fanatic', 'Flashcard Fanatic', 'Complete 3 flashcard decks', '{"target_count": 3}', 40),
    ('review_master', 'Review Master', 'Complete 5 review items', '{"target_count": 5}', 50)
ON CONFLICT (id) DO NOTHING;

-- 4. Add comment for documentation
COMMENT ON TABLE daily_challenges IS 'Pre-generated daily challenges with configurable templates';
COMMENT ON TABLE user_challenge_progress IS 'User progress tracking for daily challenges';
COMMENT ON TABLE challenge_templates IS 'Reusable challenge template definitions';

COMMENT ON COLUMN user_challenge_progress.progress IS 'JSON progress tracking (e.g., {"quizzes_completed": 2, "target": 3})';
COMMENT ON COLUMN daily_challenges.config IS 'Template-specific configuration (e.g., target counts, thresholds)';
