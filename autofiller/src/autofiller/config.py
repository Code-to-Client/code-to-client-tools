"""Configuration constants for the contact form autofiller."""

from pathlib import Path


class Config:
    """Configuration constants for the contact form autofiller."""

    # File paths
    FIELD_CONFIG_FILE = Path(__file__).parent.parent.parent / "field_config.json"

    # LLM Configuration Constants
    # Default provider is together_ai
    LLM_PROVIDER_PREFIX = "together_ai"
    # Default model is Qwen/Qwen3-235B-A22B-Instruct-2507-tput
    LLM_MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507-tput"

    # Optional base URL for self-hosted/local LLM providers (e.g. Ollama: "http://localhost:11434/v1").
    # When None, the client uses the provider's default API endpoint.
    LLM_BASE_URL = None

    DB_PATH = Path(__file__).resolve().parents[3] / "contacts.db"
