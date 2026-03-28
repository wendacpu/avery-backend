"""
Infographic Generation API Routes
RESTful API endpoints for the infographic generation system.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging
from sqlalchemy.orm import Session

from api.services.infographic_service import infographic_service, GenerationResult
from api.db.database import get_db
from api.models.infographic import InfographicGeneration
from api.routes.auth import get_current_user
from api.models.user import User
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/infographic", tags=["infographic"])


class TextGenerationRequest(BaseModel):
    """Request model for text-based generation"""
    content: str = Field(..., description="Industry background content")
    job_title: str = Field(default="hybrid", description="cto, ceo, or hybrid")
    perspective: str = Field(default="hybrid", description="Primary perspective")
    count: int = Field(default=3, description="Number of infographics to generate", ge=1, le=10)


class EditRequest(BaseModel):
    """Request model for image editing"""
    image_filename: str = Field(..., description="Filename of original image")
    prompt: str = Field(..., description="Natural language edit instruction")


class URLGenerationRequest(BaseModel):
    """Request model for URL-based generation"""
    url: str = Field(..., description="URL to scrape for context")
    job_title: str = Field(default="hybrid", description="cto, ceo, or hybrid")
    perspective: str = Field(default="hybrid", description="Primary perspective")
    count: int = Field(default=3, description="Number of infographics to generate", ge=1, le=10)


class GenerationResponse(BaseModel):
    """Response model for generation requests"""
    success: bool
    message: str
    results: List[Dict[str, Any]] = Field(default_factory=list)
    total_generated: int = 0
    failed: int = 0


@router.post("/generate/from-text", response_model=GenerationResponse)
async def generate_from_text(
    request: TextGenerationRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate infographics from text input.
    """
    try:
        logger.info(f"User {current_user.email} generating {request.count} infographics from text")

        result = infographic_service.generate_from_text(
            content=request.content,
            job_title=request.job_title,
            perspective=request.perspective,
            count=request.count
        )

        # Save to database
        generation_id = str(uuid.uuid4())
        db_record = InfographicGeneration(
            id=generation_id,
            user_id=current_user.id,
            input_content=request.content,
            input_type="text",
            job_title=request.job_title,
            perspective=request.perspective,
            status="completed" if result.success else "failed",
            generated_count=len([r for r in result.results if r.get('success')]),
            results=result.results
        )
        db.add(db_record)
        db.commit()

        return GenerationResponse(
            success=result.success,
            message=result.message,
            results=result.results,
            total_generated=len([r for r in result.results if r.get('success')]),
            failed=len([r for r in result.results if not r.get('success')])
        )

    except Exception as e:
        logger.error(f"Error generating from text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/generate/from-url")
async def generate_from_url(
    request: URLGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate infographics from URL input.
    """
    try:
        logger.info(f"User {current_user.email} generating from URL: {request.url}")

        result = infographic_service.generate_from_url(
            url=request.url,
            job_title=request.job_title,
            perspective=request.perspective,
            count=request.count
        )

        # Save to database
        generation_id = str(uuid.uuid4())
        db_record = InfographicGeneration(
            id=generation_id,
            user_id=current_user.id,
            input_content=request.url,
            input_type="url",
            job_title=request.job_title,
            perspective=request.perspective,
            status="completed" if result.success else "failed",
            generated_count=len([r for r in result.results if r.get('success')]),
            results=result.results
        )
        db.add(db_record)
        db.commit()

        return GenerationResponse(
            success=result.success,
            message=result.message,
            results=result.results,
            total_generated=len([r for r in result.results if r.get('success')]),
            failed=len([r for r in result.results if not r.get('success')])
        )

    except Exception as e:
        logger.error(f"Error generating from URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/generate/from-file")
async def generate_from_file(
    file: UploadFile = File(...),
    job_title: str = "hybrid",
    perspective: str = "hybrid",
    count: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate infographics from uploaded file (PDF, TXT, MD).
    """
    try:
        logger.info(f"User {current_user.email} generating from file: {file.filename}")

        # Read file content
        content = await file.read()

        result = infographic_service.generate_from_file(
            file_content=content,
            filename=file.filename,
            job_title=job_title,
            perspective=perspective,
            count=count
        )

        # Save to database
        generation_id = str(uuid.uuid4())
        db_record = InfographicGeneration(
            id=generation_id,
            user_id=current_user.id,
            input_content=file.filename,
            input_type="file",
            job_title=job_title,
            perspective=perspective,
            status="completed" if result.success else "failed",
            generated_count=len([r for r in result.results if r.get('success')]),
            results=result.results
        )
        db.add(db_record)
        db.commit()

        return GenerationResponse(
            success=result.success,
            message=result.message,
            results=result.results,
            total_generated=len([r for r in result.results if r.get('success')]),
            failed=len([r for r in result.results if not r.get('success')])
        )

    except Exception as e:
        logger.error(f"Error generating from file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/edit", response_model=Dict[str, Any])
async def edit_infographic(request: EditRequest):
    """
    Edit an existing infographic using natural language.

    Args:
        request: EditRequest with filename and instruction prompt

    Returns:
        Dict with status and new image path
    """
    try:
        logger.info(f"Editing infographic {request.image_filename} with prompt: {request.prompt}")

        # Construct local path
        image_path = f"./generated_images/{request.image_filename}"
        
        result = infographic_service.image_generator.edit_image(
            image_path=image_path,
            prompt=request.prompt,
            save_local=True
        )

        if not result.get("success"):
            return JSONResponse(status_code=400, content=result)

        return {
            "success": True,
            "topic": "Refined Infographic",
            "image_url": result.get("image_url", ""),
            "local_path": result.get("local_path", ""),
            "message": "Image edited successfully"
        }

    except Exception as e:
        logger.error(f"Error editing infographic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")


@router.get("/image/{filename}")
async def get_image(filename: str):
    """
    Retrieve a generated infographic image.

    Args:
        filename: Name of the image file

    Returns:
        FileResponse with the image
    """
    try:
        image_path = Path(f"./generated_images/{filename}")

        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")

        return FileResponse(image_path)

    except Exception as e:
        logger.error(f"Error retrieving image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve image: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the infographic service"""
    return {
        "status": "healthy",
        "service": "infographic-generation",
        "version": "1.0.0"
    }


@router.get("/history")
async def get_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get infographic generation history.

    Args:
        limit: Maximum number of records to return (default: 50)
        offset: Number of records to skip (default: 0)
        db: Database session

    Returns:
        List of infographic generation records
    """
    try:
        logger.info(f"Fetching history for user {current_user.email}: limit={limit}, offset={offset}")

        # Query records ordered by created_at descending
        records = db.query(InfographicGeneration)\
            .filter(InfographicGeneration.user_id == current_user.id)\
            .order_by(InfographicGeneration.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()

        # Convert to list of dicts
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "input_content": record.input_content[:100] + "..." if record.input_content and len(record.input_content) > 100 else record.input_content,
                "input_type": record.input_type,
                "job_title": record.job_title,
                "perspective": record.perspective,
                "framework": record.framework,
                "status": record.status,
                "generated_count": record.generated_count,
                "results": record.results,
                "created_at": record.created_at.isoformat() if record.created_at else None
            })

        return {
            "success": True,
            "count": len(history),
            "total": len(history),  # TODO: Add total count query
            "history": history
        }

    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")
