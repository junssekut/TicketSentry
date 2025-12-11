"""
Notification Manager Service.
"""
from typing import List
from src.config import config
from src.services.notifications.base import NotificationStrategy
from src.services.notifications.gui import GuiNotification
from src.services.notifications.discord import DiscordNotifier
from src.services.notifications.telegram import TelegramNotifier
from src.services.sentry_service import SentryService


class NotificationManager:
    """
    Manages multiple notification channels.
    Supports: GUI, Discord Webhook, Telegram Bot
    """
    
    def __init__(self):
        self.channels: List[NotificationStrategy] = []
        self._setup_channels()

    def _setup_channels(self):
        """Setup notification channels from config."""
        # Always add GUI notification
        self.add_channel(GuiNotification())
        
        # Add Discord if configured
        if config.DISCORD_WEBHOOK_URL:
            discord = DiscordNotifier(config.DISCORD_WEBHOOK_URL)
            if discord.enabled:
                self.add_channel(discord)
                print("[✓] Discord notifications enabled")
        
        # Add Telegram if configured
        if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
            telegram = TelegramNotifier(
                config.TELEGRAM_BOT_TOKEN,
                config.TELEGRAM_CHAT_ID
            )
            if telegram.enabled:
                self.add_channel(telegram)
                print("[✓] Telegram notifications enabled")

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
