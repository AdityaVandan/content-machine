import re
from pathlib import Path
from datetime import datetime, timezone

import frontmatter
import yaml

DRAFTS_DIR = Path("drafts")
REVIEWED_DIR = Path("reviewed")


def read_input_md(path: str = "input.md") -> tuple[dict, str]:
    """Parse input.md frontmatter and body. Returns (meta_dict, body_str)."""
    post = frontmatter.load(path)
    return dict(post.metadata), post.content


def make_slug(topic: str) -> str:
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:50].rstrip("-")


def write_draft(platform: str, slug: str, meta: dict, content: str) -> Path:
    DRAFTS_DIR.mkdir(exist_ok=True)
    path = DRAFTS_DIR / f"{platform}_{slug}.md"
    header = _make_header({
        "platform": platform,
        "topic": meta.get("topic", ""),
        "target_audience": meta.get("target_audience", ""),
        "generated_at": _now(),
        "status": "draft",
    })
    path.write_text(header + content)
    return path


def list_drafts() -> list[Path]:
    return sorted(DRAFTS_DIR.glob("*.md"))


def read_draft(path: Path) -> tuple[dict, str]:
    post = frontmatter.load(str(path))
    return dict(post.metadata), post.content


def write_reviewed(original_filename: str, meta: dict, reviewed_text: str) -> Path:
    REVIEWED_DIR.mkdir(exist_ok=True)
    path = REVIEWED_DIR / original_filename
    updated_meta = {**meta, "reviewed_at": _now(), "status": "reviewed"}
    header = _make_header(updated_meta)
    path.write_text(header + reviewed_text)
    return path


def list_reviewed() -> list[Path]:
    return sorted(REVIEWED_DIR.glob("*.md"))


def read_reviewed(path: Path) -> tuple[dict, str]:
    """Returns (meta, content_after_Refined_Content_section)."""
    post = frontmatter.load(str(path))
    content = post.content
    if "## Refined Content" in content:
        content = content.split("## Refined Content", 1)[1].strip()
    return dict(post.metadata), content


# --- helpers ---

def _make_header(meta: dict) -> str:
    return "---\n" + yaml.dump(meta, default_flow_style=False) + "---\n\n"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
