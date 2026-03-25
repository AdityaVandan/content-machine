# Data Flow Documentation

## Content Creation Data Flow

### 1. Input Processing Flow

```
User Request (Web UI/API)
        │
        ▼
ContentInput Model Validation
        │
        ▼
Platform Enum Conversion
        │
        ▼
ContentType Enum Conversion
        │
        ▼
Pipeline Initialization
```

**Input Data Structure:**
```python
ContentInput {
    topic: str                    # Main topic
    keywords: List[str]          # Research keywords
    target_platforms: List[Platform]  # Target platforms
    content_type: ContentType     # Content format
    additional_context: str       # Optional context
    tone: str                    # Content tone
    target_audience: str         # Target audience
}
```

### 2. Research Phase Data Flow

```
ContentInput
        │
        ▼
Researcher Agent Input Mapping
        │
        ▼
OpenRouter LLM Request
        │
        ▼
Research Generation
        │
        ▼
AgentResult {
    agent_type: RESEARCHER
    success: bool
    data: ResearchData
    processing_time: float
}
```

**Research Agent Input:**
```python
{
    "topic": input_data.topic,
    "keywords": input_data.keywords,
    "target_audience": input_data.target_audience,
    "tone": input_data.tone
}
```

**Research Data Output:**
```python
ResearchData {
    topic: str
    key_points: List[str]
    statistics: List[Dict]
    references: List[str]
    trends: List[str]
    competitor_insights: List[str]
    created_at: datetime
}
```

### 3. Draft Creation Flow

```
ResearchData + ContentInput
        │
        ▼
Editor Agent Input Mapping
        │
        ▼
Platform-Specific Draft Generation
        │
        ▼
Multiple ContentDraft Objects
        │
        ▼
AgentResult {
    agent_type: EDITOR
    success: bool
    data: { "drafts": List[ContentDraft] }
    processing_time: float
}
```

**Editor Agent Input:**
```python
{
    "research_data": research_data.research_data,
    "topic": input_data.topic,
    "target_platforms": input_data.target_platforms,
    "content_type": input_data.content_type,
    "tone": input_data.tone,
    "target_audience": input_data.target_audience
}
```

**ContentDraft Structure:**
```python
ContentDraft {
    title: Optional[str]
    content: str
    platform: Platform
    content_type: ContentType
    hashtags: List[str]
    mentions: List[str]
    word_count: int
    character_count: int
    created_at: datetime
}
```

### 4. Review Phase Flow

```
ContentDraft (per platform)
        │
        ▼
Reviewer Agent Input Mapping
        │
        ▼
Quality Assessment & Improvement
        │
        ▼
ReviewedContent Object
        │
        ▼
AgentResult {
    agent_type: REVIEWER
    success: bool
    data: { "reviewed_content": ReviewedContent }
    processing_time: float
}
```

**Reviewer Agent Input:**
```python
{
    "draft": draft_data,
    "topic": input_data.topic,
    "target_audience": input_data.target_audience,
    "tone": input_data.tone
}
```

**ReviewedContent Structure:**
```python
ReviewedContent {
    draft: ContentDraft
    quality_score: float (0-10)
    feedback: List[str]
    improvements: List[str]
    final_content: str
    approved: bool
    created_at: datetime
}
```

### 5. Content Assembly Flow

```
ContentInput + ResearchData + ContentDraft + ReviewedContent
        │
        ▼
ContentPiece Assembly
        │
        ▼
Status Assignment (HUMAN_REVIEW or APPROVED)
        │
        ▼
Database Storage (Future)
        │
        ▼
Response Generation
```

**ContentPiece Structure:**
```python
ContentPiece {
    id: str
    input_data: ContentInput
    research_data: ResearchData
    draft: ContentDraft
    reviewed_content: ReviewedContent
    status: ContentStatus
    platform: Platform
    published_url: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
}
```

## Human Review Flow

### Review Request Data Flow

```
ContentPiece (HUMAN_REVIEW status)
        │
        ▼
Review Notification Task (Celery)
        │
        ▼
Email/Notification System
        │
        ▼
Reviewer Action (Web UI)
```

### Review Submission Flow

```
HumanReview Request
        │
        ▼
Validation
        │
        ▼
ContentPiece Status Update
        │
        ▼
Database Update
        │
        ▼
Scheduling Trigger (if approved)
```

**HumanReview Structure:**
```python
HumanReview {
    content_piece_id: str
    reviewer_notes: Optional[str]
    approved: bool
    modifications: Optional[str]
    reviewed_at: datetime
}
```

## Publishing Flow

### Immediate Publishing Flow

```
ContentPiece (APPROVED status)
        │
        ▼
Platform Integration Selection
        │
        ▼
Authentication Check
        │
        ▼
Content Validation
        │
        ▼
Platform-Specific Formatting
        │
        ▼
API Request to Platform
        │
        ▼
Response Processing
        │
        ▼
ContentPiece Update (PUBLISHED)
```

### Scheduled Publishing Flow

```
ContentPiece (APPROVED status)
        │
        ▼
ScheduledPost Creation
        │
        ▼
Celery Task Scheduling
        │
        ▼
Periodic Task Execution (Beat)
        │
        ▼
Publishing Flow Execution
```

**ScheduledPost Structure:**
```python
ScheduledPost {
    content_piece_id: str
    platform: Platform
    scheduled_time: datetime
    status: str
    created_at: datetime
}
```

## API Data Flow

### Content Creation API Flow

```
POST /content/create
        │
        ▼
Request Validation (Pydantic)
        │
        ▼
Platform/Content Type Conversion
        │
        ▼
ContentInput Creation
        │
        ▼
Pipeline Execution (Sync/Async)
        │
        ▼
Response Generation
```

**Request/Response Flow:**
```python
# Request
ContentRequest {
    topic: str
    keywords: List[str]
    target_platforms: List[str]
    content_type: str
    additional_context: Optional[str]
    tone: Optional[str]
    target_audience: Optional[str]
    scheduled_time: Optional[datetime]
}

# Response
{
    "success": bool,
    "content_pieces": List[ContentPiece],
    "created_at": str,
    "task_id": Optional[str]  # For async operations
}
```

### Task Status Flow

```
GET /tasks/{task_id}
        │
        ▼
Task ID Validation
        │
        ▼
Celery Result Retrieval
        │
        ▼
Status Mapping
        │
        ▼
Response Generation
```

## Error Handling Flow

### Agent Execution Errors

```
Agent Execution
        │
        ▼
Exception Catch
        │
        ▼
Error Logging
        │
        ▼
Retry Logic (if applicable)
        │
        ▼
AgentResult (success=False)
        │
        ▼
Pipeline Error Handling
```

### Platform API Errors

```
Platform API Request
        │
        ▼
HTTP Error Catch
        │
        ▼
Error Classification
        │
        ▼
Retry Logic (Rate Limit/Transient)
        │
        ▼
Failure Response
```

## State Transitions

### Content Status Flow

```
PENDING
    │
    ▼
RESEARCHING (Research Agent Start)
    │
    ▼
EDITING (Editor Agent Start)
    │
    ▼
REVIEWING (Reviewer Agent Start)
    │
    ▼
HUMAN_REVIEW (if human_review_required)
    │   ├─► APPROVED (Human approval)
    │   └─► FAILED (Human rejection)
    │
    ▼
APPROVED (Auto-approval if no human review)
    │
    ▼
PUBLISHED (Successful publishing)
    │
    ▼
FAILED (Any stage failure)
```

## Data Persistence Flow

### Current State (In-Memory)

```
Content Creation → Memory Storage → Response
```

### Future Database Integration

```
Content Creation
        │
        ▼
Database Transaction Start
        │
        ▼
ContentPiece Insert
        │
        ▼
ResearchData Insert
        │
        ▼
ContentDraft Insert
        │
        ▼
ReviewedContent Insert
        │
        ▼
Transaction Commit
        │
        ▼
Response Generation
```

## Monitoring Data Flow

### Logging Flow

```
Component Action
        │
        ▼
Structured Log Entry
        │
        ▼
Log Aggregation
        │
        ▼
Monitoring Dashboard
```

### Metrics Flow

```
Agent Execution
        │
        ▼
Performance Metrics Collection
        │
        ▼
Time Series Database
        │
        ▼
Visualization/Alerting
```

## Security Data Flow

### Credential Management

```
Environment Variables
        │
        ▼
Configuration Loading
        │
        ▼
Secure Storage (Runtime)
        │
        ▼
API Request Signing
```

### Input Sanitization

```
User Input
        │
        ▼
Validation (Pydantic)
        │
        ▼
Sanitization
        │
        ▼
Processing
```
