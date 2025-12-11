"""
Discord Webhook notification strategy.
"""
import requests
from datetime import datetime
from .base import NotificationStrategy


class DiscordNotifier(NotificationStrategy):
    """
    Send notifications via Discord Webhook.
    
    Setup:
        1. Go to your Discord server -> Settings -> Integrations -> Webhooks
        2. Create a new webhook and copy the URL
        3. Add to .env: DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
    """
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
    
    def send(self, message: str, **kwargs) -> bool:
        """
        Send a notification to Discord.
        
        Args:
            message: The link/content to send
            **kwargs: timestamp, source (meeting URL)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        timestamp = kwargs.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        source = kwargs.get("source", "Unknown")
        
        # Create rich embed
        embed = {
            "title": "🎫 TicketSentry Alert!",
            "color": 0x5865F2,  # Discord Blurple
            "fields": [
                {
                    "name": "🔗 Link Found",
                    "value": message,
                    "inline": False
                },
                {
                    "name": "⏰ Time",
                    "value": timestamp,
                    "inline": True
                },
                {
                    "name": "📍 Source",
                    "value": source,
                    "inline": True
                }
            ],
            "footer": {
                "text": "TicketSentry • Automated Link Detection"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                print("[📨 Discord] Notification sent successfully!")
                return True
            else:
                print(f"[❌ Discord] Failed to send: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"[❌ Discord] Error: {e}")
            return False
