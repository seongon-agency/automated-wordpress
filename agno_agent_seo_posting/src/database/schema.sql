-- Multi-Project SEO Publishing System Database Schema
-- Version: 1.0 (MVP)
-- Description: Simple schema with JSON columns for flexible configuration

-- Projects table: Stores all project configurations
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,                    -- Unique identifier (e.g., "acme_corp")
    project_name TEXT NOT NULL,                     -- Display name (e.g., "Acme Corporation")
    wordpress_url TEXT NOT NULL,                    -- WordPress site URL
    wordpress_username TEXT NOT NULL,               -- WP username
    wordpress_app_password TEXT NOT NULL,           -- WP application password
    html_configs TEXT,                              -- JSON: HTML transformation patterns
    image_configs TEXT,                             -- JSON: Image processing settings
    status TEXT DEFAULT 'active',                   -- active | inactive | testing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_published_at TIMESTAMP,                    -- Last successful publish
    notes TEXT                                      -- Additional notes for agent
);

-- Publishing history table: Tracks all publishing activities
CREATE TABLE IF NOT EXISTS publishing_history (
    publish_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,                                -- NULL if "no-project" option used
    google_docs_url TEXT NOT NULL,
    wordpress_post_id INTEGER,                      -- WP post ID if successful
    wordpress_post_url TEXT,                        -- Full URL to published post
    post_title TEXT,
    post_status TEXT,                               -- draft | publish
    images_processed INTEGER DEFAULT 0,
    success BOOLEAN,
    error_message TEXT,
    execution_time_seconds REAL,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_publishing_history_project_id ON publishing_history(project_id);
CREATE INDEX IF NOT EXISTS idx_publishing_history_published_at ON publishing_history(published_at DESC);
