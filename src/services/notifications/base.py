"""
Abstract base class for notification strategies.
"""
from abc import ABC, abstractmethod

class NotificationStrategy(ABC):
    """
    Interface for all notification methods.
    """
    
    @abstractmethod
    def send(self, message: str, **kwargs):
        """
        Send a notification.
        
        Args:
            message: The main content/link to send.
            **kwargs: Additional context (e.g., timestamp, source).
        """
        pass
