-- ============================================
-- DARKTRACE INTELLIGENCE
-- DarkForums Safe Corpus Schema
-- ============================================

-- Drop existing tables in dependency order
DROP TABLE IF EXISTS persona_relationships CASCADE;
DROP TABLE IF EXISTS persona_features CASCADE;
DROP TABLE IF EXISTS evidence CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS threads CASCADE;
DROP TABLE IF EXISTS handles CASCADE;
DROP TABLE IF EXISTS platforms CASCADE;
DROP TABLE IF EXISTS actors CASCADE;


-- ============================================
-- 1. ACTORS / PERSONAS
-- ============================================

CREATE TABLE actors (
    actor_id SERIAL PRIMARY KEY,

    -- Do NOT use this as a real-world identity.
    -- Represents an authorized/synthetic persona label.
    name TEXT NOT NULL,

    risk_level TEXT DEFAULT 'Unknown',

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 2. PLATFORMS
-- ============================================

CREATE TABLE platforms (
    platform_id SERIAL PRIMARY KEY,

    name TEXT NOT NULL UNIQUE,

    platform_type TEXT DEFAULT 'Forum',

    source TEXT
);


-- ============================================
-- 3. HANDLES
-- ============================================

CREATE TABLE handles (
    handle_id SERIAL PRIMARY KEY,

    actor_id INT REFERENCES actors(actor_id)
        ON DELETE SET NULL,

    platform_id INT REFERENCES platforms(platform_id)
        ON DELETE SET NULL,

    username TEXT NOT NULL,

    first_seen TIMESTAMP,

    last_seen TIMESTAMP,

    source TEXT,

    UNIQUE(platform_id, username)
);


-- ============================================
-- 4. THREADS
-- ============================================

CREATE TABLE threads (
    thread_id TEXT PRIMARY KEY,

    platform_id INT REFERENCES platforms(platform_id)
        ON DELETE SET NULL,

    title TEXT,

    category TEXT,

    forum_name TEXT,

    created_at TIMESTAMP,

    source TEXT
);


-- ============================================
-- 5. POSTS
-- ============================================

CREATE TABLE posts (
    post_id TEXT PRIMARY KEY,

    thread_id TEXT REFERENCES threads(thread_id)
        ON DELETE CASCADE,

    handle_id INT REFERENCES handles(handle_id)
        ON DELETE SET NULL,

    post_number INT,

    content TEXT NOT NULL,

    created_at TIMESTAMP,

    source TEXT NOT NULL DEFAULT 'DarkForums Safe Corpus',

    language TEXT DEFAULT 'en',

    content_hash TEXT,

    created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 6. EVIDENCE
-- ============================================

CREATE TABLE evidence (
    evidence_id SERIAL PRIMARY KEY,

    actor_id INT REFERENCES actors(actor_id)
        ON DELETE CASCADE,

    post_id TEXT REFERENCES posts(post_id)
        ON DELETE CASCADE,

    evidence_type TEXT NOT NULL,

    description TEXT,

    source TEXT NOT NULL,

    evidence_timestamp TIMESTAMP,

    confidence NUMERIC(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 7. PERSONA FEATURES
-- ============================================

CREATE TABLE persona_features (
    feature_id SERIAL PRIMARY KEY,

    actor_id INT REFERENCES actors(actor_id)
        ON DELETE CASCADE,

    avg_post_length NUMERIC(10,2),

    post_frequency NUMERIC(10,4),

    avg_sentence_length NUMERIC(10,2),

    vocabulary_size INT,

    punctuation_rate NUMERIC(10,4),

    technical_term_rate NUMERIC(10,4),

    active_hour_start INT,

    active_hour_end INT,

    top_category TEXT,

    total_posts INT,

    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(actor_id)
);


-- ============================================
-- 8. PERSONA RELATIONSHIPS
-- ============================================

CREATE TABLE persona_relationships (
    relationship_id SERIAL PRIMARY KEY,

    actor_a_id INT REFERENCES actors(actor_id)
        ON DELETE CASCADE,

    actor_b_id INT REFERENCES actors(actor_id)
        ON DELETE CASCADE,

    linguistic_score NUMERIC(5,2),

    behavioral_score NUMERIC(5,2),

    topic_score NUMERIC(5,2),

    temporal_score NUMERIC(5,2),

    overall_confidence NUMERIC(5,2),

    explanation TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(actor_a_id, actor_b_id)
);