# API Reference Documentation

## Overview

Content Machine provides a comprehensive REST API built with FastAPI for content creation, management, and publishing. All endpoints support JSON request/response format and include proper error handling.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production deployments, implement proper authentication mechanisms (OAuth 2.0, API keys, etc.).

## Content Type

All requests and responses use `application/json` content type.

## Core Endpoints

### 1. Root Endpoint

**GET /**

Redirects to the web interface frontend.

**Response:**
- HTML content of `web/frontend/index.html`

### 2. Health Check

**GET /health**

Returns the current health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 3. Pipeline Status

**GET /status**

Returns the current status of the content pipeline including available agents and platforms.

**Response:**
```json
{
  "agents": ["researcher", "editor", "reviewer"],
  "platforms": ["twitter", "linkedin", "medium"],
  "human_review_required": true,
  "default_llm_model": "anthropic/claude-3-sonnet"
}
```

## Content Management Endpoints

### 4. Create Content

**POST /content/create**

Creates content for specified platforms using the AI agent pipeline.

**Request Body:**
```json
{
  "topic": "Microservices Architecture Best Practices",
  "keywords": ["microservices", "architecture", "scalability"],
  "target_platforms": ["twitter", "linkedin"],
  "content_type": "blog",
  "additional_context": "Focus on modern cloud-native approaches",
  "tone": "professional",
  "target_audience": "tech professionals",
  "scheduled_time": "2024-01-01T15:00:00.000Z"
}
```

**Parameters:**
- `topic` (string, required): Main topic for content creation
- `keywords` (array of strings, optional): Keywords for research
- `target_platforms` (array of strings, required): Target platforms
- `content_type` (string, required): Type of content to create
- `additional_context` (string, optional): Additional requirements
- `tone` (string, optional): Content tone (default: "professional")
- `target_audience` (string, optional): Target audience (default: "tech professionals")
- `scheduled_time` (datetime, optional): Schedule for later creation

**Response:**
```json
{
  "success": true,
  "content_pieces": [
    {
      "id": "uuid-string",
      "input_data": {
        "topic": "Microservices Architecture Best Practices",
        "keywords": ["microservices", "architecture", "scalability"],
        "target_platforms": ["twitter", "linkedin"],
        "content_type": "blog",
        "tone": "professional",
        "target_audience": "tech professionals"
      },
      "research_data": {
        "topic": "Microservices Architecture Best Practices",
        "key_points": ["...", "..."],
        "statistics": [{"metric": "...", "value": "..."}],
        "references": ["...", "..."],
        "trends": ["...", "..."],
        "competitor_insights": ["...", "..."]
      },
      "draft": {
        "title": "Microservices Architecture Best Practices",
        "content": "...",
        "platform": "twitter",
        "content_type": "blog",
        "hashtags": ["#microservices", "#architecture"],
        "mentions": [],
        "word_count": 280,
        "character_count": 1500
      },
      "reviewed_content": {
        "quality_score": 8.5,
        "feedback": ["Good structure", "Clear explanations"],
        "improvements": ["Add more examples"],
        "final_content": "...",
        "approved": false
      },
      "status": "human_review",
      "platform": "twitter",
      "created_at": "2024-01-01T12:00:00.000Z",
      "updated_at": "2024-01-01T12:00:00.000Z"
    }
  ],
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid platform or content type
- `500 Internal Server Error`: Pipeline execution failure

### 5. Review Content

**POST /content/review**

Submits human review for content pieces.

**Request Body:**
```json
{
  "content_piece_id": "uuid-string",
  "approved": true,
  "reviewer_notes": "Great content, minor formatting adjustments needed",
  "modifications": "Added bullet points for better readability"
}
```

**Parameters:**
- `content_piece_id` (string, required): ID of content piece to review
- `approved` (boolean, required): Approval status
- `reviewer_notes` (string, optional): Reviewer feedback
- `modifications` (string, optional): Made modifications

**Response:**
```json
{
  "success": true,
  "message": "Review submitted successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid content piece ID
- `500 Internal Server Error`: Review submission failure

### 6. Publish Content

**POST /content/publish**

Publishes approved content to specified platforms.

**Request Body:**
```json
{
  "content_piece_id": "uuid-string",
  "platform": "twitter",
  "scheduled_time": "2024-01-01T15:00:00.000Z"
}
```

**Parameters:**
- `content_piece_id` (string, required): ID of content piece to publish
- `platform` (string, required): Target platform
- `scheduled_time` (datetime, optional): Schedule for later publishing

**Response:**
```json
{
  "success": true,
  "published_url": "https://twitter.com/user/status/123456789",
  "published_at": "2024-01-01T12:00:00.000Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid platform or content piece ID
- `500 Internal Server Error`: Publishing failure

## Task Management Endpoints

### 7. Get Task Status

**GET /tasks/{task_id}**

Retrieves the status of a scheduled task.

**Path Parameters:**
- `task_id` (string): Unique task identifier

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "PENDING",
  "result": null,
  "created_at": "2024-01-01T12:00:00.000Z",
  "updated_at": "2024-01-01T12:00:00.000Z"
}
```

**Task Status Values:**
- `PENDING`: Task queued but not started
- `STARTED`: Task in progress
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task failed
- `RETRY`: Task scheduled for retry

### 8. Cancel Task

**DELETE /tasks/{task_id}**

Cancels a scheduled task.

**Path Parameters:**
- `task_id` (string): Unique task identifier

**Response:**
```json
{
  "success": true,
  "message": "Task cancelled successfully"
}
```

### 9. Get Scheduled Tasks

**GET /tasks**

Retrieves a list of all scheduled tasks.

**Query Parameters:**
- `status` (string, optional): Filter by task status
- `limit` (integer, optional): Maximum number of tasks to return

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "uuid-string",
      "type": "create_content",
      "status": "PENDING",
      "scheduled_time": "2024-01-01T15:00:00.000Z",
      "created_at": "2024-01-01T12:00:00.000Z"
    }
  ],
  "total": 1
}
```

## Reference Data Endpoints

### 10. Get Platforms

**GET /platforms**

Returns available platforms and their specifications.

**Response:**
```json
{
  "platforms": [
    {
      "value": "twitter",
      "name": "Twitter/X",
      "max_length": 280
    },
    {
      "value": "linkedin",
      "name": "LinkedIn",
      "max_length": 3000
    },
    {
      "value": "medium",
      "name": "Medium",
      "min_length": 800,
      "max_length": 2000
    }
  ]
}
```

### 11. Get Content Types

**GET /content-types**

Returns available content types.

**Response:**
```json
{
  "content_types": [
    {
      "value": "blog",
      "name": "Blog Post"
    },
    {
      "value": "tweet",
      "name": "Tweet"
    },
    {
      "value": "linkedin_post",
      "name": "LinkedIn Post"
    },
    {
      "value": "medium_article",
      "name": "Medium Article"
    }
  ]
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

### Common Error Scenarios

1. **Invalid Platform**
   ```json
   {
     "detail": "Invalid platform: instagram"
   }
   ```

2. **Invalid Content Type**
   ```json
   {
     "detail": "Invalid content type: video"
   }
   ```

3. **Missing Required Fields**
   ```json
   {
     "detail": "Field required: topic"
   }
   ```

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing:
- Platform-specific rate limits
- User-based rate limiting
- Global API rate limiting

## Pagination

List endpoints support pagination via query parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Example:**
```
GET /tasks?page=2&limit=10
```

## CORS Configuration

The API is configured to accept requests from any origin with full CORS support:
- Allow origins: `*`
- Allow methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`
- Allow headers: `*`

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## WebSocket Support

Currently, WebSocket support is not implemented. Future versions may include:
- Real-time task status updates
- Live content creation progress
- Notification streaming

## SDK Examples

### Python Example

```python
import requests

# Create content
response = requests.post("http://localhost:8000/content/create", json={
    "topic": "AI in Software Development",
    "keywords": ["AI", "software", "development"],
    "target_platforms": ["twitter", "linkedin"],
    "content_type": "blog"
})

result = response.json()
print(f"Created {len(result['content_pieces'])} content pieces")
```

### JavaScript Example

```javascript
// Create content
const response = await fetch('http://localhost:8000/content/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    topic: 'Cloud Native Architecture',
    keywords: ['cloud', 'architecture', 'kubernetes'],
    target_platforms: ['medium'],
    content_type: 'medium_article'
  })
});

const result = await response.json();
console.log('Content created:', result);
```

### cURL Example

```bash
# Create content
curl -X POST "http://localhost:8000/content/create" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "DevOps Best Practices",
    "keywords": ["devops", "cicd", "automation"],
    "target_platforms": ["linkedin"],
    "content_type": "linkedin_post"
  }'
```
