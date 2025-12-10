"""
Service for managing discovered 'loot' (collected links).
"""
import os
from datetime import datetime
from src.services.sentry_service import SentryService

class LootManager:
    """
    Handles the storage and persistence of found links.
    """
    
    def __init__(self, loot_dir: str = "loot", filename: str = "collected_links.txt"):
        self.loot_dir = loot_dir
        self.filename = filename
        self.filepath = os.path.join(self.loot_dir, self.filename)
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the loot directory exists."""
        os.makedirs(self.loot_dir, exist_ok=True)

    def save_link(self, url: str):
        """
        Append a found link to the storage file with a timestamp.
        
        Args:
            url: The URL to save.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {url}\n"
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(entry)
            return True
        except IOError as e:
            # We might want to log this or re-raise depending on severity
            print(f"[!] Failed to save link: {e}")
            SentryService.capture_exception(e)
            return False
