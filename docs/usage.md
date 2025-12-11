# Usage Guide

## Basic Usage

To start the miner, provide the Zoom meeting URL. The tool will automatically convert standard invite links to the Web Client format.

```bash
python run.py "https://zoom.us/j/123456789?pwd=abc..."
```

## What Happens Next?

1.  **Initialization**: The tool launches a fresh Chrome window.
2.  **Authentication**: Navigates to Zoom domain and completes Microsoft SSO login.
3.  **Navigation**: Redirects to the meeting URL via Web Client (`/wc/join`).
4.  **Entry**: Handles "Continue without Audio/Video" and joins the meeting.
5.  **Monitoring**: Opens the Chat panel and begins scanning.
6.  **Collection**:
    *   All chat messages are logged to `loot/chat_log.txt`.
    *   When a target link is found (e.g., forms.office, forms.gle):
        *   It is printed to the console: `[💰 FOUND] ...`
        *   It is saved to `loot/collected_links.txt`.
        *   Push notifications are sent (Discord/Telegram if configured).
        *   It is reported to Sentry (if configured).

## Stopping the Tool

*   Press `Ctrl+C` in the terminal to stop the miner.
*   The browser window will remain open (`detach=True`) so you can manually verify or interact if needed.

## Output Files

| File | Description |
|------|-------------|
| `loot/collected_links.txt` | All detected attendance/form links with timestamps |
| `loot/chat_log.txt` | Complete chat history from the meeting |

## Troubleshooting

*   **Microsoft login fails**: Ensure `MS_EMAIL` and `MS_PASSWORD` are correct in `.env`. If 2FA is enabled, leave credentials empty and login manually when prompted.
*   **"Element not found"**: Zoom UI may have changed. Check Sentry logs for details.
*   **No notifications**: Verify your webhook URL or bot token is correct. Check console for `[✓] Discord/Telegram notifications enabled` on startup.
