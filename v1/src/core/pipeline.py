from typing import List, Dict, Any, Optional
import uuid
import structlog
from datetime import datetime
from src.agents import ResearcherAgent, EditorAgent, ReviewerAgent
from src.platforms import TwitterIntegration, LinkedInIntegration, MediumIntegration
from src.core.models import (
    ContentInput, ContentPiece, ContentStatus, AgentResult, 
    HumanReview, Platform, ContentType
)
from src.core.config import settings

logger = structlog.get_logger()


class ContentPipeline:
    """Main orchestrator for the content creation pipeline"""
    
    def __init__(self):
        self.agents = {
            "researcher": ResearcherAgent(),
            "editor": EditorAgent(),
            "reviewer": ReviewerAgent()
        }
        
        self.platform_integrations = {
            Platform.TWITTER: TwitterIntegration(),
            Platform.LINKEDIN: LinkedInIntegration(),
            Platform.MEDIUM: MediumIntegration()
        }
    
    def create_content(self, input_data: ContentInput) -> List[ContentPiece]:
        """Create content for all specified platforms"""
        try:
            logger.info(f"Starting content creation for topic: {input_data.topic}")
            
            content_pieces = []
            
            # Step 1: Research
            research_result = self._execute_research(input_data)
            if not research_result.success:
                logger.error("Research phase failed")
                return []
            
            # Step 2: Create drafts for each platform
            drafts = self._create_drafts(input_data, research_result.data)
            
            # Step 3: Review each draft
            for draft_data in drafts:
                reviewed_content = self._review_draft(draft_data, input_data)
                
                # Create content piece
                content_piece = ContentPiece(
                    id=str(uuid.uuid4()),
                    input_data=input_data,
                    research_data=research_result.data.get("research_data"),
                    draft=draft_data,
                    reviewed_content=reviewed_content,
                    status=ContentStatus.HUMAN_REVIEW if settings.human_review_required else ContentStatus.APPROVED,
                    platform=draft_data["platform"]
                )
                
                content_pieces.append(content_piece)
            
            logger.info(f"Created {len(content_pieces)} content pieces")
            return content_pieces
            
        except Exception as e:
            logger.error(f"Error in content creation pipeline: {str(e)}")
            return []
    
    def _execute_research(self, input_data: ContentInput) -> AgentResult:
        """Execute the research phase"""
        researcher_input = {
            "topic": input_data.topic,
            "keywords": input_data.keywords,
            "target_audience": input_data.target_audience,
            "tone": input_data.tone
        }
        
        return self.agents["researcher"].execute(researcher_input)
    
    def _create_drafts(self, input_data: ContentInput, research_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create drafts for all target platforms"""
        drafts = []
        
        editor_input = {
            "research_data": research_data.get("research_data"),
            "topic": input_data.topic,
            "target_platforms": input_data.target_platforms,
            "content_type": input_data.content_type,
            "tone": input_data.tone,
            "target_audience": input_data.target_audience
        }
        
        editor_result = self.agents["editor"].execute(editor_input)
        
        if editor_result.success:
            drafts = editor_result.data.get("drafts", [])
        else:
            logger.error("Editor agent failed")
        
        return drafts
    
    def _review_draft(self, draft_data: Dict[str, Any], input_data: ContentInput):
        """Review a single draft"""
        reviewer_input = {
            "draft": draft_data,
            "topic": input_data.topic,
            "target_audience": input_data.target_audience,
            "tone": input_data.tone
        }
        
        reviewer_result = self.agents["reviewer"].execute(reviewer_input)
        
        if reviewer_result.success:
            return reviewer_result.data.get("reviewed_content")
        else:
            logger.error("Reviewer agent failed")
            return None
    
    def approve_content(self, content_piece_id: str, human_review: HumanReview) -> bool:
        """Approve content after human review"""
        try:
            # In a real implementation, you would save this to database
            logger.info(f"Content {content_piece_id} approved by human reviewer")
            return True
        except Exception as e:
            logger.error(f"Error approving content: {str(e)}")
            return False
    
    def publish_content(self, content_piece: ContentPiece, 
                       scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Publish content to the specified platform"""
        try:
            platform = content_piece.platform
            reviewed_content = content_piece.reviewed_content
            
            if not reviewed_content:
                return {"success": False, "error": "No reviewed content available"}
            
            # Get platform integration
            integration = self.platform_integrations.get(platform)
            if not integration:
                return {"success": False, "error": f"No integration for platform {platform}"}
            
            # Authenticate if needed
            if not integration.is_authenticated():
                if not integration.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            # Validate content
            validation = integration.validate_content(reviewed_content)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "Content validation failed",
                    "validation_errors": validation["errors"]
                }
            
            # Publish content
            if scheduled_time:
                # Schedule for later (would integrate with Celery in production)
                return self._schedule_publication(content_piece, scheduled_time)
            else:
                # Publish immediately
                result = integration.publish_content(reviewed_content)
                
                if result.get("success"):
                    logger.info(f"Content published successfully to {platform.value}")
                    return result
                else:
                    logger.error(f"Failed to publish to {platform.value}: {result.get('error')}")
                    return result
            
        except Exception as e:
            logger.error(f"Error publishing content: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _schedule_publication(self, content_piece: ContentPiece, 
                             scheduled_time: datetime) -> Dict[str, Any]:
        """Schedule content for later publication"""
        # This would integrate with Celery for actual scheduling
        logger.info(f"Content scheduled for publication at {scheduled_time}")
        
        return {
            "success": True,
            "scheduled": True,
            "scheduled_time": scheduled_time.isoformat(),
            "content_id": content_piece.id
        }
    
    def get_content_analytics(self, content_piece_id: str, platform: Platform) -> Dict[str, Any]:
        """Get analytics for published content"""
        try:
            integration = self.platform_integrations.get(platform)
            if not integration:
                return {"error": f"No integration for platform {platform}"}
            
            # In a real implementation, you would retrieve the published content ID
            # For now, return placeholder
            return {"message": "Analytics functionality requires database integration"}
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline status"""
        return {
            "agents": list(self.agents.keys()),
            "platforms": [p.value for p in self.platform_integrations.keys()],
            "human_review_required": settings.human_review_required,
            "default_llm_model": settings.default_llm_model
        }
