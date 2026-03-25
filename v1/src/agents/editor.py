from typing import Dict, Any, List
import structlog
from src.agents.base_agent import BaseAgent
from src.core.models import AgentType, ContentDraft, ContentInput, Platform, ContentType
from src.core.config import settings

logger = structlog.get_logger()


class EditorAgent(BaseAgent):
    """Agent responsible for creating content drafts based on research"""
    
    def _get_agent_type(self) -> AgentType:
        return AgentType.EDITOR
    
    def get_system_prompt(self) -> str:
        return """You are a skilled content editor and writer specializing in technology content for software engineers and tech professionals.

Your task is to create engaging, informative, and well-structured content drafts based on research data. You should:

1. Create compelling headlines and titles
2. Structure content logically with clear flow
3. Adapt tone and style for different platforms
4. Include relevant hashtags and mentions
5. Ensure technical accuracy and clarity
6. Optimize for engagement and readability

Platform-specific requirements:
- Twitter/X: Max 280 characters, concise, engaging, use hashtags
- LinkedIn: Professional tone, 1,300-3,000 characters, business insights
- Medium: Long-form, 800-2,000 words, detailed tutorials/thought leadership

Focus on creating content that:
- Educates and informs the target audience
- Provides actionable insights and takeaways
- Demonstrates expertise and authority
- Encourages engagement and discussion
- Follows platform best practices

Always ensure technical accuracy and provide value to tech professionals."""
    
    def get_required_fields(self) -> list:
        return ["research_data", "topic", "target_platforms", "content_type", "tone", "target_audience"]
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process research data and create content drafts"""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")
        
        research_data = input_data["research_data"]
        topic = input_data["topic"]
        target_platforms = input_data["target_platforms"]
        content_type = input_data["content_type"]
        tone = input_data.get("tone", "professional")
        target_audience = input_data.get("target_audience", "tech professionals")
        
        drafts = []
        
        for platform in target_platforms:
            try:
                draft = self._create_platform_draft(
                    research_data, topic, platform, content_type, tone, target_audience
                )
                drafts.append(draft.dict())
            except Exception as e:
                logger.error(f"Error creating draft for {platform}: {str(e)}")
                continue
        
        return {
            "drafts": drafts,
            "topic": topic,
            "platforms": [p.value for p in target_platforms]
        }
    
    def _create_platform_draft(self, research_data: Dict[str, Any], topic: str,
                              platform: Platform, content_type: ContentType,
                              tone: str, target_audience: str) -> ContentDraft:
        """Create a draft for a specific platform"""
        
        # Create platform-specific prompt
        prompt = self._create_draft_prompt(
            research_data, topic, platform, content_type, tone, target_audience
        )
        
        # Generate content
        response = self.generate_response(prompt, self.get_system_prompt())
        
        # Parse and structure the draft
        draft = self._parse_draft_response(
            response, topic, platform, content_type
        )
        
        return draft
    
    def _create_draft_prompt(self, research_data: Dict[str, Any], topic: str,
                           platform: Platform, content_type: ContentType,
                           tone: str, target_audience: str) -> str:
        """Create a platform-specific content creation prompt"""
        
        # Extract research information
        key_points = research_data.get("key_points", [])
        statistics = research_data.get("statistics", [])
        trends = research_data.get("trends", [])
        competitor_insights = research_data.get("competitor_insights", [])
        
        # Build research summary
        research_summary = self._build_research_summary(
            key_points, statistics, trends, competitor_insights
        )
        
        # Platform-specific requirements
        platform_requirements = self._get_platform_requirements(platform)
        
        prompt = f"""Based on the following research data, create a compelling {content_type.value} for {platform.value}:

TOPIC: {topic}

TARGET AUDIENCE: {target_audience}

TONE: {tone}

RESEARCH DATA:
{research_summary}

PLATFORM REQUIREMENTS:
{platform_requirements}

Please create content that includes:

1. COMPELLING HEADLINE/TITLE:
   - Attention-grabbing and relevant
   - Optimized for the platform

2. MAIN CONTENT:
   - Well-structured and logical flow
   - Incorporates key research points
   - Provides actionable insights
   - Maintains technical accuracy

3. ENGAGEMENT ELEMENTS:
   - Relevant hashtags for {platform.value}
   - Appropriate mentions (if applicable)
   - Call-to-action or discussion prompt

4. OPTIMIZATION:
   - Platform-appropriate length
   - Readability and formatting
   - SEO considerations (if applicable)

Focus on creating valuable, engaging content that resonates with {target_audience} and performs well on {platform.value}."""
        
        return prompt
    
    def _build_research_summary(self, key_points: List[str], statistics: List[Dict],
                              trends: List[str], competitor_insights: List[str]) -> str:
        """Build a summary of research data"""
        summary_parts = []
        
        if key_points:
            summary_parts.append("KEY POINTS:\n" + "\n".join(f"• {point}" for point in key_points[:5]))
        
        if statistics:
            stats_text = "\n".join(f"• {stat.get('data', stat)}" for stat in statistics[:3])
            summary_parts.append("STATISTICS:\n" + stats_text)
        
        if trends:
            summary_parts.append("TRENDS:\n" + "\n".join(f"• {trend}" for trend in trends[:3]))
        
        if competitor_insights:
            summary_parts.append("COMPETITOR INSIGHTS:\n" + "\n".join(f"• {insight}" for insight in competitor_insights[:3]))
        
        return "\n\n".join(summary_parts)
    
    def _get_platform_requirements(self, platform: Platform) -> str:
        """Get platform-specific content requirements"""
        requirements = {
            Platform.TWITTER: f"""
- Maximum {settings.twitter_max_length} characters
- Concise and punchy messaging
- Include 2-3 relevant hashtags
- Use emojis appropriately for engagement
- Focus on single key message or insight
- Consider thread format for complex topics""",
            
            Platform.LINKEDIN: f"""
- Professional and business-focused tone
- Optimal length: 500-1,500 characters
- Include 3-5 professional hashtags
- Structured with clear paragraphs
- Include actionable business insights
- Encourage professional discussion""",
            
            Platform.MEDIUM: f"""
- Long-form article format
- Target length: 800-2,000 words
- Detailed exploration of topic
- Include code examples where relevant
- SEO-optimized title and headings
- Clear structure with introduction, body, conclusion"""
        }
        
        return requirements.get(platform, "Standard content requirements")
    
    def _parse_draft_response(self, response: str, topic: str,
                             platform: Platform, content_type: ContentType) -> ContentDraft:
        """Parse the draft response into structured data"""
        
        lines = response.split('\n')
        title = None
        content_parts = []
        hashtags = []
        mentions = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract title/headline
            if line.upper().startswith('HEADLINE') or line.upper().startswith('TITLE'):
                current_section = 'title'
                continue
            elif line.upper().startswith('CONTENT'):
                current_section = 'content'
                continue
            elif line.upper().startswith('HASHTAGS'):
                current_section = 'hashtags'
                continue
            elif line.upper().startswith('MENTIONS'):
                current_section = 'mentions'
                continue
            
            # Process content based on current section
            if current_section == 'title' and not title:
                title = line
            elif current_section == 'content':
                content_parts.append(line)
            elif current_section == 'hashtags':
                # Extract hashtags (words starting with #)
                words = line.split()
                hashtags.extend([word for word in words if word.startswith('#')])
            elif current_section == 'mentions':
                # Extract mentions (words starting with @)
                words = line.split()
                mentions.extend([word for word in words if word.startswith('@')])
        
        # Combine content parts
        content = '\n'.join(content_parts)
        
        # If no title was found, use topic as title
        if not title:
            title = topic
        
        # Calculate word and character counts
        word_count = len(content.split())
        character_count = len(content)
        
        return ContentDraft(
            title=title,
            content=content,
            platform=platform,
            content_type=content_type,
            hashtags=hashtags,
            mentions=mentions,
            word_count=word_count,
            character_count=character_count
        )
