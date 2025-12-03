-- Multi-Project SEO Publishing System Database Schema for Supabase
-- Version: 2.0 (Supabase/PostgreSQL)
--
-- Run this SQL in Supabase SQL Editor to create the tables:
-- https://app.supabase.com/project/YOUR_PROJECT/sql

-- Projects table: Stores all project configurations
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,                    -- Unique identifier (e.g., "acme_corp")
    project_name TEXT NOT NULL,                     -- Display name (e.g., "Acme Corporation")
    wordpress_url TEXT NOT NULL,                    -- WordPress site URL
    wordpress_username TEXT NOT NULL,               -- WP username
    wordpress_app_password TEXT NOT NULL,           -- WP application password
    html_configs JSONB,                             -- JSON: HTML transformation patterns
    image_configs JSONB,                            -- JSON: Image processing settings
    status TEXT DEFAULT 'active',                   -- active | inactive | testing
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_published_at TIMESTAMPTZ,                  -- Last successful publish
    notes TEXT                                      -- Additional notes for agent
);

-- Publishing history table: Tracks all publishing activities
CREATE TABLE IF NOT EXISTS publishing_history (
    publish_id SERIAL PRIMARY KEY,
    project_id TEXT REFERENCES projects(project_id) ON DELETE SET NULL,
    google_docs_url TEXT NOT NULL,
    wordpress_post_id INTEGER,                      -- WP post ID if successful
    wordpress_post_url TEXT,                        -- Full URL to published post
    post_title TEXT,
    post_status TEXT,                               -- draft | publish
    images_processed INTEGER DEFAULT 0,
    success BOOLEAN,
    error_message TEXT,
    execution_time_seconds REAL,
    published_at TIMESTAMPTZ DEFAULT NOW(),
    saved_html_docs_url TEXT                        -- URL to saved HTML Google Doc (optional)
);

-- To add this column to an existing database, run:
-- ALTER TABLE publishing_history ADD COLUMN IF NOT EXISTS saved_html_docs_url TEXT;

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_publishing_history_project_id ON publishing_history(project_id);
CREATE INDEX IF NOT EXISTS idx_publishing_history_published_at ON publishing_history(published_at DESC);

-- Enable Row Level Security (optional but recommended)
-- ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE publishing_history ENABLE ROW LEVEL SECURITY;

-- Create policies for anonymous access (if needed for Streamlit)
-- CREATE POLICY "Allow all access to projects" ON projects FOR ALL USING (true);
-- CREATE POLICY "Allow all access to publishing_history" ON publishing_history FOR ALL USING (true);
