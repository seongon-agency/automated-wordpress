"""Patterns API Router"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List

from services.ai_patterns import modify_patterns_with_ai, scan_html_for_patterns

logger = logging.getLogger(__name__)
router = APIRouter()


class HtmlPattern(BaseModel):
    element_type: str
    source_pattern: str
    target_pattern: str
    description: Optional[str] = None


class PatternModifyRequest(BaseModel):
    current_patterns: List[HtmlPattern]
    instruction: str

    @field_validator('instruction')
    @classmethod
    def validate_instruction(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError('Instruction must be at least 3 characters')
        if len(v) > 500:
            raise ValueError('Instruction must be 500 characters or less')
        return v.strip()


class PatternModifyResponse(BaseModel):
    success: bool
    patterns: Optional[List[HtmlPattern]] = None
    changes_made: Optional[str] = None
    error: Optional[str] = None


class HtmlScanRequest(BaseModel):
    html_content: str

    @field_validator('html_content')
    @classmethod
    def validate_html_content(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError('HTML content must be at least 10 characters')
        if len(v) > 100000:
            raise ValueError('HTML content exceeds maximum length (100KB)')
        return v


class HtmlScanResponse(BaseModel):
    success: bool
    patterns: Optional[List[HtmlPattern]] = None
    elements_found: Optional[List[str]] = None
    notes: Optional[str] = None
    error: Optional[str] = None


@router.post("/modify", response_model=PatternModifyResponse)
async def modify_patterns(request: PatternModifyRequest):
    """
    Modify HTML patterns using AI based on natural language instruction.

    Examples:
    - "Make all h2 headings blue"
    - "Add class 'highlight' to all paragraphs"
    - "Make links open in new tab"
    """
    try:
        result = await modify_patterns_with_ai(
            current_patterns=[p.model_dump() for p in request.current_patterns],
            instruction=request.instruction
        )

        if result["success"]:
            return PatternModifyResponse(
                success=True,
                patterns=[HtmlPattern(**p) for p in result["patterns"]],
                changes_made=result.get("changes_made")
            )
        else:
            return PatternModifyResponse(
                success=False,
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        logger.error(f"Pattern modification failed: {e}", exc_info=True)
        return PatternModifyResponse(
            success=False,
            error="Failed to modify patterns"
        )


@router.post("/scan", response_model=HtmlScanResponse)
async def scan_html(request: HtmlScanRequest):
    """
    Scan HTML content and extract transformation patterns.

    AI analyzes the sample HTML and generates regex patterns for transformation.
    """
    try:
        result = await scan_html_for_patterns(request.html_content)

        if result["success"]:
            return HtmlScanResponse(
                success=True,
                patterns=[HtmlPattern(**p) for p in result["patterns"]],
                elements_found=result.get("elements_found"),
                notes=result.get("notes")
            )
        else:
            return HtmlScanResponse(
                success=False,
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        logger.error(f"HTML scanning failed: {e}", exc_info=True)
        return HtmlScanResponse(
            success=False,
            error="Failed to scan HTML"
        )
