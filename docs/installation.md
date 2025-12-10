# Installation Guide

## Prerequisites

*   **Python 3.9+**: Ensure Python is installed and added to your PATH.
*   **Google Chrome**: The browser must be installed.
*   **Chrome User Profile**: You should have a Chrome profile logged into Zoom (SSO/Google) to bypass authentication steps.

## Setup Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/junssekut/TicketSentry.git
    cd TicketSentry
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Verification

Run the following command to verify installation:
```bash
python run.py --help
```
You should see the help message for the SAT-Miner tool.
