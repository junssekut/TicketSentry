"""
Sentry integration service for error tracking and monitoring.
"""
import sentry_sdk
from sentry_sdk.integrations.mcp import MCPIntegration
from src.config import config

class SentryService:
    """
    Service responsible for initializing Sentry and reporting events.
    """
    
    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize the Sentry SDK."""
        if cls._initialized:
            return

        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            traces_sample_rate=config.SENTRY_SAMPLE_RATE,
            environment=config.SENTRY_ENV,
            integrations=[
                MCPIntegration()
            ]
        )
        cls._initialized = True

    @staticmethod
    def capture_exception(exception: Exception):
        """Capture and report an exception."""
        sentry_sdk.capture_exception(exception)

    @staticmethod
    def capture_message(message: str, level: str = "info"):
        """Capture and report a message."""
        sentry_sdk.capture_message(message, level=level)

    @staticmethod
    def start_transaction(name: str, op: str):
        """Start a performance monitoring transaction."""
        return sentry_sdk.start_transaction(name=name, op=op)
