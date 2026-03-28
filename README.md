# Content Machine

An AI-powered pipeline that turns raw learnings into polished, platform-ready social media content.

Two versions exist in this repo, each with a different scope and complexity tradeoff.

## Versions

### [v2/](v2/) — Lightweight CLI pipeline *(active)*

A minimal, file-based 3-layer agent system. Write your notes in `input.md`, run three scripts, publish via Buffer.

- **Entry point:** edit `v2/input.md`, then run `01_generate.py` → `02_review.py` → `03_upload.py`
- **Infrastructure:** none — just Python + OpenRouter + Buffer API
- **Best for:** personal use, quick iteration, learning the agent pattern

→ See [v2/README.md](v2/README.md) for full setup and usage.

---

### [v1/](v1/) — Full-stack multi-agent system *(legacy)*

A production-grade system with a FastAPI web UI, Celery task scheduler, Redis, and native integrations for Twitter, LinkedIn, and Medium.

- **Entry point:** `docker compose up` then visit `localhost:8000`
- **Infrastructure:** Docker Compose (Redis, Celery worker + beat, Flower)
- **Best for:** teams, scheduled publishing, extensible agent architecture

→ See [v1/README.md](v1/README.md) for full setup and usage.

---

## Comparison

| | v1 | v2 |
|--|----|----|
| Interface | Web UI + REST API | CLI scripts |
| Scheduling | Celery + Redis | Manual / cron |
| Publishing | Twitter, LinkedIn, Medium (native APIs) | Buffer API |
| Review workflow | Human review checkpoint in UI | AI reviewer agent + file inspection |
| Setup | Docker Compose | `pip install -r requirements.txt` |
| State | Database (SQLAlchemy) | Markdown files |

## LLM Provider

Both versions use [OpenRouter](https://openrouter.ai/) as the LLM gateway, defaulting to `anthropic/claude-opus-4-5`. This can be changed via the `OPENROUTER_MODEL` env var.

## License

MIT
