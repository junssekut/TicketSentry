"""
Notification strategies for TicketSentry.
"""
from .base import NotificationStrategy
from .gui import GuiNotification
from .discord import DiscordNotifier
from .telegram import TelegramNotifier
from .manager import NotificationManager

__all__ = [
    "NotificationStrategy",
    "GuiNotification", 
    "DiscordNotifier",
    "TelegramNotifier",
    "NotificationManager",
]