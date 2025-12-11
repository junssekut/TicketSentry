"""
Telegram Bot notification strategy.
"""
import re
import requests
from datetime import datetime
from .base import NotificationStrategy


class TelegramNotifier(NotificationStrategy):
    """
    Send notifications via Telegram Bot.
    
    Setup:
        1. Message @BotFather on Telegram -> /newbot -> follow steps
        2. Copy the bot token
        3. Start a chat with your bot
        4. Get your chat ID from: https://api.telegram.org/bot<TOKEN>/getUpdates
        5. Add to .env:
           TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
           TELEGRAM_CHAT_ID=123456789
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage" if bot_token else ""
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for MarkdownV2."""
        # Characters that need escaping in MarkdownV2
        special_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)
    
    def send(self, message: str, **kwargs) -> bool:
        """
        Send a notification to Telegram.
        
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
        
        # Format message with MarkdownV2
        escaped_timestamp = self._escape_markdown(timestamp)
        escaped_source = self._escape_markdown(source)
        
        text = f"""🎫 *TicketSentry Alert\\!*
━━━━━━━━━━━━━━━━━━━

🔗 *Link Found*
`{message}`

⏰ {escaped_timestamp}
📍 {escaped_source}

━━━━━━━━━━━━━━━━━━━"""
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": False
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("[📨 Telegram] Notification sent successfully!")
                return True
            else:
                print(f"[❌ Telegram] Failed to send: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"[❌ Telegram] Error: {e}")
            return False
