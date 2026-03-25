# Development Guide

## Overview

This guide covers development practices, coding standards, and contribution guidelines for the Content Machine project.

## Development Environment Setup

### Prerequisites

- **Python**: 3.11+
- **Git**: Latest version
- **IDE**: VS Code, PyCharm, or similar
- **Redis**: 6.0+ (for local development)
- **Docker**: 20.10+ (optional but recommended)

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd content-machine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys and settings

# Install pre-commit hooks
pre-commit install

# Initialize database
python -c "from src.core.database import create_tables; create_tables()"
```

### Development Dependencies

Create `requirements-dev.txt`:

```txt
# Testing
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
pytest-mock==3.11.1

# Code quality
black==23.7.0
isort==5.12.0
flake8==6.0.0
mypy==1.5.0
bandit==1.7.5

# Development tools
pre-commit==3.3.3
ipython==8.14.0
jupyter==1.0.0

# Documentation
mkdocs==1.5.0
mkdocs-material==9.1.21
```

## Project Structure

```
content-machine/
├── src/
│   ├── agents/              # AI agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py    # Base agent class
│   │   ├── researcher.py    # Research agent
│   │   ├── editor.py        # Editor agent
│   │   └── reviewer.py      # Reviewer agent
│   ├── core/                # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database operations
│   │   ├── models.py        # Data models
│   │   └── pipeline.py      # Main pipeline orchestration
│   ├── platforms/           # Platform integrations
│   │   ├── __init__.py
│   │   ├── base_platform.py # Base platform class
│   │   ├── twitter.py       # Twitter/X integration
│   │   ├── linkedin.py      # LinkedIn integration
│   │   └── medium.py        # Medium integration
│   ├── scheduler/           # Task scheduling
│   │   ├── __init__.py
│   │   ├── publisher.py     # Publishing logic
│   │   └── tasks.py         # Celery tasks
│   └── __init__.py
├── web/                     # Web interface
│   ├── api/                 # FastAPI application
│   │   ├── __init__.py
│   │   └── main.py          # API endpoints
│   └── frontend/            # Frontend assets
│       ├── index.html
│       ├── css/
│       ├── js/
│       └── assets/
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── doc/                     # Documentation
├── scripts/                 # Utility scripts
├── .github/                 # GitHub workflows
├── requirements.txt          # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Project configuration
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks
└── README.md               # Project README
```

## Coding Standards

### Python Code Style

We follow PEP 8 with additional conventions:

```python
# Imports: standard library, third-party, local
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.core.models import ContentPiece, ContentStatus
from src.agents.base_agent import BaseAgent

# Constants: UPPER_CASE
MAX_CONTENT_LENGTH = 280
DEFAULT_RETRY_COUNT = 3

# Class names: PascalCase
class ContentPipeline:
    """Main orchestrator for the content creation pipeline."""
    
    def __init__(self) -> None:
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = structlog.get_logger()
    
    def create_content(self, input_data: ContentInput) -> List[ContentPiece]:
        """Create content for all specified platforms.
        
        Args:
            input_data: User input data for content creation
            
        Returns:
            List of created content pieces
            
        Raises:
            ValueError: If input data is invalid
            PipelineError: If pipeline execution fails
        """
        # Implementation
        pass

# Function names: snake_case
def validate_platform_input(platforms: List[str]) -> bool:
    """Validate platform input strings."""
    # Implementation
    pass

# Variable names: snake_case
content_pieces = []
processing_time = 0.0
```

### Type Hints

All functions should have proper type hints:

```python
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

def process_content(
    content: str,
    platform: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, bool]]:
    """Process content for specific platform."""
    # Implementation
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def create_content_piece(
    topic: str,
    platform: str,
    content_type: str,
    tone: str = "professional"
) -> ContentPiece:
    """Create a new content piece.
    
    This function orchestrates the content creation pipeline including
    research, drafting, and review phases.
    
    Args:
        topic: Main topic for the content
        platform: Target platform (twitter, linkedin, medium)
        content_type: Type of content to create
        tone: Content tone (professional, casual, etc.)
        
    Returns:
        ContentPiece: The created content piece with all metadata
        
    Raises:
        ValueError: If platform or content_type is invalid
        PipelineError: If any agent in the pipeline fails
        
    Example:
        >>> piece = create_content_piece(
        ...     "AI in Software Development",
        ...     "linkedin",
        ...     "blog",
        ...     "professional"
        ... )
        >>> print(piece.status)
        'human_review'
    """
    # Implementation
    pass
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_agents.py
│   ├── test_platforms.py
│   ├── test_pipeline.py
│   └── test_models.py
├── integration/            # Integration tests
│   ├── test_api.py
│   ├── test_scheduler.py
│   └── test_database.py
├── e2e/                   # End-to-end tests
│   ├── test_content_flow.py
│   └── test_publishing.py
├── fixtures/              # Test data
│   ├── sample_inputs.json
│   └── mock_responses.json
└── conftest.py           # Pytest configuration
```

### Unit Testing

```python
# tests/unit/test_agents.py
import pytest
from unittest.mock import Mock, patch
from src.agents.researcher import ResearcherAgent
from src.core.models import AgentResult, AgentType

class TestResearcherAgent:
    """Test cases for ResearcherAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = ResearcherAgent()
    
    def test_get_agent_type(self):
        """Test agent type identification."""
        assert self.agent._get_agent_type() == AgentType.RESEARCHER
    
    def test_get_required_fields(self):
        """Test required fields validation."""
        required_fields = self.agent.get_required_fields()
        expected = ["topic", "keywords", "target_audience", "tone"]
        assert required_fields == expected
    
    @patch('src.agents.base_agent.ChatOpenAI')
    def test_process_input_success(self, mock_llm):
        """Test successful input processing."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '{"research_data": {"key_points": ["AI", "ML"]}}'
        mock_llm.return_value.invoke.return_value = mock_response
        
        input_data = {
            "topic": "AI in Software",
            "keywords": ["AI", "software"],
            "target_audience": "developers",
            "tone": "professional"
        }
        
        result = self.agent.process_input(input_data)
        
        assert "research_data" in result
        assert isinstance(result, dict)
    
    def test_validate_input_missing_field(self):
        """Test input validation with missing fields."""
        invalid_input = {"topic": "AI"}  # Missing required fields
        
        assert not self.agent.validate_input(invalid_input)
```

### Integration Testing

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from web.api.main import app

class TestContentAPI:
    """Integration tests for content API."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_create_content_success(self):
        """Test successful content creation."""
        request_data = {
            "topic": "Microservices Architecture",
            "keywords": ["microservices", "architecture"],
            "target_platforms": ["twitter"],
            "content_type": "blog"
        }
        
        response = self.client.post("/content/create", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "content_pieces" in data
    
    def test_create_content_invalid_platform(self):
        """Test content creation with invalid platform."""
        request_data = {
            "topic": "Test Topic",
            "target_platforms": ["invalid_platform"],
            "content_type": "blog"
        }
        
        response = self.client.post("/content/create", json=request_data)
        
        assert response.status_code == 400
        assert "Invalid platform" in response.json()["detail"]
```

### Test Configuration

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from src.core.database import create_tables
from src.agents.researcher import ResearcherAgent
from src.agents.editor import EditorAgent
from src.agents.reviewer import ReviewerAgent

@pytest.fixture(scope="session")
def setup_database():
    """Set up test database."""
    create_tables()
    yield
    # Cleanup if needed

@pytest.fixture
def mock_researcher_agent():
    """Mock researcher agent for testing."""
    agent = Mock(spec=ResearcherAgent)
    agent.execute.return_value = Mock(
        success=True,
        data={"research_data": {"key_points": ["Test point"]}},
        processing_time=1.0
    )
    return agent

@pytest.fixture
def sample_content_input():
    """Sample content input for testing."""
    return {
        "topic": "Test Topic",
        "keywords": ["test", "topic"],
        "target_platforms": ["twitter"],
        "content_type": "blog",
        "tone": "professional",
        "target_audience": "developers"
    }
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_agents.py::TestResearcherAgent::test_get_agent_type
```

## Development Workflow

### Git Workflow

We use GitHub Flow:

1. **Main Branch**: Production-ready code
2. **Feature Branches**: `feature/feature-name`
3. **Pull Requests**: Code review before merging

### Branch Naming Conventions

```bash
feature/add-new-platform
feature/improve-content-quality
bugfix/fix-twitter-integration
hotfix/critical-security-patch
refactor/optimize-pipeline-performance
docs/update-api-documentation
```

### Commit Message Format

Follow Conventional Commits:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```bash
feat(agents): add sentiment analysis capability
fix(platforms): resolve Twitter API authentication issue
docs(api): update endpoint documentation
refactor(pipeline): optimize content processing performance
test(integration): add end-to-end content creation tests
```

### Pre-commit Hooks

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Adding New Features

### Adding a New Agent

1. **Create Agent Class**:

```python
# src/agents/sentiment_analyzer.py
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.core.models import AgentType, AgentResult

class SentimentAnalyzerAgent(BaseAgent):
    """Agent for analyzing content sentiment."""
    
    def _get_agent_type(self) -> AgentType:
        return AgentType.SENTIMENT_ANALYZER
    
    def get_system_prompt(self) -> str:
        return """You are a sentiment analysis expert. Analyze the given content
        and provide sentiment scores and insights."""
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of the given content."""
        prompt = f"""
        Analyze the sentiment of this content:
        {input_data.get('content', '')}
        
        Provide:
        - Overall sentiment (positive, negative, neutral)
        - Confidence score (0-1)
        - Key emotional indicators
        """
        
        response = self.generate_response(
            prompt, 
            self.get_system_prompt()
        )
        
        return {"sentiment_analysis": response}
    
    def get_required_fields(self) -> list:
        return ["content"]
```

2. **Update Agent Registry**:

```python
# src/agents/__init__.py
from .base_agent import BaseAgent
from .researcher import ResearcherAgent
from .editor import EditorAgent
from .reviewer import ReviewerAgent
from .sentiment_analyzer import SentimentAnalyzerAgent

__all__ = [
    "BaseAgent",
    "ResearcherAgent", 
    "EditorAgent",
    "ReviewerAgent",
    "SentimentAnalyzerAgent"
]
```

3. **Update Models**:

```python
# src/core/models.py
class AgentType(str, Enum):
    RESEARCHER = "researcher"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    SENTIMENT_ANALYZER = "sentiment_analyzer"  # Add new type
```

4. **Add Tests**:

```python
# tests/unit/test_sentiment_analyzer.py
import pytest
from src.agents.sentiment_analyzer import SentimentAnalyzerAgent

class TestSentimentAnalyzerAgent:
    def setup_method(self):
        self.agent = SentimentAnalyzerAgent()
    
    def test_get_agent_type(self):
        assert self.agent._get_agent_type() == "sentiment_analyzer"
    
    def test_process_input(self):
        input_data = {"content": "This is amazing!"}
        result = self.agent.process_input(input_data)
        
        assert "sentiment_analysis" in result
```

### Adding a New Platform

1. **Create Platform Integration**:

```python
# src/platforms/instagram.py
from typing import Dict, Any
from src.platforms.base_platform import BasePlatformIntegration
from src.core.models import Platform, ReviewedContent

class InstagramIntegration(BasePlatformIntegration):
    """Instagram platform integration."""
    
    def __init__(self):
        super().__init__(Platform.INSTAGRAM)
    
    def authenticate(self) -> bool:
        """Authenticate with Instagram API."""
        # Implementation
        return True
    
    def publish_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Publish content to Instagram."""
        # Implementation
        return {"success": True, "post_id": "instagram_post_123"}
    
    def validate_content(self, content: ReviewedContent) -> Dict[str, Any]:
        """Validate content for Instagram."""
        errors = []
        
        if len(content.final_content) > 2200:
            errors.append("Content exceeds Instagram caption limit")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get analytics for Instagram post."""
        # Implementation
        return {"likes": 100, "comments": 25}
```

2. **Update Platform Registry**:

```python
# src/platforms/__init__.py
from .base_platform import BasePlatformIntegration
from .twitter import TwitterIntegration
from .linkedin import LinkedInIntegration
from .medium import MediumIntegration
from .instagram import InstagramIntegration

__all__ = [
    "BasePlatformIntegration",
    "TwitterIntegration",
    "LinkedInIntegration", 
    "MediumIntegration",
    "InstagramIntegration"
]
```

3. **Update Platform Enum**:

```python
# src/core/config.py
class Platform(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    MEDIUM = "medium"
    INSTAGRAM = "instagram"  # Add new platform
```

## Debugging

### Logging Configuration

```python
# src/core/logging.py
import structlog
import logging
import sys

def setup_logging(log_level: str = "INFO"):
    """Configure structured logging."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

### Debug Mode

```python
# src/core/config.py
import os
from typing import Optional

class Settings:
    def __init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        if self.debug:
            self.log_level = "DEBUG"
```

### Common Debugging Techniques

1. **Logging Agent Execution**:

```python
def execute(self, input_data: Dict[str, Any]) -> AgentResult:
    self.logger.info("Starting agent execution", 
                    agent_type=self.agent_type,
                    input_keys=list(input_data.keys()))
    
    try:
        result = self.process_input(input_data)
        self.logger.info("Agent execution successful",
                        result_keys=list(result.keys()))
        return AgentResult(success=True, data=result)
    except Exception as e:
        self.logger.error("Agent execution failed",
                         error=str(e),
                         exc_info=True)
        return AgentResult(success=False, error_message=str(e))
```

2. **Pipeline State Debugging**:

```python
def create_content(self, input_data: ContentInput) -> List[ContentPiece]:
    self.logger.info("Starting content creation",
                    topic=input_data.topic,
                    platforms=[p.value for p in input_data.target_platforms])
    
    # Debug each stage
    research_result = self._execute_research(input_data)
    self.logger.debug("Research completed",
                     success=research_result.success,
                     processing_time=research_result.processing_time)
    
    # Continue with other stages...
```

## Performance Optimization

### Profiling

```python
# scripts/profile_pipeline.py
import cProfile
import pstats
from src.core.pipeline import ContentPipeline
from src.core.models import ContentInput, Platform, ContentType

def profile_content_creation():
    """Profile the content creation pipeline."""
    profiler = cProfile.Profile()
    
    input_data = ContentInput(
        topic="AI in Software Development",
        target_platforms=[Platform.TWITTER],
        content_type=ContentType.BLOG
    )
    
    profiler.enable()
    pipeline = ContentPipeline()
    result = pipeline.create_content(input_data)
    profiler.disable()
    
    # Save stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

if __name__ == "__main__":
    profile_content_creation()
```

### Memory Optimization

```python
# Use generators for large datasets
def process_large_content_batch(content_inputs: List[ContentInput]) -> Iterator[ContentPiece]:
    """Process content in batches to optimize memory usage."""
    for input_data in content_inputs:
        yield from create_content(input_data)

# Clear large objects when done
def cleanup_resources():
    """Clean up resources to free memory."""
    import gc
    gc.collect()
```

## Documentation

### Code Documentation

- All public functions must have docstrings
- Complex algorithms should have inline comments
- Use type hints for better IDE support

### API Documentation

API documentation is auto-generated from FastAPI:
- Access at `/docs` (Swagger UI)
- Access at `/redoc` (ReDoc)

### Updating Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

This development guide provides comprehensive guidelines for contributing to the Content Machine project effectively.
