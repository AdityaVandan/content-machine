from typing import Dict, Any, List
import structlog
from src.agents.base_agent import BaseAgent
from src.core.models import AgentType, ContentDraft, ReviewedContent, Platform

logger = structlog.get_logger()


class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing and improving content drafts"""
    
    def _get_agent_type(self) -> AgentType:
        return AgentType.REVIEWER
    
    def get_system_prompt(self) -> str:
        return """You are a skilled content reviewer and quality assurance specialist for technology content.

Your task is to review content drafts and provide:
1. Quality assessment and scoring (1-10 scale)
2. Detailed feedback on strengths and weaknesses
3. Specific improvement suggestions
4. Final polished content version

Review criteria:
- Technical accuracy and clarity
- Content structure and flow
- Engagement and readability
- Platform appropriateness
- Value proposition for target audience
- SEO and optimization factors
- Grammar and style

For each review, provide:
- Overall quality score (1-10)
- Specific feedback points
- Actionable improvement suggestions
- Refined final version of content

Focus on ensuring content meets high standards for technical content and provides genuine value to tech professionals. Be constructive and specific in your feedback."""
    
    def get_required_fields(self) -> list:
        return ["draft", "topic", "target_audience", "tone"]
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review content drafts and provide quality assessment"""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")
        
        draft_data = input_data["draft"]
        topic = input_data["topic"]
        target_audience = input_data.get("target_audience", "tech professionals")
        tone = input_data.get("tone", "professional")
        
        # Convert draft data to ContentDraft object
        draft = ContentDraft(**draft_data)
        
        # Create review prompt
        review_prompt = self._create_review_prompt(
            draft, topic, target_audience, tone
        )
        
        # Generate review response
        review_response = self.generate_response(
            review_prompt,
            self.get_system_prompt()
        )
        
        # Parse review response
        reviewed_content = self._parse_review_response(
            review_response, draft
        )
        
        return {
            "reviewed_content": reviewed_content.dict(),
            "platform": draft.platform.value,
            "quality_score": reviewed_content.quality_score
        }
    
    def _create_review_prompt(self, draft: ContentDraft, topic: str,
                             target_audience: str, tone: str) -> str:
        """Create a comprehensive review prompt"""
        
        prompt = f"""Please review the following content draft and provide detailed feedback:

CONTENT DETAILS:
- Topic: {topic}
- Platform: {draft.platform.value}
- Target Audience: {target_audience}
- Tone: {tone}

DRAFT CONTENT:
Title: {draft.title}
Content: {draft.content}
Hashtags: {', '.join(draft.hashtags) if draft.hashtags else 'None'}
Mentions: {', '.join(draft.mentions) if draft.mentions else 'None'}

Content Metrics:
- Word Count: {draft.word_count}
- Character Count: {draft.character_count}

Please provide a comprehensive review including:

1. QUALITY SCORE (1-10):
   - Overall assessment of content quality
   - Consider technical accuracy, clarity, engagement, and value

2. STRENGTHS:
   - What works well in this content
   - Positive aspects to maintain

3. AREAS FOR IMPROVEMENT:
   - Specific weaknesses or issues
   - Opportunities for enhancement

4. SPECIFIC SUGGESTIONS:
   - Actionable recommendations for improvement
   - Concrete changes to implement

5. FINAL REFINED VERSION:
   - Improved version incorporating your suggestions
   - Maintain the core message while enhancing quality
   - Ensure platform-appropriate formatting

Focus on providing constructive, specific feedback that will help create high-quality technical content that resonates with {target_audience}."""
        
        return prompt
    
    def _parse_review_response(self, response: str, draft: ContentDraft) -> ReviewedContent:
        """Parse the review response into structured data"""
        
        lines = response.split('\n')
        quality_score = 5.0  # Default score
        feedback = []
        improvements = []
        final_content = draft.content  # Default to original content
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if line.upper().startswith('QUALITY SCORE') or line.upper().startswith('SCORE'):
                current_section = 'score'
            elif line.upper().startswith('STRENGTHS'):
                current_section = 'feedback'
            elif line.upper().startswith('AREAS FOR IMPROVEMENT') or line.upper().startswith('IMPROVEMENT'):
                current_section = 'improvements'
            elif line.upper().startswith('FINAL REFINED') or line.upper().startswith('FINAL VERSION'):
                current_section = 'final_content'
            elif line.upper().startswith('SPECIFIC SUGGESTIONS'):
                current_section = 'improvements'
            
            # Extract content based on current section
            elif current_section == 'score':
                # Look for numeric score
                import re
                numbers = re.findall(r'\b(\d+(\.\d+)?)\b', line)
                if numbers:
                    try:
                        score = float(numbers[0][0])
                        if 1 <= score <= 10:
                            quality_score = score
                    except ValueError:
                        pass
            
            elif current_section == 'feedback' and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                feedback.append(line.lstrip('-•* ').strip())
            
            elif current_section == 'improvements' and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                improvements.append(line.lstrip('-•* ').strip())
            
            elif current_section == 'final_content':
                # Collect all lines for final content
                if line and not line.upper().startswith('FINAL'):
                    final_content += '\n' + line
        
        # Determine approval based on quality score
        approved = quality_score >= 7.0
        
        return ReviewedContent(
            draft=draft,
            quality_score=quality_score,
            feedback=feedback,
            improvements=improvements,
            final_content=final_content.strip(),
            approved=approved
        )
