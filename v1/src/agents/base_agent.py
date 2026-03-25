from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.core.config import settings
from src.core.models import AgentResult, AgentType

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Base class for all content generation agents"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.default_llm_model
        self.llm = self._initialize_llm()
        self.agent_type = self._get_agent_type()
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model"""
        return ChatOpenAI(
            model=self.model_name,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base=settings.openrouter_base_url,
            temperature=0.7,
            max_tokens=4000
        )
    
    @abstractmethod
    def _get_agent_type(self) -> AgentType:
        """Return the agent type"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input and return results"""
        pass
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM"""
        try:
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent's main task"""
        start_time = time.time()
        
        try:
            logger.info(f"Executing {self.agent_type} agent", input_data=input_data)
            
            # Process the input
            result_data = self.process_input(input_data)
            
            processing_time = time.time() - start_time
            
            logger.info(f"{self.agent_type} agent completed successfully", 
                       processing_time=processing_time)
            
            return AgentResult(
                agent_type=self.agent_type,
                success=True,
                data=result_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Error in {self.agent_type} agent: {str(e)}"
            
            logger.error(error_message, processing_time=processing_time)
            
            return AgentResult(
                agent_type=self.agent_type,
                success=False,
                error_message=error_message,
                processing_time=processing_time
            )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate the input data"""
        required_fields = self.get_required_fields()
        
        for field in required_fields:
            if field not in input_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    @abstractmethod
    def get_required_fields(self) -> list:
        """Return list of required input fields"""
        pass
