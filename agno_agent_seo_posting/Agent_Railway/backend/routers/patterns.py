"""
Patterns Router - AI-powered pattern generation and modification.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ai_patterns import modify_patterns_with_ai, generate_patterns_from_template
from database import get_project, update_project


router = APIRouter()


class PatternItem(BaseModel):
    element_type: str
    source_pattern: str
    target_pattern: str


class ModifyPatternsRequest(BaseModel):
    project_id: str
    instruction: str


class GeneratePatternsRequest(BaseModel):
    source_html: str
    target_html: str
    project_id: Optional[str] = None  # If provided, save patterns to project


class DeletePatternRequest(BaseModel):
    project_id: str
    pattern_index: int


@router.post("/modify")
async def modify_patterns(request: ModifyPatternsRequest):
    """
    Modify project patterns using natural language instruction.

    Examples:
    - "Make all h2 headings blue"
    - "Add class 'highlight' to paragraphs"
    - "Remove styling from images"
    """
    try:
        # Get current project patterns
        project = get_project(request.project_id)
        current_patterns = []

        if project.get('html_configs') and project['html_configs'].get('patterns'):
            current_patterns = project['html_configs']['patterns']

        # Modify patterns with AI
        result = modify_patterns_with_ai(current_patterns, request.instruction)

        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error'))

        # Save updated patterns to project
        update_project(
            request.project_id,
            html_configs={"patterns": result['patterns']}
        )

        return {
            "success": True,
            "patterns": result['patterns'],
            "changes_made": result.get('changes_made')
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_patterns(request: GeneratePatternsRequest):
    """
    Generate HTML transformation patterns from source and target HTML.

    Analyzes the HTML structure and creates regex patterns for transformation.
    """
    try:
        result = generate_patterns_from_template(
            source_html=request.source_html,
            target_html=request.target_html
        )

        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error'))

        # If project_id provided, save patterns to project
        if request.project_id:
            update_project(
                request.project_id,
                html_configs={"patterns": result['patterns']}
            )

        return {
            "success": True,
            "patterns": result['patterns'],
            "analysis": result.get('analysis'),
            "saved_to_project": request.project_id is not None
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("")
async def delete_pattern(request: DeletePatternRequest):
    """
    Delete a specific pattern from a project by index.
    """
    try:
        project = get_project(request.project_id)

        if not project.get('html_configs') or not project['html_configs'].get('patterns'):
            raise HTTPException(status_code=400, detail="Project has no patterns")

        patterns = project['html_configs']['patterns']

        if request.pattern_index < 0 or request.pattern_index >= len(patterns):
            raise HTTPException(status_code=400, detail="Invalid pattern index")

        # Remove pattern at index
        deleted_pattern = patterns.pop(request.pattern_index)

        # Save updated patterns
        update_project(
            request.project_id,
            html_configs={"patterns": patterns}
        )

        return {
            "success": True,
            "deleted_pattern": deleted_pattern,
            "remaining_patterns": len(patterns)
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}")
async def get_patterns(project_id: str):
    """
    Get all patterns for a project.
    """
    try:
        project = get_project(project_id)

        patterns = []
        if project.get('html_configs') and project['html_configs'].get('patterns'):
            patterns = project['html_configs']['patterns']

        return {
            "success": True,
            "project_id": project_id,
            "patterns": patterns,
            "count": len(patterns)
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
