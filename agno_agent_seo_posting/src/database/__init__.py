"""
Database module for multi-project SEO publishing system.

This module provides database operations for managing projects and publishing history.
"""

from .project_manager import (
    create_project,
    get_project,
    update_project,
    delete_project,
    list_projects,
    log_publish,
    get_publish_history,
    init_database,
)

__all__ = [
    'create_project',
    'get_project',
    'update_project',
    'delete_project',
    'list_projects',
    'log_publish',
    'get_publish_history',
    'init_database',
]
