from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import structlog
from src.core.models import Platform, ReviewedContent

logger = structlog.get_logger()


class BasePlatformIntegration(ABC):
    """Base class for all platform integrations"""
    
    def __init__(self, platform: Platform):
        self.platform = platform
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform API"""
        pass
    
    @abstractmethod
    def publish_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Publish content to the platform"""
        pass
    
    @abstractmethod
    def validate_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Validate content against platform requirements"""
        pass
    
    @abstractmethod
    def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get analytics for published content"""
        pass
    
    def format_content_for_platform(self, content: ReviewedContent) -> str:
        """Format content according to platform specifications"""
        return content.final_content
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with platform"""
        return True
