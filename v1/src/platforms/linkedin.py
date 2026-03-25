from typing import Dict, Any, Optional
import requests
import structlog
from src.platforms.base_platform import BasePlatformIntegration
from src.core.models import Platform, ReviewedContent
from src.core.config import settings

logger = structlog.get_logger()


class LinkedInIntegration(BasePlatformIntegration):
    """LinkedIn platform integration"""
    
    def __init__(self):
        super().__init__(Platform.LINKEDIN)
        self.access_token = None
        self.base_url = "https://api.linkedin.com/v2"
    
    def authenticate(self) -> bool:
        """Authenticate with LinkedIn API"""
        try:
            if not settings.linkedin_access_token:
                logger.error("Missing LinkedIn access token")
                return False
            
            self.access_token = settings.linkedin_access_token
            
            # Test authentication by getting user profile
            response = self._make_request("/people/~:(id,firstName,lastName)")
            
            if response and "id" in response:
                logger.info("LinkedIn authentication successful")
                return True
            else:
                logger.error("LinkedIn authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn authentication error: {str(e)}")
            return False
    
    def validate_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Validate content against LinkedIn requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check character count
        if content.character_count > settings.linkedin_max_length:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Content exceeds LinkedIn limit: {content.character_count} > {settings.linkedin_max_length} characters"
            )
        
        # Check minimum content length
        if content.character_count < 100:
            validation_result["warnings"].append(
                "Content is quite short for LinkedIn (minimum 100 characters recommended)"
            )
        
        # Check for empty content
        if not content.final_content.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("Content cannot be empty")
        
        return validation_result
    
    def format_content_for_platform(self, content: ReviewedContent) -> str:
        """Format content for LinkedIn"""
        formatted_content = content.final_content
        
        # Add hashtags if not already included
        if content.draft.hashtags:
            hashtag_string = "\n\n" + " ".join(content.draft.hashtags)
            if hashtag_string not in formatted_content:
                formatted_content += hashtag_string
        
        # Add proper line breaks for readability
        formatted_content = formatted_content.replace("\n", "\n\n")
        
        return formatted_content
    
    def publish_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Publish content to LinkedIn"""
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
            
            # Get user profile
            user_profile = self._make_request("/people/~:(id)")
            if not user_profile:
                return {
                    "success": False,
                    "error": "Failed to get user profile"
                }
            
            # Format content
            formatted_content = self.format_content_for_platform(content)
            
            # Create share content
            share_data = {
                "author": f"urn:li:person:{user_profile['id']}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": formatted_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Publish post
            response = self._make_request(
                "/ugcPosts",
                method="POST",
                data=share_data
            )
            
            if response and "id" in response:
                post_url = f"https://www.linkedin.com/feed/update/urn:li:ugcPost:{response['id']}"
                logger.info(f"LinkedIn post published successfully: {post_url}")
                
                return {
                    "success": True,
                    "content_id": response['id'],
                    "url": post_url,
                    "platform": "linkedin"
                }
            else:
                logger.error("Failed to publish LinkedIn post")
                return {
                    "success": False,
                    "error": "Failed to publish LinkedIn post"
                }
                
        except Exception as e:
            logger.error(f"Error publishing to LinkedIn: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get analytics for published LinkedIn post"""
        try:
            if not self.is_authenticated():
                return {"error": "Not authenticated"}
            
            # Get post statistics
            response = self._make_request(
                f"/socialActions/{content_id}",
                params={"fields": "likes,comments,shares"}
            )
            
            if response:
                return {
                    "likes": len(response.get("likes", [])),
                    "comments": len(response.get("comments", [])),
                    "shares": len(response.get("shares", []))
                }
            else:
                return {"error": "Post not found"}
                
        except Exception as e:
            logger.error(f"Error getting LinkedIn analytics: {str(e)}")
            return {"error": str(e)}
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to LinkedIn API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"LinkedIn API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"LinkedIn API request error: {str(e)}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with LinkedIn"""
        return self.access_token is not None
