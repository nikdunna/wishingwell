-- Wishing Well Database Schema
-- PostgreSQL Schema for Topic Modeling Platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Topics table: Topic metadata from BERTopic (created first, no dependencies)
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    wish_count INTEGER DEFAULT 0,
    embedding_model VARCHAR(100),
    topic_model_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Model updates: Training history (no dependencies)
CREATE TABLE model_updates (
    id SERIAL PRIMARY KEY,
    version INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'running', 'completed', 'failed'
    wishes_count INTEGER DEFAULT 0,
    topics_created INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    configuration JSONB
);

-- Rejected wishes: Content moderation log (no dependencies)
CREATE TABLE rejected_wishes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    rejection_reason VARCHAR(255) NOT NULL,
    moderation_model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Wishes table: Core wish storage (depends on topics)
CREATE TABLE wishes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Topic-Wishes junction: Many-to-many with probabilities (depends on topics and wishes)
CREATE TABLE topic_wishes (
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    wish_id UUID REFERENCES wishes(id) ON DELETE CASCADE,
    probability DECIMAL(5,4) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (topic_id, wish_id)
);

-- Indexes for performance
CREATE INDEX idx_wishes_created_at ON wishes(created_at DESC);
CREATE INDEX idx_wishes_topic_id ON wishes(topic_id);
CREATE INDEX idx_wishes_is_deleted ON wishes(is_deleted);
CREATE INDEX idx_topics_wish_count ON topics(wish_count DESC);
CREATE INDEX idx_topic_wishes_probability ON topic_wishes(probability DESC);
CREATE INDEX idx_topic_wishes_is_primary ON topic_wishes(is_primary);
CREATE INDEX idx_model_updates_version ON model_updates(version);
CREATE INDEX idx_model_updates_status ON model_updates(status);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_wishes_updated_at BEFORE UPDATE ON wishes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
