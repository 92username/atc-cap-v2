"""Shared path utilities for output storage."""

import os
from pathlib import Path

# Base directory for uploads and generated outputs.
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/data/uploads")).expanduser()


def ensure_output_dir() -> Path:
    """Ensure the configured output directory exists and return it."""
    # Re-compute from environment in case it changed after import.
    env_path = Path(os.getenv("OUTPUT_DIR", str(OUTPUT_DIR))).expanduser()
    env_path.mkdir(parents=True, exist_ok=True)
    return env_path
