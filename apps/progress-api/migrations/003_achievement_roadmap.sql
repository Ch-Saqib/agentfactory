-- Migration: Achievement Roadmap System
-- Adds visual skill tree showing learning paths with unlockable nodes
-- Safe to re-run — all statements are idempotent

-- 1. New table: achievement_nodes
-- Defines the roadmap structure (parts, chapters, milestones)
CREATE TABLE IF NOT EXISTS achievement_nodes (
    id              VARCHAR(100) PRIMARY KEY,
    parent_id       VARCHAR(100) REFERENCES achievement_nodes(id) ON DELETE CASCADE,
    node_type       VARCHAR(20) NOT NULL CHECK (node_type IN ('part', 'chapter', 'milestone')),
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    position_x      INTEGER NOT NULL DEFAULT 0,
    position_y      INTEGER NOT NULL DEFAULT 0,
    config          JSONB NOT NULL DEFAULT '{}',
    required_xp     INTEGER NOT NULL DEFAULT 0,
    icon            VARCHAR(50),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for roadmap queries
CREATE INDEX IF NOT EXISTS ix_achievement_nodes_parent
    ON achievement_nodes (parent_id);

CREATE INDEX IF NOT EXISTS ix_achievement_nodes_type
    ON achievement_nodes (node_type);

-- 2. New table: user_achievement_progress
-- Tracks which nodes each user has unlocked
CREATE TABLE IF NOT EXISTS user_achievement_progress (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    node_id         VARCHAR NOT NULL REFERENCES achievement_nodes(id) ON DELETE CASCADE,
    unlocked_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, node_id)
);

-- Index for user's unlocked nodes
CREATE INDEX IF NOT EXISTS ix_user_achievement_progress_user
    ON user_achievement_progress (user_id, unlocked_at DESC);

-- 3. Insert roadmap structure
-- Part 1: General Agents Foundations
INSERT INTO achievement_nodes (id, node_type, title, description, position_x, position_y, required_xp, icon)
VALUES
    ('part_01_foundations', 'part', 'Foundations', 'Learn the paradigm and principles', 0, 0, 0, '📚'),
    ('ch_01_paradigm', 'chapter', 'Agent Factory Paradigm', 'Understanding the new approach', -100, 100, 0, '🎯'),
    ('ch_02_general', 'chapter', 'General Agents', 'Building without code', 0, 100, 50, '🤖'),
    ('ch_03_principles', 'chapter', 'Seven Principles', 'Core patterns for success', 100, 100, 100, '⚡')
ON CONFLICT (id) DO NOTHING;

-- Part 2: Applied General Agent Workflows
INSERT INTO achievement_nodes (id, parent_id, node_type, title, description, position_x, position_y, required_xp, icon)
VALUES
    ('part_02_workflows', NULL, 'part', 'Applied Workflows', 'Practical AI applications', 200, 0, 150, '🛠️'),
    ('ch_06_first_employee', 'part_02_workflows', 'chapter', 'First AI Employee', 'Build your first agent', 100, 100, 150, '👔')
ON CONFLICT (id) DO NOTHING;

-- Part 3: SDD-RI Fundamentals
INSERT INTO achievement_nodes (id, node_type, title, description, position_x, position_y, required_xp, icon)
VALUES
    ('part_03_sdd', 'part', 'SDD Fundamentals', 'Spec-Driven Development', 400, 0, 300, '📋')
ON CONFLICT (id) DO NOTHING;

-- Part 4: Programming in the AI Era
INSERT INTO achievement_nodes (id, node_type, title, description, position_x, position_y, required_xp, icon)
VALUES
    ('part_04_programming', 'part', 'AI Programming', 'Code with AI assistance', 600, 0, 500, '💻')
ON CONFLICT (id) DO NOTHING;

-- Part 5: Agent Deployment
INSERT INTO achievement_nodes (id, node_type, title, description, position_x, position_y, required_xp, icon)
VALUES
    ('part_05_deployment', 'part', 'Agent Deployment', 'Ship your agents', 800, 0, 800, '🚀')
ON CONFLICT (id) DO NOTHING;

-- Part 6: Cloud Native Agents
INSERT INTO achievement_nodes (id, node_type, title, description, position_x, position_y, required_xp, icon)
VALUES
    ('part_06_cloud', 'part', 'Cloud Native', 'Scale with infrastructure', 1000, 0, 1200, '☁️')
ON CONFLICT (id) DO NOTHING;

-- Milestones
INSERT INTO achievement_nodes (id, parent_id, node_type, title, description, position_x, position_y, required_xp, icon)
VALUES
    ('milestone_first_quiz', 'part_01_foundations', 'milestone', 'First Quiz', 'Complete your first quiz', -50, 200, 0, '✅'),
    ('milestone_streak_3', 'part_02_workflows', 'milestone', '3-Day Streak', 'Learn for 3 days straight', 250, 150, 100, '🔥'),
    ('milestone_xp_500', 'part_03_sdd', 'milestone', '500 XP', 'Earn 500 total XP', 400, 150, 500, '⭐'),
    ('milestone_badges_5', 'part_04_programming', 'milestone', '5 Badges', 'Collect 5 badges', 600, 150, 300, '🏆')
ON CONFLICT (id) DO NOTHING;

-- 4. Add comments for documentation
COMMENT ON TABLE achievement_nodes IS 'Roadmap structure: parts, chapters, milestones with positions for ReactFlow visualization';
COMMENT ON TABLE user_achievement_progress IS 'User unlock status for each achievement node';

COMMENT ON COLUMN achievement_nodes.position_x IS 'X coordinate for ReactFlow layout';
COMMENT ON COLUMN achievement_nodes.position_y IS 'Y coordinate for ReactFlow layout';
COMMENT ON COLUMN achievement_nodes.config IS 'Additional node data (prerequisites, links, etc.)';
COMMENT ON COLUMN user_achievement_progress.unlocked_at IS 'When the user unlocked this node';
