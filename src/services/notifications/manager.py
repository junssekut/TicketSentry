"""
Notification Manager Service.
"""
from typing import List
from src.services.notifications.base import NotificationStrategy
from src.services.notifications.gui import GuiNotification
from src.services.sentry_service import SentryService

class NotificationManager:
    """
    Manages multiple notification channels.
    """
    
    def __init__(self):
        self.channels: List[NotificationStrategy] = []
        
        # Default configuration: Add GUI notification
        # In the future, we can load this from config/env
        self.add_channel(GuiNotification())

    def add_channel(self, channel: NotificationStrategy):
        """Register a new notification channel."""
        self.channels.append(channel)
    def notify_all(self, message: str, **kwargs):
        """Broadcast message to all registered channels."""
        for channel in self.channels:
            try:
                channel.send(message, **kwargs)
            except Exception as e:
                print(f"[!] Notification failed for {channel.__class__.__name__}: {e}")
                SentryService.capture_exception(e)
