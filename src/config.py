"""
Configuration management for SAT-Miner.
"""
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # Sentry Configuration
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", None)
    SENTRY_ENV: str = os.getenv("SENTRY_ENV", "production")
    SENTRY_SAMPLE_RATE: float = 1.0

    # Chrome Configuration
    # Default to macOS path, but allow override via env var
    CHROME_USER_DATA_DIR: str = os.getenv(
        "CHROME_USER_DATA_DIR", 
        "/Users/arjunaandio/Library/Application Support/Google/Chrome"
    )
    CHROME_PROFILE_DIRECTORY: str = os.getenv("CHROME_PROFILE_DIRECTORY", "Default")
    
    # Headless Mode
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # Miner Configuration
    POLL_INTERVAL: int = 5
    PAGE_LOAD_DELAY_MIN: float = 5.0
    PAGE_LOAD_DELAY_MAX: float = 8.0
    
    # Target Keywords for Link Discovery
    KEYWORDS: List[str] = field(default_factory=lambda: [
        "forms.gle", 
        "docs.google.com", 
        "tinyurl", 
        "bit.ly", 
        "attendance", 
        "presensi",
        "forms.office"
    ])

# Global configuration instance
config = AppConfig()
