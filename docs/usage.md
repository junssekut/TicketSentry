# Usage Guide

## Basic Usage

To start the miner, provide the Zoom meeting URL. The tool will automatically convert standard invite links to the Web Client format.

```bash
python run.py "https://zoom.us/j/123456789?pwd=abc..."
```

## What Happens Next?

1.  **Initialization**: The tool launches a Chrome window using your configured profile.
2.  **Navigation**: It navigates to the Zoom Web Client (`/wc/join`).
3.  **Entry**: It handles "Join Audio" popups automatically.
4.  **Monitoring**: It opens the Chat panel and begins scanning.
5.  **Collection**:
    *   When a link matching the keywords (e.g., Google Forms) is found:
    *   It is printed to the console: `[💰 FOUND] ...`
    *   It is saved to `loot/collected_links.txt`.
    *   It is reported to Sentry (if configured).

## Stopping the Tool

*   Press `Ctrl+C` in the terminal to stop the miner.
*   The browser window will remain open (`detach=True`) so you can manually verify or interact if needed.

## Troubleshooting

*   **Chrome Crashes immediately**: Ensure all other Chrome windows are closed before running the tool. Selenium cannot attach to a user data directory that is already in use.
*   **"Element not found"**: Zoom UI may have changed. Check Sentry logs for details.
