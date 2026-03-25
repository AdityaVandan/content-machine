# Quick Setup Guide

## 🎉 Content Machine is Ready!

Your Content Machine system is successfully installed and running. Here's how to start creating content:

### ✅ What's Working
- ✅ Web server running at http://localhost:8000
- ✅ API endpoints functional
- ✅ Database initialized
- ✅ All agents and platforms configured

### 🔧 Next Steps for Full Functionality

#### 1. Get OpenRouter API Key
```bash
# Sign up at https://openrouter.ai/
# Get your API key and add it to .env:
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. Start Redis (for scheduling)
```bash
redis-server
```

#### 3. Start Celery Worker (for background tasks)
```bash
# In a new terminal
celery -A src.scheduler.tasks worker --loglevel=info
```

#### 4. Access the Web Interface
- Open http://localhost:8000/web/frontend/index.html
- Or use the API directly at http://localhost:8000/docs

### 🚀 Test Content Creation

Once you have your OpenRouter API key:

```bash
# Test via API
curl -X POST http://localhost:8000/content/create \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "5 Best Practices for API Design",
    "keywords": ["api", "design", "rest", "best-practices"],
    "target_platforms": ["twitter", "linkedin"],
    "content_type": "blog",
    "tone": "professional",
    "target_audience": "developers"
  }'
```

### 📱 Platform Integration (Optional)

To actually publish content, add platform API keys to `.env`:

```bash
# Twitter/X
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_token

# Medium
MEDIUM_INTEGRATION_TOKEN=your_token
```

### 🎯 Features Available

- **Multi-Agent Pipeline**: Research → Edit → Review
- **Platform Support**: Twitter, LinkedIn, Medium
- **Human Review**: Built-in approval workflow
- **Scheduling**: Automated publishing
- **Web Interface**: Easy content management

### 📊 Monitoring

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/status

Your Content Machine is ready to transform your tech topics into engaging content! 🎉
