from typing import Dict, Any, Optional
import requests
import json
import structlog
from src.platforms.base_platform import BasePlatformIntegration
from src.core.models import Platform, ReviewedContent
from src.core.config import settings

logger = structlog.get_logger()


class MediumIntegration(BasePlatformIntegration):
    """Medium platform integration"""
    
    def __init__(self):
        super().__init__(Platform.MEDIUM)
        self.integration_token = None
        self.base_url = "https://api.medium.com/v1"
    
    def authenticate(self) -> bool:
        """Authenticate with Medium API"""
        try:
            if not settings.medium_integration_token:
                logger.error("Missing Medium integration token")
                return False
            
            self.integration_token = settings.medium_integration_token
            
            # Test authentication by getting user details
            response = self._make_request("/me")
            
            if response and "data" in response:
                logger.info("Medium authentication successful")
                return True
            else:
                logger.error("Medium authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Medium authentication error: {str(e)}")
            return False
    
    def validate_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Validate content against Medium requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check word count
        if content.word_count < settings.medium_min_length:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Content too short for Medium: {content.word_count} < {settings.medium_min_length} words"
            )
        
        if content.word_count > settings.medium_max_length:
            validation_result["warnings"].append(
                f"Content quite long for Medium: {content.word_count} > {settings.medium_max_length} words"
            )
        
        # Check for title
        if not content.draft.title or not content.draft.title.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("Medium articles must have a title")
        
        # Check for empty content
        if not content.final_content.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("Content cannot be empty")
        
        return validation_result
    
    def format_content_for_platform(self, content: ReviewedContent) -> str:
        """Format content for Medium"""
        formatted_content = content.final_content
        
        # Convert to HTML format for Medium
        # Add proper paragraph tags
        paragraphs = formatted_content.split('\n\n')
        html_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Check if it's a heading (simple heuristic)
                if len(paragraph.strip()) < 100 and paragraph.strip().endswith('?'):
                    html_paragraphs.append(f"<h2>{paragraph.strip()}</h2>")
                else:
                    html_paragraphs.append(f"<p>{paragraph.strip()}</p>")
        
        html_content = "\n".join(html_paragraphs)
        
        return html_content
    
    def publish_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Publish content to Medium"""
        try:
            if not self.is_authenticated():
                if not self.authenticate():
                    return {
                        "success": False,
                        "error": "Authentication failed"
                    }
            
            # Validate content
            validation = self.validate_content(content)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "Content validation failed",
                    "validation_errors": validation["errors"]
                }
            
            # Get user details
            user_response = self._make_request("/me")
            if not user_response or "data" not in user_response:
                return {
                    "success": False,
                    "error": "Failed to get user details"
                }
            
            author_id = user_response["data"]["id"]
            
            # Format content for Medium
            html_content = self.format_content_for_platform(content)
            
            # Create post data
            post_data = {
                "title": content.draft.title or "Untitled",
                "contentFormat": "html",
                "content": html_content,
                "tags": self._extract_tags(content),
                "publishStatus": "public"
            }
            
            # Publish article
            response = self._make_request(
                f"/users/{author_id}/posts",
                method="POST",
                data=post_data
            )
            
            if response and "data" in response:
                post_url = response["data"]["url"]
                post_id = response["data"]["id"]
                logger.info(f"Medium article published successfully: {post_url}")
                
                return {
                    "success": True,
                    "content_id": post_id,
                    "url": post_url,
                    "platform": "medium"
                }
            else:
                logger.error("Failed to publish Medium article")
                return {
                    "success": False,
                    "error": "Failed to publish Medium article"
                }
                
        except Exception as e:
            logger.error(f"Error publishing to Medium: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get analytics for published Medium article"""
        try:
            if not self.is_authenticated():
                return {"error": "Not authenticated"}
            
            # Medium's API doesn't provide detailed analytics directly
            # You would need to use Medium's analytics endpoint or third-party tools
            # This is a placeholder implementation
            
            return {
                "views": "Not available via API",
                "reads": "Not available via API",
                "read_ratio": "Not available via API",
                "fans": "Not available via API",
                "note": "Analytics not available through Medium API"
            }
                
        except Exception as e:
            logger.error(f"Error getting Medium analytics: {str(e)}")
            return {"error": str(e)}
    
    def _extract_tags(self, content: ReviewedContent) -> list:
        """Extract tags from content for Medium"""
        tags = []
        
        # Add hashtags as tags (remove # symbol)
        for hashtag in content.draft.hashtags:
            tag = hashtag.lstrip('#')
            if len(tag) <= 25:  # Medium tag limit
                tags.append(tag)
        
        # Add some default tech tags if none provided
        if not tags:
            tags = ["technology", "programming", "software"]
        
        # Limit to 5 tags (Medium limit)
        return tags[:5]
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to Medium API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.integration_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Medium API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Medium API request error: {str(e)}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with Medium"""
        return self.integration_token is not None
