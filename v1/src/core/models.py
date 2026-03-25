from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from src.core.config import Platform


class ContentType(str, Enum):
    BLOG = "blog"
    TWEET = "tweet"
    LINKEDIN_POST = "linkedin_post"
    MEDIUM_ARTICLE = "medium_article"


class AgentType(str, Enum):
    RESEARCHER = "researcher"
    EDITOR = "editor"
    REVIEWER = "reviewer"


class ContentStatus(str, Enum):
    PENDING = "pending"
    RESEARCHING = "researching"
    EDITING = "editing"
    REVIEWING = "reviewing"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    FAILED = "failed"


class ContentInput(BaseModel):
    topic: str = Field(..., description="Main topic or theme for content")
    keywords: List[str] = Field(default_factory=list, description="Keywords to include")
    target_platforms: List[Platform] = Field(..., description="Target platforms for content")
    content_type: ContentType = Field(..., description="Type of content to generate")
    additional_context: Optional[str] = Field(None, description="Additional context or requirements")
    tone: Optional[str] = Field("professional", description="Desired tone for the content")
    target_audience: Optional[str] = Field("tech professionals", description="Target audience")


class ResearchData(BaseModel):
    topic: str
    key_points: List[str]
    statistics: List[Dict[str, Any]]
    references: List[str]
    trends: List[str]
    competitor_insights: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContentDraft(BaseModel):
    title: Optional[str] = None
    content: str
    platform: Platform
    content_type: ContentType
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    word_count: int
    character_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewedContent(BaseModel):
    draft: ContentDraft
    quality_score: float = Field(ge=0, le=10)
    feedback: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    final_content: str
    approved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContentPiece(BaseModel):
    id: Optional[str] = None
    input_data: ContentInput
    research_data: Optional[ResearchData] = None
    draft: Optional[ContentDraft] = None
    reviewed_content: Optional[ReviewedContent] = None
    status: ContentStatus = ContentStatus.PENDING
    platform: Platform
    published_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HumanReview(BaseModel):
    content_piece_id: str
    reviewer_notes: Optional[str] = None
    approved: bool
    modifications: Optional[str] = None
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduledPost(BaseModel):
    content_piece_id: str
    platform: Platform
    scheduled_time: datetime
    status: str = "scheduled"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    agent_type: AgentType
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
