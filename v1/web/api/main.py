from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
import os

from src import ContentPipeline, ContentScheduler
from src.core.models import ContentInput, Platform, ContentType, HumanReview

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Content Machine API",
    description="LangChain-powered content creation and publishing system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="web/frontend"), name="static")

# Initialize services
pipeline = ContentPipeline()
scheduler = ContentScheduler()

# Pydantic models for API
class ContentRequest(BaseModel):
    topic: str
    keywords: List[str] = []
    target_platforms: List[str]
    content_type: str
    additional_context: Optional[str] = None
    tone: Optional[str] = "professional"
    target_audience: Optional[str] = "tech professionals"
    scheduled_time: Optional[datetime] = None

class ReviewRequest(BaseModel):
    content_piece_id: str
    approved: bool
    reviewer_notes: Optional[str] = None
    modifications: Optional[str] = None

class PublishRequest(BaseModel):
    content_piece_id: str
    platform: str
    scheduled_time: Optional[datetime] = None

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint - redirect to frontend"""
    return FileResponse("web/frontend/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/status")
async def get_status():
    """Get pipeline status"""
    try:
        return pipeline.get_pipeline_status()
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/content/create")
async def create_content(request: ContentRequest, background_tasks: BackgroundTasks):
    """Create content for specified platforms"""
    try:
        # Convert string platforms to enum
        platform_enums = []
        for platform_str in request.target_platforms:
            try:
                platform_enums.append(Platform(platform_str))
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid platform: {platform_str}"
                )
        
        # Convert content type
        try:
            content_type_enum = ContentType(request.content_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type: {request.content_type}"
            )
        
        # Create ContentInput
        content_input = ContentInput(
            topic=request.topic,
            keywords=request.keywords,
            target_platforms=platform_enums,
            content_type=content_type_enum,
            additional_context=request.additional_context,
            tone=request.tone,
            target_audience=request.target_audience
        )
        
        if request.scheduled_time:
            # Schedule for later
            result = scheduler.schedule_content_creation(content_input, request.scheduled_time)
        else:
            # Create immediately
            content_pieces = pipeline.create_content(content_input)
            
            # Schedule review notifications if human review is required
            for piece in content_pieces:
                background_tasks.add_task(
                    scheduler.schedule_review_notification,
                    piece.id
                )
            
            result = {
                "success": True,
                "content_pieces": [piece.dict() for piece in content_pieces],
                "created_at": datetime.utcnow().isoformat()
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/content/review")
async def review_content(request: ReviewRequest):
    """Submit human review for content"""
    try:
        human_review = HumanReview(
            content_piece_id=request.content_piece_id,
            approved=request.approved,
            reviewer_notes=request.reviewer_notes,
            modifications=request.modifications
        )
        
        success = pipeline.approve_content(request.content_piece_id, human_review)
        
        if success:
            return {"success": True, "message": "Review submitted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to submit review")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/content/publish")
async def publish_content(request: PublishRequest, background_tasks: BackgroundTasks):
    """Publish content to specified platform"""
    try:
        # Convert platform string to enum
        try:
            platform_enum = Platform(request.platform)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {request.platform}"
            )
        
        if request.scheduled_time:
            # Schedule for later
            result = scheduler.schedule_content_publication(
                request.content_piece_id,
                platform_enum,
                request.scheduled_time
            )
        else:
            # Publish immediately (would need database integration)
            result = {"message": "Publish functionality requires database integration"}
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a scheduled task"""
    try:
        result = scheduler.get_task_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a scheduled task"""
    try:
        result = scheduler.cancel_task(task_id)
        return result
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_scheduled_tasks():
    """Get list of scheduled tasks"""
    try:
        result = scheduler.get_scheduled_tasks()
        return result
    except Exception as e:
        logger.error(f"Error getting scheduled tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/platforms")
async def get_platforms():
    """Get available platforms"""
    return {
        "platforms": [
            {"value": "twitter", "name": "Twitter/X", "max_length": 280},
            {"value": "linkedin", "name": "LinkedIn", "max_length": 3000},
            {"value": "medium", "name": "Medium", "min_length": 800, "max_length": 2000}
        ]
    }

@app.get("/content-types")
async def get_content_types():
    """Get available content types"""
    return {
        "content_types": [
            {"value": "blog", "name": "Blog Post"},
            {"value": "tweet", "name": "Tweet"},
            {"value": "linkedin_post", "name": "LinkedIn Post"},
            {"value": "medium_article", "name": "Medium Article"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
