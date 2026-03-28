from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str
    openrouter_model: str = "anthropic/claude-sonnet-4.6"

    buffer_access_token: str
    buffer_twitter_profile_id: str
    buffer_linkedin_profile_id: str
    buffer_bluesky_profile_id: str

    model_config = SettingsConfigDict(
        # Always load the v2 env file, regardless of current working directory.
        env_file=str(Path(__file__).resolve().parents[1] / ".env"),
        case_sensitive=False,
        # Allow other env vars to exist (e.g., repo-root .env) without failing.
        extra="ignore",
    )


def _build_settings() -> "Settings":
    try:
        return Settings()
    except Exception as e:
        v2_dir = Path(__file__).resolve().parents[1]
        env_path = v2_dir / ".env"
        example_path = v2_dir / ".env.example"
        hint = (
            "Missing required environment variables for v2.\n\n"
            f"Create `{env_path}` (it is gitignored) from `{example_path}` and set:\n"
            "- OPENROUTER_API_KEY\n"
            "- BUFFER_ACCESS_TOKEN\n\n"
            "Alternatively, export `OPENROUTER_API_KEY` and `BUFFER_ACCESS_TOKEN` in your shell."
        )
        raise RuntimeError(hint) from e


settings = _build_settings()
