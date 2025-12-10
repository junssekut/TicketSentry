# Configuration Guide

The application is configured via a `.env` file in the project root.

## Setup

1.  Copy the example configuration file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` with your specific settings.

## Chrome Profile Setup (Crucial)

To bypass 2FA and SSO logins, this tool uses your existing Chrome session. You need to point the tool to your Chrome User Data directory.

### Finding Your Paths

1.  Open Chrome.
2.  Navigate to `chrome://version`.
3.  Look for **Profile Path**.
    *   Example: `/Users/username/Library/Application Support/Google/Chrome/Default`
    *   **User Data Dir**: `/Users/username/Library/Application Support/Google/Chrome`
    *   **Profile Directory**: `Default`

### Setting Variables in .env

*   `CHROME_USER_DATA_DIR`: Path to the User Data folder.
*   `CHROME_PROFILE_DIRECTORY`: Name of the profile folder (e.g., "Default", "Profile 1").

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

