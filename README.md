# SAT-Miner (TicketSentry)

**SAT-Miner** is a specialized CLI automation tool designed to aggregate specific links from Zoom meeting chats. It leverages Selenium with Microsoft SSO authentication to seamlessly join meetings via the Web Client.

## 🚀 Features

*   **Microsoft SSO Login**: Automatic authentication via Microsoft/Office365 credentials.
*   **Push Notifications**: Get instant alerts on your phone via **Discord** or **Telegram**.
*   **Visual Notifications**: "Always-on-top" popup alerts when a link is detected.
*   **Headless Mode**: Run silently in the background or watch the browser in action.
*   **Web Client Optimization**: Automatically transforms desktop links to lightweight Web Client URLs.
*   **Auto-Pilot**: Handles "Continue without Audio/Video" and joins meetings automatically.
*   **Chat Logging**: All chat messages are saved to `loot/chat_log.txt`.
*   **Passive Collection**: Silently monitors chat for target keywords (e.g., `forms.gle`, `forms.office`).
*   **Remote Monitoring**: Integrated with Sentry for real-time status and error reporting.

## 📚 Documentation

Detailed documentation is available in the `/docs` directory:

*   [**Configuration Guide**](docs/configuration.md): Setting up Chrome profiles, Sentry, and Headless mode.
*   [**Usage Guide**](docs/usage.md): How to run and operate the tool.
*   [**Versioning Guide**](docs/versioning.md): Semantic versioning and release process.e profiles and Sentry.
*   [**Usage Guide**](docs/usage.md): How to run and operate the tool.

## ⚡️ Quick Start

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure**:
    Copy `.env.example` to `.env` and add your Microsoft credentials + notification settings.
    ```bash
    cp .env.example .env
    ```
    
    Required settings:
    ```env
    MS_EMAIL=your.email@example.com
    MS_PASSWORD=your_password
    ```
    
    Optional notifications:
    ```env
    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
    TELEGRAM_BOT_TOKEN=123456:ABC...
    TELEGRAM_CHAT_ID=123456789
    ```

3.  **Run**:
    ```bash
    python run.py "https://your-zoom-url.com/j/..."
    ```

## 📂 Project Structure

```
├── src/
│   ├── config.py           # Configuration
│   ├── core/               # Miner Logic & Driver Factory
│   ├── services/           # Sentry, Notifications, & File I/O
│   │   └── notifications/  # Discord, Telegram, GUI notifiers
│   └── utils/              # Helpers
├── loot/                   # Collected links & chat logs
└── docs/                   # Documentation
```

## 📱 Notification Setup

### Discord
1. Server Settings → Integrations → Webhooks → New Webhook
2. Copy URL → Add to `.env` as `DISCORD_WEBHOOK_URL`

### Telegram
1. Message [@BotFather](https://t.me/BotFather) → `/newbot`
2. Copy token → Add to `.env` as `TELEGRAM_BOT_TOKEN`
3. Get your chat ID from `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Add to `.env` as `TELEGRAM_CHAT_ID`

## ⚠️ Disclaimer

This tool is for educational and automation testing purposes only. Please ensure you comply with the Terms of Service of the platforms you interact with.
