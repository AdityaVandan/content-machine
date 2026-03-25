# Content Machine Architecture Overview

## System Overview

Content Machine is a LangChain-powered multi-agent content creation system that transforms technical inputs into platform-specific content for Twitter/X, LinkedIn, and Medium with automated scheduling and human review checkpoints.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   REST API      │    │   Scheduler     │
│   (Frontend)    │◄──►│   (FastAPI)     │◄──►│   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Content        │
                       │  Pipeline       │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Agent System   │
                       │  (3-Layer)      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Platform       │
                       │  Integrations   │
                       └─────────────────┘
```

## Core Components

### 1. Content Pipeline (`src/core/pipeline.py`)
The main orchestrator that manages the entire content creation workflow.

**Key Responsibilities:**
- Coordinate agent execution sequence
- Manage content state transitions
- Handle platform-specific formatting
- Orchestrate human review process
- Schedule and publish content

**Workflow:**
1. User Input → Research Phase
2. Research → Draft Creation (per platform)
3. Draft → Review Phase
4. Review → Human Review (if required)
5. Approval → Platform Formatting
6. Formatting → Publication/Scheduling

### 2. Agent System (`src/agents/`)
A three-layer AI agent system built on LangChain and OpenRouter.

#### Agent Types:
- **Researcher Agent**: Gathers information, trends, and insights
- **Editor Agent**: Creates platform-specific drafts
- **Reviewer Agent**: Quality assessment and improvement suggestions

#### Base Agent Architecture:
```python
BaseAgent
├── _initialize_llm()     # OpenRouter LLM setup
├── get_system_prompt()   # Agent-specific instructions
├── process_input()        # Core processing logic
├── execute()             # Error handling and logging
└── validate_input()      # Input validation
```

### 3. Platform Integrations (`src/platforms/`)
Native API integrations for social media platforms.

#### Supported Platforms:
- **Twitter/X**: Character-limited posts, hashtag support
- **LinkedIn**: Professional posts, longer format
- **Medium**: Article publishing with rich formatting

#### Base Platform Architecture:
```python
BasePlatformIntegration
├── authenticate()        # OAuth/API authentication
├── publish_content()     # Platform-specific publishing
├── validate_content()    # Content validation
├── get_analytics()       # Performance metrics
└── format_content()      # Platform formatting
```

### 4. Scheduler (`src/scheduler/`)
Celery-based task scheduling and automation system.

#### Key Features:
- Asynchronous content creation
- Scheduled publishing
- Retry mechanisms with exponential backoff
- Periodic maintenance tasks
- Task monitoring and cleanup

#### Task Types:
- `create_content_task`: Content generation pipeline
- `publish_content_task`: Platform publishing
- `publish_scheduled_content`: Scheduled post publishing
- `cleanup_old_tasks`: Maintenance and cleanup
- `send_review_notification`: Human review notifications

### 5. Web Interface (`web/`)
Modern web UI and REST API for content management.

#### API Layer (FastAPI):
- RESTful endpoints for all operations
- Real-time task status monitoring
- Content review and approval
- Platform management
- Health monitoring

#### Frontend:
- Content creation forms
- Review dashboard
- Task monitoring
- Analytics visualization

## Data Models

### Core Entities:
- **ContentInput**: User request data
- **ContentPiece**: Complete content with metadata
- **ResearchData**: Agent research results
- **ContentDraft**: Platform-specific drafts
- **ReviewedContent**: Quality-assessed content
- **HumanReview**: Human approval workflow
- **ScheduledPost**: Time-based publishing

### State Management:
Content flows through defined states:
`PENDING → RESEARCHING → EDITING → REVIEWING → HUMAN_REVIEW → APPROVED → PUBLISHED`

## Technology Stack

### Core Technologies:
- **Python 3.11+**: Primary language
- **LangChain**: LLM orchestration framework
- **OpenRouter**: Multi-model LLM access
- **FastAPI**: REST API framework
- **Celery**: Distributed task queue
- **Redis**: Message broker and caching
- **SQLite**: Data persistence

### External Integrations:
- **Twitter API**: X platform publishing
- **LinkedIn API**: Professional networking
- **Medium API**: Article publishing

## Configuration Management

### Environment Variables:
- `OPENROUTER_API_KEY`: LLM access
- Platform API credentials (Twitter, LinkedIn, Medium)
- Database and Redis connections
- Celery configuration

### Settings (`src/core/config.py`):
- Default LLM model selection
- Human review requirements
- Platform-specific limits
- Retry and timeout configurations

## Security Considerations

### API Security:
- CORS configuration
- Input validation and sanitization
- Rate limiting (platform-dependent)
- Secure credential storage

### Data Privacy:
- No sensitive data logging
- Encrypted credential storage
- Minimal data retention policies

## Scalability Architecture

### Horizontal Scaling:
- Celery worker scaling
- Database connection pooling
- Redis clustering for high availability
- Load balancer ready API design

### Performance Optimizations:
- Async task processing
- Connection reuse
- Efficient LLM token usage
- Caching strategies

## Monitoring and Observability

### Logging:
- Structured logging with `structlog`
- Agent execution tracking
- Performance metrics
- Error tracking and alerting

### Health Monitoring:
- API health endpoints
- Celery task monitoring (Flower)
- Database connection health
- Platform API status

## Development Workflow

### Adding New Agents:
1. Inherit from `BaseAgent`
2. Implement required abstract methods
3. Add to agents registry
4. Update pipeline configuration

### Adding New Platforms:
1. Inherit from `BasePlatformIntegration`
2. Implement platform-specific methods
3. Add to platform registry
4. Update configuration

### Testing Strategy:
- Unit tests for individual components
- Integration tests for workflows
- End-to-end API testing
- Platform integration testing

## Deployment Architecture

### Containerization:
- Docker multi-stage builds
- Docker Compose for development
- Production-ready configurations
- Environment-specific settings

### Production Considerations:
- Database migrations
- Backup strategies
- Monitoring and alerting
- Disaster recovery procedures
