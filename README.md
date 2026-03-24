# Content Machine

A LangChain-powered multi-agent content creation system that transforms your tech/software engineering inputs into platform-specific content for X, LinkedIn, and Medium with automated scheduling and human review checkpoints.

## Features

- **Multi-Agent Pipeline**: 3-layer system (Researcher → Editor → Reviewer) with extensibility for more agents
- **Platform Integration**: Native support for Twitter/X, LinkedIn, and Medium
- **OpenRouter LLM**: Access to multiple language models through OpenRouter
- **Human Review**: Built-in review checkpoint before final publishing
- **Automated Scheduling**: Celery-powered task scheduling and automation
- **Web Interface**: Modern web UI for content management and review
- **REST API**: Full API for programmatic access

## Architecture

```
User Input → Researcher → Editor → Reviewer → Human Review → Platform Formatting → Scheduling → Publication
```

### Components

1. **Core Pipeline**: Orchestrates the content creation workflow
2. **Agents**: Specialized AI agents for research, editing, and review
3. **Platform Integrations**: Native API integrations for social platforms
4. **Scheduler**: Celery-based task scheduling and automation
5. **Web Interface**: Modern UI for content management
6. **API Layer**: FastAPI-based REST API

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (for Celery)
- OpenRouter API key
- Platform API credentials (Twitter, LinkedIn, Medium)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd content-machine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Start Redis**
   ```bash
   redis-server
   ```

5. **Initialize database**
   ```python
   from src.core.database import create_tables
   create_tables()
   ```

6. **Start the application**
   ```bash
   # Start the web server
   python run.py
   
   # In another terminal, start Celery worker
   celery -A src.scheduler.tasks worker --loglevel=info
   
   # In another terminal, start Celery beat (scheduler)
   celery -A src.scheduler.tasks beat --loglevel=info
   ```

### Docker Setup

1. **Build and start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Flower (Celery Monitoring): http://localhost:5555

## Usage

### Web Interface

1. Open http://localhost:8000 in your browser
2. Fill out the content creation form:
   - **Topic**: Main topic for your content
   - **Keywords**: Relevant keywords for research
   - **Target Platforms**: Select platforms (Twitter, LinkedIn, Medium)
   - **Content Type**: Choose content format
   - **Additional Context**: Any specific requirements
3. Click "Create Content" to start the pipeline
4. Review generated content in the results section
5. Approve or modify content before publishing

### API Usage

```python
import requests

# Create content
response = requests.post("http://localhost:8000/content/create", json={
    "topic": "Microservices Architecture Best Practices",
    "keywords": ["microservices", "architecture", "scalability"],
    "target_platforms": ["twitter", "linkedin"],
    "content_type": "blog",
    "tone": "professional",
    "target_audience": "tech professionals"
})

# Get task status
task_id = response.json()["task_id"]
status = requests.get(f"http://localhost:8000/tasks/{task_id}")
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Yes |
| `TWITTER_API_KEY` | Twitter API key | For Twitter |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn access token | For LinkedIn |
| `MEDIUM_INTEGRATION_TOKEN` | Medium integration token | For Medium |
| `DATABASE_URL` | Database connection string | No |
| `REDIS_URL` | Redis connection string | No |

### Platform Setup

#### Twitter/X
1. Create a Twitter Developer account
2. Create a new app and get API credentials
3. Add credentials to `.env` file

#### LinkedIn
1. Create LinkedIn app
2. Get OAuth 2.0 access token
3. Add token to `.env` file

#### Medium
1. Get Medium integration token from settings
2. Add token to `.env` file

## Development

### Project Structure

```
content-machine/
├── src/
│   ├── agents/          # AI agents (researcher, editor, reviewer)
│   ├── platforms/       # Platform integrations
│   ├── scheduler/       # Celery tasks and scheduling
│   └── core/           # Core models and pipeline
├── web/
│   ├── api/            # FastAPI application
│   └── frontend/       # Web interface
├── tests/              # Test suite
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # Docker setup
└── README.md          # This file
```

### Adding New Agents

1. Create new agent class inheriting from `BaseAgent`
2. Implement required methods: `get_system_prompt`, `process_input`, etc.
3. Add to agents module `__init__.py`
4. Update pipeline to use new agent

### Adding New Platforms

1. Create new integration class inheriting from `BasePlatformIntegration`
2. Implement required methods: `authenticate`, `publish_content`, etc.
3. Add to platforms module `__init__.py`
4. Update platform configuration

## Monitoring

### Flower (Celery Monitoring)
- Access at http://localhost:5555
- Monitor task execution and performance
- View task history and statistics

### API Documentation
- Access at http://localhost:8000/docs
- Interactive API documentation
- Test endpoints directly

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the documentation
2. Review GitHub issues
3. Create new issue with detailed description
