-- Memory V2.0 Database Schema
-- SQLite database schema for OpenClaw Memory System

-- Priority Analysis Table
CREATE TABLE IF NOT EXISTS memory_priorities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id TEXT NOT NULL,
    conv_id TEXT,
    priority_level TEXT CHECK(priority_level IN ('critical', 'high', 'medium', 'low')),
    reasoning TEXT,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Learning Tracking Table
CREATE TABLE IF NOT EXISTS memory_learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id TEXT NOT NULL,
    conv_id TEXT,
    topic TEXT,
    description TEXT,
    status TEXT CHECK(status IN ('active', 'paused', 'completed', 'abandoned')) DEFAULT 'active',
    progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

-- Learning Milestones Table
CREATE TABLE IF NOT EXISTS memory_learning_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learning_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    achieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learning_id) REFERENCES memory_learning(id) ON DELETE CASCADE
);

-- Decision Records Table
CREATE TABLE IF NOT EXISTS memory_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id TEXT NOT NULL,
    conv_id TEXT,
    summary TEXT NOT NULL,
    context TEXT,
    expected_outcome TEXT,
    actual_outcome TEXT,
    status TEXT CHECK(status IN ('pending', 'implemented', 'validated', 'rejected')) DEFAULT 'pending',
    review_scheduled_at DATETIME,
    reviewed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Skill Evolution Table
CREATE TABLE IF NOT EXISTS memory_evolution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    category TEXT,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_used_at DATETIME,
    first_used_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Database Version Tracking
CREATE TABLE IF NOT EXISTS memory_schema_version (
    version TEXT PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial version
INSERT OR IGNORE INTO memory_schema_version (version) VALUES ('2.0.0');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_priorities_level ON memory_priorities(priority_level);
CREATE INDEX IF NOT EXISTS idx_priorities_created ON memory_priorities(created_at);
CREATE INDEX IF NOT EXISTS idx_learning_status ON memory_learning(status);
CREATE INDEX IF NOT EXISTS idx_learning_topic ON memory_learning(topic);
CREATE INDEX IF NOT EXISTS idx_decisions_status ON memory_decisions(status);
CREATE INDEX IF NOT EXISTS idx_decisions_review ON memory_decisions(review_scheduled_at);
CREATE INDEX IF NOT EXISTS idx_evolution_skill ON memory_evolution(skill_name);
CREATE INDEX IF NOT EXISTS idx_evolution_category ON memory_evolution(category);

-- Views for common queries

-- View: Pending Decisions
CREATE VIEW IF NOT EXISTS v_pending_decisions AS
SELECT 
    d.*,
    CASE 
        WHEN review_scheduled_at < CURRENT_TIMESTAMP THEN 'overdue'
        WHEN review_scheduled_at <= datetime('now', '+7 days') THEN 'due_soon'
        ELSE 'scheduled'
    END as review_status
FROM memory_decisions d
WHERE status IN ('pending', 'implemented')
    AND (review_scheduled_at IS NULL OR review_scheduled_at <= datetime('now', '+7 days'))
ORDER BY review_scheduled_at ASC;

-- View: Skill Summary
CREATE VIEW IF NOT EXISTS v_skill_summary AS
SELECT 
    skill_name,
    category,
    usage_count,
    success_count,
    CASE 
        WHEN usage_count > 0 THEN ROUND(100.0 * success_count / usage_count, 2)
        ELSE 0
    END as success_rate,
    last_used_at,
    first_used_at
FROM memory_evolution
ORDER BY usage_count DESC;

-- View: Weekly Learning Report
CREATE VIEW IF NOT EXISTS v_weekly_learning_report AS
SELECT 
    topic,
    COUNT(*) as session_count,
    AVG(progress) as avg_progress,
    MAX(updated_at) as last_activity,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count
FROM memory_learning
WHERE updated_at >= datetime('now', '-7 days')
GROUP BY topic
ORDER BY last_activity DESC;

-- View: High Priority Items
CREATE VIEW IF NOT EXISTS v_high_priority AS
SELECT 
    'priority' as type,
    id,
    msg_id,
    priority_level as level,
    category,
    reasoning as details,
    created_at
FROM memory_priorities
WHERE priority_level IN ('critical', 'high')
UNION ALL
SELECT 
    'decision' as type,
    id,
    msg_id,
    status as level,
    'decision' as category,
    summary as details,
    created_at
FROM memory_decisions
WHERE status = 'pending' AND review_scheduled_at <= CURRENT_TIMESTAMP
ORDER BY created_at DESC;
