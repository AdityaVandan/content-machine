#!/usr/bin/env python3
"""
Layer 3: Upload reviewed content to Buffer

Usage:
    python scripts/03_upload.py             # push to Buffer
    python scripts/03_upload.py --dry-run   # preview without posting
"""
import sys
import argparse
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings
from core.file_io import list_reviewed, read_reviewed
from agents.uploader_agent import (
    BUFFER_GRAPHQL_ENDPOINT,
    format_twitter_thread,
    format_linkedin_post,
    format_bluesky_post,
)


CREATE_POST_MUTATION = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post {
        id
        text
      }
    }
    ... on MutationError {
      message
    }
  }
}
"""

PLATFORM_LIMITS = {
    "twitter_thread": 280,
    "bluesky_post": 300,
    "linkedin_post": 3000,
}


def _truncate_with_ellipsis(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    if max_len <= 3:
        return text[:max_len]
    return text[: max_len - 3].rstrip() + "..."


def _chunk_by_words(text: str, max_len: int) -> list[str]:
    """
    Split text into <= max_len chunks, preferring word boundaries.
    Preserves existing newlines by treating them as paragraph boundaries.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_len:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for para in paragraphs:
        if len(para) > max_len:
            flush()
            words = para.split()
            buf = ""
            for w in words:
                candidate = (buf + " " + w).strip()
                if len(candidate) <= max_len:
                    buf = candidate
                else:
                    if buf:
                        chunks.append(buf)
                        buf = w
                    else:
                        chunks.append(w[:max_len])
                        rest = w[max_len:]
                        while rest:
                            chunks.append(rest[:max_len])
                            rest = rest[max_len:]
                        buf = ""
            if buf:
                chunks.append(buf)
            continue

        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate) <= max_len:
            current = candidate
        else:
            flush()
            current = para

    flush()
    return [c for c in chunks if c]


def _enforce_platform_limits(platform: str, text_or_texts):
    max_len = PLATFORM_LIMITS.get(platform)
    if not max_len:
        return text_or_texts

    if isinstance(text_or_texts, list):
        out: list[str] = []
        for t in text_or_texts:
            if len(t) <= max_len:
                out.append(t)
            else:
                parts = _chunk_by_words(t, max_len)
                out.extend(parts)
                print(f"    NOTE: split 1 item into {len(parts)} parts to fit {max_len} chars")
        return out

    if len(text_or_texts) > max_len:
        print(f"    NOTE: truncating from {len(text_or_texts)} to {max_len} chars")
        return _truncate_with_ellipsis(text_or_texts, max_len)
    return text_or_texts


def push_to_buffer(channel_id: str, text: str, dry_run: bool = False) -> None:
    if dry_run:
        print(f"    [DRY RUN] {text[:120]}{'...' if len(text) > 120 else ''}")
        return
    print("push_to_buffer")

    resp = requests.post(
        BUFFER_GRAPHQL_ENDPOINT,
        json={
            "query": CREATE_POST_MUTATION,
            "variables": {
                "input": {
                    "channelId": channel_id,
                    "text": text,
                    # Required by Buffer: schedulingType + mode
                    # `queue` adds to the Buffer queue (no explicit dueAt needed).
                    "schedulingType": "automatic",
                    "mode": "addToQueue",
                }
            },
        },
        headers={
            "Authorization": f"Bearer {settings.buffer_access_token}",
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    resp.raise_for_status()

    data = resp.json()
    if "errors" in data and data["errors"]:
        raise RuntimeError(f"Buffer GraphQL errors: {data['errors']}")
    result = data.get("data", {}).get("createPost", {})
    if "message" in result:
        raise RuntimeError(f"Buffer error: {result['message']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload reviewed content to Buffer")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    args = parser.parse_args()

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"Layer 3: Uploading to Buffer [{mode}]...\n")

    reviewed_files = list_reviewed()
    if not reviewed_files:
        print("No reviewed files found in reviewed/. Run 02_review.py first.")
        sys.exit(1)

    for file_path in reviewed_files:
        meta, refined_content = read_reviewed(file_path)
        platform = meta.get("platform", file_path.stem)
        print(f"  {file_path.name} ({platform})")

        try:
            if platform == "twitter_thread":
                channel_id = settings.buffer_twitter_profile_id
                if not channel_id:
                    print("  SKIP: BUFFER_TWITTER_PROFILE_ID not set in .env")
                    continue
                tweets = _enforce_platform_limits(
                    platform, format_twitter_thread(refined_content)
                )
                for i, tweet in enumerate(tweets, 1):
                    push_to_buffer(channel_id, tweet, args.dry_run)
                    print(f"    Tweet {i}/{len(tweets)}: OK")

            elif platform == "linkedin_post":
                channel_id = settings.buffer_linkedin_profile_id
                if not channel_id:
                    print("  SKIP: BUFFER_LINKEDIN_PROFILE_ID not set in .env")
                    continue
                post_text = _enforce_platform_limits(
                    platform, format_linkedin_post(refined_content)
                )
                push_to_buffer(channel_id, post_text, args.dry_run)
                print(f"    LinkedIn post: OK")

            elif platform == "bluesky_post":
                channel_id = settings.buffer_bluesky_profile_id
                if not channel_id:
                    print("  SKIP: BUFFER_BLUESKY_PROFILE_ID not set in .env")
                    continue
                post_text = _enforce_platform_limits(
                    platform, format_bluesky_post(refined_content)
                )
                push_to_buffer(channel_id, post_text, args.dry_run)
                print(f"    Bluesky post: OK")

            else:
                print(f"  SKIP: unknown platform '{platform}'")

        except requests.HTTPError as e:
            print(f"  ERROR: Buffer returned HTTP {e.response.status_code}")
            print(f"  {e.response.text}")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
