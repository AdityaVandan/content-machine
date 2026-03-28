# Content Machine v2

A lightweight, file-based CLI pipeline that turns your raw learnings into polished social media content using a 3-layer AI agent system.

## How it works

```
input.md  →  01_generate.py  →  drafts/  →  02_review.py  →  reviewed/  →  03_upload.py  →  Buffer
```

Each script is a discrete, resumable step. You can stop between any two layers to manually inspect or edit the output.

## Architecture

### Agents

| Layer | Script | Agent | Role |
|-------|--------|-------|------|
| 1 | `01_generate.py` | `generator_agent` | Raw learnings → platform-specific drafts |
| 2 | `02_review.py` | `reviewer_agent` | Drafts → refined content + quality score (1–10) |
| 3 | `03_upload.py` | `uploader_agent` | Reviewed content → Buffer API (no LLM) |

### File layout

```
v2/
├── agents/
│   ├── generator_agent.py   # Layer 1: content generation
│   ├── reviewer_agent.py    # Layer 2: editing + scoring
│   └── uploader_agent.py    # Layer 3: formatting + Buffer upload
├── core/
│   ├── config.py            # Pydantic settings (OpenRouter, Buffer)
│   ├── llm.py               # LangChain wrapper for OpenRouter
│   └── file_io.py           # Frontmatter-based markdown I/O
├── scripts/
│   ├── 01_generate.py
│   ├── 02_review.py
│   └── 03_upload.py
├── drafts/                  # Auto-generated, git-ignored
├── reviewed/                # Auto-generated, git-ignored
└── input.md                 # Your entry point
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENROUTER_API_KEY=your_key_here          # required — https://openrouter.ai/
OPENROUTER_MODEL=anthropic/claude-opus-4-5  # optional, this is the default

BUFFER_ACCESS_TOKEN=your_token_here       # required for upload step
BUFFER_TWITTER_PROFILE_ID=               # optional
BUFFER_LINKEDIN_PROFILE_ID=              # optional
```

## Usage

### Step 1 — Fill in `input.md`

```markdown
---
topic: "What I learned about Python async this week"
target_audience: "mid-level Python developers"
tone: "conversational but technical"
platforms:
  - twitter_thread
  - linkedin_post
---

Your raw notes and learnings go here...
```

### Step 2 — Generate drafts

```bash
python scripts/01_generate.py
```

Outputs one file per platform to `drafts/`, e.g. `drafts/twitter_thread_python-async.md`.

### Step 3 — Review and refine

```bash
python scripts/02_review.py
```

Runs each draft through the reviewer agent. Outputs to `reviewed/` with reviewer notes, a quality score (1–10), and refined content.

### Step 4 — Upload to Buffer

```bash
# Preview without posting
python scripts/03_upload.py --dry-run

# Actually post
python scripts/03_upload.py
```

## Platforms

| Platform | Format | Notes |
|----------|--------|-------|
| `twitter_thread` | 5–8 tweets, ≤280 chars each | Parsed from `## Tweet N` sections |
| `linkedin_post` | 150–800 words | Extracted from `## Content` section |

## Output format

After generation, each draft contains YAML frontmatter with metadata:

```yaml
---
topic: ...
platform: twitter_thread
status: draft
generated_at: 2024-01-15T10:30:00
---
```

After review, the reviewed file adds:

```
## Reviewer Notes
- ...

## Quality Score
8

## Refined Content
...
```

## Dependencies

- `langchain-openai` / `langchain-core` — LLM calls via OpenRouter
- `python-frontmatter` — Markdown + YAML parsing
- `pydantic` / `pydantic-settings` — Config validation
- `requests` — Buffer API calls
