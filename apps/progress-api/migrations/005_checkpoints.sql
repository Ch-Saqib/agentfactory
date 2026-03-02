-- Migration: Knowledge Checkpoints System
-- Adds knowledge questions at scroll positions during lesson reading
-- Safe to re-run — all statements are idempotent

-- 1. New table: knowledge_checkpoints
-- Pre-defined checkpoint questions for lessons
CREATE TABLE IF NOT EXISTS knowledge_checkpoints (
    id              SERIAL PRIMARY KEY,
    lesson_slug     VARCHAR(200) NOT NULL,
    position_pct    INTEGER NOT NULL CHECK (position_pct BETWEEN 0 AND 100),
    question_data   JSONB NOT NULL DEFAULT '{}',
    xp_bonus        INTEGER NOT NULL DEFAULT 10,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(lesson_slug, position_pct)
);

-- Index for checkpoint lookups by lesson
CREATE INDEX IF NOT EXISTS ix_knowledge_checkpoints_lesson
    ON knowledge_checkpoints (lesson_slug, position_pct);

-- 2. New table: checkpoint_attempts
-- Tracks user answers to checkpoint questions
CREATE TABLE IF NOT EXISTS checkpoint_attempts (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    checkpoint_id   INTEGER NOT NULL REFERENCES knowledge_checkpoints(id) ON DELETE CASCADE,
    answer          TEXT NOT NULL,
    correct         BOOLEAN NOT NULL,
    xp_awarded      INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for user's checkpoint attempts (cleanup)
CREATE INDEX IF NOT EXISTS ix_checkpoint_attempts_user_checkpoint
    ON checkpoint_attempts (user_id, checkpoint_id);

CREATE INDEX IF NOT EXISTS ix_checkpoint_attempts_created
    ON checkpoint_attempts (created_at)
    WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'; -- Data retention

-- 3. Add comments for documentation
COMMENT ON TABLE knowledge_checkpoints IS 'Pre-defined checkpoint questions at specific scroll positions in lessons';
COMMENT ON TABLE checkpoint_attempts IS 'User answers to checkpoint questions for analytics and XP tracking';

COMMENT ON COLUMN knowledge_checkpoints.position_pct IS 'Scroll position percentage (e.g., 50, 75) where checkpoint appears';
COMMENT ON COLUMN knowledge_checkpoints.question_data IS 'JSON data: question, options, correct_answer, explanation';
COMMENT ON COLUMN checkpoint_attempts.correct IS 'Whether the user answered correctly';
COMMENT ON COLUMN checkpoint_attempts.xp_awarded IS 'XP awarded for correct answer (usually 0 for checkpoints, used for analytics)';
