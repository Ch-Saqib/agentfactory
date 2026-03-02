-- Migration: Smart Review System
-- Adds personalized review recommendations with spaced repetition
-- Safe to re-run — all statements are idempotent

-- 1. New table: review_reminders
-- Tracks items recommended for review
CREATE TABLE IF NOT EXISTS review_reminders (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_slug    VARCHAR(200) NOT NULL,
    priority        VARCHAR(20) NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
    reason          VARCHAR(50) NOT NULL, -- 'weak_area', 'spaced_repetition', 'prerequisite'
    interval_days   INTEGER NOT NULL DEFAULT 1,
    due_date        DATE NOT NULL,
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for review queue queries
CREATE INDEX IF NOT EXISTS ix_review_reminders_user_due
    ON review_reminders (user_id, due_date)
    WHERE completed = FALSE;

CREATE INDEX IF NOT EXISTS ix_review_reminders_user_priority
    ON review_reminders (user_id, priority, due_date)
    WHERE completed = FALSE;

-- Index for cleanup
CREATE INDEX IF NOT EXISTS ix_review_reminders_created
    ON review_reminders (created_at)
    WHERE created_at < CURRENT_DATE - INTERVAL '365 days'; -- Data retention

-- 2. Add comments for documentation
COMMENT ON TABLE review_reminders IS 'Personalized review queue with spaced repetition scheduling';

COMMENT ON COLUMN review_reminders.priority IS 'Review priority: high (weak areas), medium (prerequisites), low (maintenance)';
COMMENT ON COLUMN review_reminders.reason IS 'Why this item is recommended: weak_area (score < 70%), spaced_repetition (FSRS), prerequisite (for next lesson)';
COMMENT ON COLUMN review_reminders.interval_days IS 'Days until next review (increases with successful recalls)';
COMMENT ON COLUMN review_reminders.due_date IS 'When this item is due for review';

-- 3. Function to calculate next review interval (FSRS-style)
-- Simplified version: intervals double after each successful review
-- CREATE OR REPLACE FUNCTION calculate_next_review(
--     p_current_interval INTEGER,
--     p_score_pct INTEGER
-- ) RETURNS INTEGER AS $$
--     BEGIN
--         -- If score >= 80%, double the interval (up to 90 days)
--         -- If score < 80%, reset to 1 day
--         IF p_score_pct >= 80 THEN
--             RETURN LEAST(p_current_interval * 2, 90);
--         ELSE
--             RETURN 1;
--         END IF;
--     END;
-- $$ LANGUAGE plpgsql;
