from typing import Dict, Any, List
import structlog
from src.agents.base_agent import BaseAgent
from src.core.models import AgentType, ResearchData, ContentInput

logger = structlog.get_logger()


class ResearcherAgent(BaseAgent):
    """Agent responsible for researching topics and gathering relevant information"""
    
    def _get_agent_type(self) -> AgentType:
        return AgentType.RESEARCHER
    
    def get_system_prompt(self) -> str:
        return """You are a skilled technology researcher specializing in software engineering, fullstack development, and tech business topics.

Your task is to conduct comprehensive research on given topics and provide:
1. Key technical points and concepts
2. Relevant statistics and data points
3. Current industry trends
4. Competitor insights and market analysis
5. Authoritative references and sources

Focus on:
- Technical accuracy and depth
- Current industry standards and best practices
- Emerging trends and innovations
- Business implications and market context
- Actionable insights for tech professionals

Provide research in a structured, well-organized format that can be easily used by content creators. Be thorough but concise, focusing on the most valuable and relevant information."""
    
    def get_required_fields(self) -> list:
        return ["topic", "keywords", "target_audience", "tone"]
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input and generate research data"""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")
        
        topic = input_data["topic"]
        keywords = input_data.get("keywords", [])
        target_audience = input_data.get("target_audience", "tech professionals")
        tone = input_data.get("tone", "professional")
        
        # Create research prompt
        research_prompt = self._create_research_prompt(
            topic, keywords, target_audience, tone
        )
        
        # Generate research response
        research_response = self.generate_response(
            research_prompt, 
            self.get_system_prompt()
        )
        
        # Parse and structure the research data
        research_data = self._parse_research_response(
            research_response, topic
        )
        
        return {
            "research_data": research_data.dict(),
            "topic": topic,
            "research_summary": research_response
        }
    
    def _create_research_prompt(self, topic: str, keywords: List[str], 
                              target_audience: str, tone: str) -> str:
        """Create a comprehensive research prompt"""
        keywords_str = ", ".join(keywords) if keywords else "N/A"
        
        prompt = f"""Please conduct comprehensive research on the following topic:

TOPIC: {topic}

KEYWORDS: {keywords_str}

TARGET AUDIENCE: {target_audience}

TONE: {tone}

Please provide research covering:

1. KEY POINTS:
   - Main technical concepts and principles
   - Important subtopics and related areas
   - Critical considerations and challenges

2. STATISTICS & DATA:
   - Relevant industry statistics
   - Performance metrics or benchmarks
   - Market data or adoption rates
   - User behavior insights

3. CURRENT TRENDS:
   - Emerging technologies or approaches
   - Industry shifts and developments
   - Future predictions and outlook

4. COMPETITOR INSIGHTS:
   - Major players and solutions
   - Market positioning and strategies
   - Strengths and weaknesses analysis

5. REFERENCES:
   - Authoritative sources and documentation
   - Industry reports and studies
   - Expert opinions and thought leadership

Focus on providing actionable, current information that would be valuable for creating engaging tech content. Include specific data points, examples, and insights that can make the content more credible and informative."""
        
        return prompt
    
    def _parse_research_response(self, response: str, topic: str) -> ResearchData:
        """Parse the research response into structured data"""
        # This is a simplified parsing approach
        # In a production system, you might want more sophisticated parsing
        
        lines = response.split('\n')
        key_points = []
        statistics = []
        references = []
        trends = []
        competitor_insights = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if line.upper().startswith('KEY POINTS'):
                current_section = 'key_points'
            elif line.upper().startswith('STATISTICS') or line.upper().startswith('DATA'):
                current_section = 'statistics'
            elif line.upper().startswith('TRENDS'):
                current_section = 'trends'
            elif line.upper().startswith('COMPETITOR'):
                current_section = 'competitor_insights'
            elif line.upper().startswith('REFERENCES'):
                current_section = 'references'
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                # Extract bullet points
                content = line.lstrip('-•* ').strip()
                if current_section == 'key_points':
                    key_points.append(content)
                elif current_section == 'statistics':
                    statistics.append({"data": content})
                elif current_section == 'trends':
                    trends.append(content)
                elif current_section == 'competitor_insights':
                    competitor_insights.append(content)
                elif current_section == 'references':
                    references.append(content)
        
        return ResearchData(
            topic=topic,
            key_points=key_points,
            statistics=statistics,
            references=references,
            trends=trends,
            competitor_insights=competitor_insights
        )
