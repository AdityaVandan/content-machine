#!/usr/bin/env python3
"""
Layer 2: AI-review all drafts in drafts/

Usage:
    python scripts/02_review.py

Output:
    reviewed/{platform}_{slug}.md  for each file in drafts/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_io import list_drafts, read_draft, write_reviewed
from core.llm import call_llm
from agents.reviewer_agent import SYSTEM_PROMPT, REVIEWER_CONFIG, build_prompt


def main() -> None:
    print("Layer 2: Reviewing drafts...\n")

    drafts = list_drafts()
    if not drafts:
        print("No drafts found in drafts/. Run 01_generate.py first.")
        sys.exit(1)

    for draft_path in drafts:
        meta, content = read_draft(draft_path)
        platform = meta.get("platform", draft_path.stem)
        print(f"  Reviewing {draft_path.name}...")

        prompt = build_prompt(
            platform=platform,
            draft_content=content,
            topic=meta.get("topic", ""),
            target_audience=meta.get("target_audience", "developers"),
        )
        try:
            reviewed_text = call_llm(SYSTEM_PROMPT, prompt, REVIEWER_CONFIG)
        except Exception as e:
            print(f"  ERROR reviewing {draft_path.name}: {e}")
            continue

        output_path = write_reviewed(draft_path.name, meta, reviewed_text)
        print(f"  Written: {output_path}")

    print(f"\nDone. Review files in reviewed/ (check ## Refined Content sections), then run:")
    print(f"  python scripts/03_upload.py --dry-run")


if __name__ == "__main__":
    main()
