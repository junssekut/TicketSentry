# Configuration Guide

The application is configured via a `.env` file in the project root.

## Setup

1.  Copy the example configuration file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` with your specific settings.

## Microsoft Authentication

The tool now uses a fresh anonymous Chrome profile to avoid corruption issues. To access authenticated Zoom meetings, you need to provide your Microsoft credentials:

### Setting Up Credentials

1.  Open `.env` file
2.  Add your Microsoft/Office365 credentials:
    ```
    MS_EMAIL=your.email@example.com
    MS_PASSWORD=your_password_here
    ```

The tool will automatically:
- Create a temporary Chrome profile
- Navigate to the Zoom meeting
- Detect Microsoft login page
- Enter your credentials
- Complete the authentication flow

### Manual Login Option

If you prefer not to store credentials or have 2FA enabled:
- Leave `MS_EMAIL` and `MS_PASSWORD` empty in `.env`
- The tool will pause and prompt you to login manually
- Press Enter after logging in to continue

## Sentry Integration (Optional)

For remote monitoring and error tracking:

1.  Create an account at [sentry.io](https://sentry.io).
2.  Create a new Python project.
3.  Get your **DSN** (Client Key).
4.  Set `SENTRY_DSN` in your `.env` file.

## Miner Settings

You can also tune:

*   `POLL_INTERVAL`: How often (in seconds) to scan the chat.
*   `PAGE_LOAD_DELAY_MIN` / `MAX`: Random delay range for page loads.
*   `HEADLESS`: Set to `true` to run browser in background (default: `false`).

## Push Notifications (Optional)

Get instant alerts on your phone when attendance links are detected!

### Discord Webhook

1. Go to your Discord server → **Settings** → **Integrations** → **Webhooks**
2. Click **New Webhook** and configure it
3. Click **Copy Webhook URL**
4. Add to your `.env`:
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdef...
   ```

### Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the **bot token** (looks like `123456789:ABCdefGHI...`)
4. Start a chat with your new bot (send any message)
5. Get your **chat ID**:
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find `"chat":{"id":123456789}` in the response
6. Add to your `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNO...
   TELEGRAM_CHAT_ID=123456789
   ```

### Using Both

You can configure both Discord and Telegram - all enabled channels will receive notifications when a link is found.

### Notification Preview

**Discord:**
```
🎫 TicketSentry Alert!
🔗 Link Found: https://forms.office.com/r/abc123
⏰ Time: 2025-12-11 12:55:14
📍 Source: customdomain.zoom.us
```

**Telegram:**
```
🎫 TicketSentry Alert!
━━━━━━━━━━━━━━━━━━━
🔗 Link Found
https://forms.office.com/r/abc123
⏰ 2025-12-11 12:55:14
📍 customdomain.zoom.us
━━━━━━━━━━━━━━━━━━━
```

