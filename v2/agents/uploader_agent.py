"""
Layer 3 Agent: Uploader

Formatting logic for each platform before Buffer API upload.
No LLM calls here — content was already refined in Layer 2.
"""

# Buffer GraphQL API endpoint (single POST endpoint, no /graphql path)
BUFFER_GRAPHQL_ENDPOINT = "https://api.buffer.com"


def format_twitter_thread(refined_content: str) -> list[str]:
    """Parse ## Tweet N sections into a list of tweet strings."""
    tweets: list[str] = []
    current_lines: list[str] = []

    for line in refined_content.split("\n"):
        if line.strip().startswith("## Tweet") and current_lines:
            text = "\n".join(current_lines).strip()
            if text:
                tweets.append(text)
            current_lines = []
        elif not line.strip().startswith("## Tweet"):
            current_lines.append(line)

    # flush last tweet
    text = "\n".join(current_lines).strip()
    if text:
        tweets.append(text)

    return [t for t in tweets if t]


def format_bluesky_post(refined_content: str) -> str:
    """Extract content under the ## Content section for Bluesky."""
    lines = refined_content.split("\n")
    in_content = False
    result: list[str] = []

    for line in lines:
        if line.strip() == "## Content":
            in_content = True
            continue
        if in_content and line.startswith("## "):
            break
        if in_content:
            result.append(line)

    return "\n".join(result).strip()


def format_linkedin_post(refined_content: str) -> str:
    """Extract content under the ## Content section."""
    lines = refined_content.split("\n")
    in_content = False
    result: list[str] = []

    for line in lines:
        if line.strip() == "## Content":
            in_content = True
            continue
        if in_content and line.startswith("## "):
            break
        if in_content:
            result.append(line)

    return "\n".join(result).strip()
