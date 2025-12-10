# SAT-Miner (TicketSentry)

**SAT-Miner** is a specialized CLI automation tool designed to aggregate specific links from Zoom meeting chats. It leverages Selenium and existing Chrome User Profiles to seamlessly join meetings via the Web Client, bypassing complex authentication flows like SSO and 2FA.

## 🚀 Features

*   **Headless-Ready Architecture**: Designed for stability and performance.
*   **Smart Authentication**: Uses your local Chrome Profile to authenticate (no credentials stored in code).
*   **Web Client Optimization**: Automatically transforms desktop links to lightweight Web Client URLs.
*   **Auto-Pilot**: Handles "Join Audio" and other common entry modals.
*   **Passive Collection**: Silently monitors chat for target keywords (e.g., `forms.gle`, `docs.google.com`).
*   **Remote Monitoring**: Integrated with Sentry for real-time status and error reporting.

## 📚 Documentation

Detailed documentation is available in the `/docs` directory:

*   [**Installation Guide**](docs/installation.md): Setup instructions and dependencies.
*   [**Configuration Guide**](docs/configuration.md): Setting up Chrome profiles and Sentry.
*   [**Usage Guide**](docs/usage.md): How to run and operate the tool.

## ⚡️ Quick Start

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure**:
    Copy `.env.example` to `.env` and update it with your Chrome User Data path.
    ```bash
    cp .env.example .env
    ```

3.  **Run**:
    ```bash
    python run.py "https://your-zoom-url.com/j/..."
    ```

## 📂 Project Structure

```
TicketSentry/
├── run.py                  # CLI Entry Point
├── src/
│   ├── config.py           # Configuration
│   ├── core/               # Miner Logic & Driver Factory
│   ├── services/           # Sentry & File I/O
│   └── utils/              # Helpers
├── loot/                   # Collected links output
└── docs/                   # Documentation
```

## ⚠️ Disclaimer

This tool is for educational and automation testing purposes only. Please ensure you comply with the Terms of Service of the platforms you interact with.
