"""
Pydantic Models for Request/Response Validation

Defines the schema for all API requests and responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ============================================================================
# Base Response Models
# ============================================================================

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Project Models
# ============================================================================

class HTMLPattern(BaseModel):
    """HTML transformation pattern"""
    element_type: str = Field(..., description="HTML element type (p, h1, h2, etc.)")
    source_pattern: str = Field(..., description="Regex pattern to match")
    target_pattern: str = Field(..., description="Replacement pattern")


class HTMLConfig(BaseModel):
    """HTML transformation configuration"""
    patterns: List[HTMLPattern] = Field(default_factory=list)


class ImageConfig(BaseModel):
    """Image processing configuration"""
    target_width: int = Field(800, description="Target width in pixels")
    quality: int = Field(92, description="JPEG quality (0-100)")
    format: str = Field("JPEG", description="Image format (JPEG, PNG, WEBP)")
    css_classes: Optional[str] = Field(None, description="CSS classes for images")


class ProjectCreate(BaseModel):
    """Create new project request"""
    project_id: str = Field(..., min_length=1, max_length=100, description="Unique project identifier")
    project_name: str = Field(..., min_length=1, description="Human-readable project name")
    wordpress_url: HttpUrl = Field(..., description="WordPress site URL")
    wordpress_username: str = Field(..., description="WordPress username")
    wordpress_app_password: str = Field(..., description="WordPress application password")
    html_configs: Optional[HTMLConfig] = None
    image_configs: Optional[ImageConfig] = None
    notes: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Update project request"""
    project_name: Optional[str] = None
    wordpress_url: Optional[HttpUrl] = None
    wordpress_username: Optional[str] = None
    wordpress_app_password: Optional[str] = None
    html_configs: Optional[HTMLConfig] = None
    image_configs: Optional[ImageConfig] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response"""
    project_id: str
    project_name: str
    wordpress_url: str
    wordpress_username: str
    html_patterns_count: int = 0
    image_width: Optional[int] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_published_at: Optional[str] = None
    notes: Optional[str] = None


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with configurations"""
    html_configs: Optional[Dict[str, Any]] = None
    image_configs: Optional[Dict[str, Any]] = None


# ============================================================================
# Publishing Models
# ============================================================================

class PublishRequest(BaseModel):
    """Content publishing request"""
    google_docs_url: HttpUrl = Field(..., description="Google Docs URL to publish")
    project_id: Optional[str] = Field(None, description="Project ID (optional, for transformations)")


class PublishResponse(BaseModel):
    """Publishing result"""
    success: bool
    post_title: Optional[str] = None
    post_url: Optional[str] = None
    wordpress_post_id: Optional[int] = None
    images_processed: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    step_failed: Optional[str] = None


class PublishHistoryItem(BaseModel):
    """Publishing history item"""
    id: int
    google_docs_url: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    success: bool
    post_title: Optional[str] = None
    post_url: Optional[str] = None
    wordpress_post_id: Optional[int] = None
    images_processed: int = 0
    execution_time: float = 0.0
    error_message: Optional[str] = None
    published_at: str


# ============================================================================
# Pattern Modification Models
# ============================================================================

class PatternModifyRequest(BaseModel):
    """Natural language pattern modification request"""
    project_id: str = Field(..., description="Project ID to modify")
    instruction: str = Field(..., min_length=1, description="Natural language instruction")


class PatternModifyPreview(BaseModel):
    """Pattern modification preview"""
    element_type: str
    current_pattern: str
    modified_pattern: str
    changes_description: str


class PatternModifyResponse(BaseModel):
    """Pattern modification result"""
    success: bool
    previews: List[PatternModifyPreview] = Field(default_factory=list)
    error: Optional[str] = None


# ============================================================================
# HTML Analysis Models
# ============================================================================

class HTMLAnalysisRequest(BaseModel):
    """HTML sample analysis request"""
    html_sample: str = Field(..., min_length=1, description="Sample HTML to analyze")


class HTMLAnalysisResponse(BaseModel):
    """HTML analysis result"""
    success: bool
    html_configs: Optional[HTMLConfig] = None
    patterns_found: int = 0
    error: Optional[str] = None


# ============================================================================
# Batch Processing Models
# ============================================================================

class BatchPublishItem(BaseModel):
    """Single item in batch publish request"""
    google_docs_url: HttpUrl
    project_id: Optional[str] = None
    item_id: Optional[str] = None  # For tracking in Lark Base


class BatchPublishRequest(BaseModel):
    """Batch publishing request"""
    items: List[BatchPublishItem] = Field(..., min_items=1, max_items=50)


class BatchPublishItemResult(BaseModel):
    """Result for single batch item"""
    item_id: Optional[str] = None
    google_docs_url: str
    success: bool
    post_url: Optional[str] = None
    error: Optional[str] = None


class BatchPublishResponse(BaseModel):
    """Batch publishing result"""
    total: int
    successful: int
    failed: int
    results: List[BatchPublishItemResult]


# ============================================================================
# Statistics Models
# ============================================================================

class ProjectStats(BaseModel):
    """Project statistics"""
    project_id: str
    project_name: str
    total_publishes: int
    successful_publishes: int
    failed_publishes: int
    success_rate: float
    avg_execution_time: float
    last_publish_date: Optional[str] = None


class SystemStats(BaseModel):
    """System-wide statistics"""
    total_projects: int
    active_projects: int
    total_publishes: int
    successful_publishes: int
    failed_publishes: int
    success_rate: float
    avg_execution_time: float
