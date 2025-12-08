"""API Routers module."""

from .projects import router as projects_router
from .publish import router as publish_router
from .patterns import router as patterns_router
from .history import router as history_router

__all__ = [
    'projects_router',
    'publish_router',
    'patterns_router',
    'history_router'
]
