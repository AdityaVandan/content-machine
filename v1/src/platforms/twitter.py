from typing import Dict, Any, Optional
import tweepy
import structlog
from src.platforms.base_platform import BasePlatformIntegration
from src.core.models import Platform, ReviewedContent
from src.core.config import settings

logger = structlog.get_logger()


class TwitterIntegration(BasePlatformIntegration):
    """Twitter/X platform integration"""
    
    def __init__(self):
        super().__init__(Platform.TWITTER)
        self.client = None
        self.api = None
    
    def authenticate(self) -> bool:
        """Authenticate with Twitter API"""
        try:
            if not all([
                settings.twitter_api_key,
                settings.twitter_api_secret,
                settings.twitter_access_token,
                settings.twitter_access_token_secret
            ]):
                logger.error("Missing Twitter API credentials")
                return False
            
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_token_secret
            )
            
            # Test authentication
            me = self.client.get_me()
            if me.data:
                logger.info("Twitter authentication successful")
                return True
            else:
                logger.error("Twitter authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Twitter authentication error: {str(e)}")
            return False
    
    def validate_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Validate content against Twitter requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check character count
        if content.character_count > settings.twitter_max_length:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Content exceeds Twitter limit: {content.character_count} > {settings.twitter_max_length} characters"
            )
        
        # Check for empty content
        if not content.final_content.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("Content cannot be empty")
        
        # Check hashtags format
        for hashtag in content.draft.hashtags:
            if not hashtag.startswith('#'):
                validation_result["warnings"].append(f"Hashtag {hashtag} should start with #")
        
        return validation_result
    
    def format_content_for_platform(self, content: ReviewedContent) -> str:
        """Format content for Twitter"""
        formatted_content = content.final_content
        
        # Add hashtags if not already included
        if content.draft.hashtags:
            hashtag_string = " " + " ".join(content.draft.hashtags)
            if hashtag_string not in formatted_content:
                formatted_content += hashtag_string
        
        # Truncate if necessary
        if len(formatted_content) > settings.twitter_max_length:
            # Try to truncate at word boundary
            truncated = formatted_content[:settings.twitter_max_length-3]
            last_space = truncated.rfind(' ')
            if last_space > settings.twitter_max_length * 0.8:  # Don't truncate too early
                formatted_content = truncated[:last_space] + "..."
            else:
                formatted_content = truncated + "..."
        
        return formatted_content
    
    def publish_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Publish content to Twitter"""
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
            
            # Format content
            formatted_content = self.format_content_for_platform(content)
            
            # Publish tweet
            response = self.client.create_tweet(text=formatted_content)
            
            if response.data:
                tweet_url = f"https://twitter.com/user/status/{response.data['id']}"
                logger.info(f"Tweet published successfully: {tweet_url}")
                
                return {
                    "success": True,
                    "content_id": response.data['id'],
                    "url": tweet_url,
                    "platform": "twitter"
                }
            else:
                logger.error("Failed to publish tweet")
                return {
                    "success": False,
                    "error": "Failed to publish tweet"
                }
                
        except Exception as e:
            logger.error(f"Error publishing to Twitter: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get analytics for published tweet"""
        try:
            if not self.is_authenticated():
                return {"error": "Not authenticated"}
            
            # Get tweet metrics
            tweet = self.client.get_tweet(
                content_id,
                tweet_fields=["public_metrics"]
            )
            
            if tweet.data:
                metrics = tweet.data.public_metrics
                return {
                    "impressions": metrics.get("impression_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0)
                }
            else:
                return {"error": "Tweet not found"}
                
        except Exception as e:
            logger.error(f"Error getting Twitter analytics: {str(e)}")
            return {"error": str(e)}
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with Twitter"""
        return self.client is not None
