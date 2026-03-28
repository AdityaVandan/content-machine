#!/usr/bin/env python3
"""
Layer 1: Generate content drafts from input.md

Usage:
    python scripts/01_generate.py

Output:
    drafts/{platform}_{slug}.md  for each platform listed in input.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_io import read_input_md, write_draft, make_slug
from core.llm import call_llm
from agents.generator_agent import SYSTEM_PROMPT, GENERATOR_CONFIG, build_prompt


def main() -> None:
    print("Layer 1: Generating drafts from input.md...\n")

    try:
        meta, raw_learnings = read_input_md("input.md")
    except FileNotFoundError as e:
        print("ERROR: input.md not found. Create it first (see input.md.example).", e)
        sys.exit(1)

    platforms: list[str] = meta.get("platforms", [])
    if not platforms:
        print("ERROR: No platforms specified in input.md frontmatter.")
        sys.exit(1)

    if not raw_learnings.strip():
        print("ERROR: input.md body is empty. Add your learnings below the frontmatter.")
        sys.exit(1)

    slug = make_slug(meta.get("topic", "content"))

    for platform in platforms:
        print(f"  Generating {platform}...")
        prompt = build_prompt(
            platform=platform,
            raw_learnings=raw_learnings,
            topic=meta.get("topic", ""),
            target_audience=meta.get("target_audience", "developers"),
            tone=meta.get("tone", "conversational"),
        )
        try:
            content = call_llm(SYSTEM_PROMPT, prompt, GENERATOR_CONFIG)
        except Exception as e:
            print(f"  ERROR generating {platform}: {e}")
            continue

        output_path = write_draft(platform, slug, meta, content)
        print(f"  Written: {output_path}")

    print(f"\nDone. Review files in drafts/, edit freely, then run:")
    print(f"  python scripts/02_review.py")


if __name__ == "__main__":
    main()
