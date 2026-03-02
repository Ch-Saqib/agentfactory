-- Migration: Study Buddies (Friendships) System
-- Adds social learning with friends and shared XP
-- Safe to re-run — all statements are idempotent

-- 1. New table: friendships
-- Tracks friend relationships between users
CREATE TABLE IF NOT EXISTS friendships (
    id              SERIAL PRIMARY KEY,
    requester_id    VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    accepter_id     VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'removed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(requester_id, accepter_id)
);

-- Indexes for friendship queries
CREATE INDEX IF NOT EXISTS ix_friendships_requester
    ON friendships (requester_id, status);

CREATE INDEX IF NOT EXISTS ix_friendships_accepter
    ON friendships (accepter_id, status);

CREATE INDEX IF NOT EXISTS ix_friendships_status
    ON friendships (status, created_at);

-- 2. New table: shared_activities
-- Tracks activities completed by friends for buddy XP eligibility
CREATE TABLE IF NOT EXISTS shared_activities (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    friend_id       VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type   VARCHAR(50) NOT NULL, -- 'quiz', 'lesson', 'flashcard', 'challenge'
    activity_ref    VARCHAR(200) NOT NULL, -- chapter_slug, lesson_id, etc.
    xp_earned       INTEGER NOT NULL DEFAULT 0,
    shared_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Buddy XP tracking
    buddy_xp_awarded BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexes for shared activity queries (buddy XP eligibility)
CREATE INDEX IF NOT EXISTS ix_shared_activities_user_friend
    ON shared_activities (user_id, friend_id, activity_type, activity_ref);

CREATE INDEX IF NOT EXISTS ix_shared_activities_date
    ON shared_activities (shared_at)
    WHERE shared_at >= CURRENT_DATE - INTERVAL '180 days'; -- Data retention

-- 3. Add comments for documentation
COMMENT ON TABLE friendships IS 'Friend relationships between users for social learning';
COMMENT ON TABLE shared_activities IS 'Activities shared between friends for buddy XP bonus tracking';

COMMENT ON COLUMN shared_activities.buddy_xp_awarded IS 'Whether the +10 buddy XP has been awarded to the friend for this activity';
COMMENT ON COLUMN friendships.status IS 'pending = request sent, accepted = friends, removed = no longer friends';

-- 4. Function to check and award buddy XP (called by quiz/lesson/challenge completion)
-- This is a helper function - actual implementation is in the service layer
-- CREATE OR REPLACE FUNCTION check_buddy_xp_eligibility(
--     p_user_id VARCHAR,
--     p_activity_type VARCHAR,
--     p_activity_ref VARCHAR
-- ) RETURNS INTEGER AS $$
--     -- Returns +10 XP if a friend completed the same activity today
--     -- Implemented in service layer for better transaction control
-- $$ LANGUAGE SQL;
