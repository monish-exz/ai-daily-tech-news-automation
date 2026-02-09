# Usage Guide - Daily AI Tech News Automation

This guide explains how to set up, run, and schedule the project for automated AI news aggregation.

---

## 1. Environment Setup

### 1.1 Virtual Environment
It is highly recommended to use a virtual environment:
```bash
# Create environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 1.2 Dependencies
The easiest way to set up everything (including folders and browsers) is to run:
```bash
python setup_project.py
```

Alternatively, you can install manually:
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 2. Google Sheets Configuration

To sync data to the cloud, follow these steps:

1. **Google Cloud Console**:
    - Go to [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Enable **Google Sheets API** and **Google Drive API**.
2. **Credentials**:
    - Navigate to **APIs & Services > Credentials**.
    - Click **Create Credentials > Service Account**.
    - Create the account, then go to the **Keys** tab for that account.
    - **Add Key > Create New Key > JSON**.
    - Rename the downloaded file to `credentials.json` and place it in the project root.
3. **Sharing**:
    - Open your target Google Sheet.
    - Share it with the `client_email` found inside your `credentials.json`.

---

## 3. Running the Scraper

### 3.1 Interactive CLI (main.py)
The primary way to use the tool is via the interactive CLI:
```bash
python main.py
```

**Workflow:**
- **URL Count**: Specify how many sources you want to scrape (1-1000).
- **URL Input**: Enter URLs one by one. If left blank, it defaults to pre-configured RSS feeds.
- **Article Limit**: Set the maximum number of articles to fetch per source.
- **Cloud Sync**: Choose whether to upload the results to Google Sheets (Y/N).

### 3.2 Automated Scheduler (main_scheduler.py)
For a set-it-and-forget-it approach:
```bash
python main_scheduler.py
```
- Runs daily at **09:00 AM**.
- Automatically scrapes default sources and saves data locally.
- Configuration can be changed directly in the script.

---

## 4. Understanding Output

- **data/raw data/**: Original scraped data in Excel format.
- **data/cleaned/**: Processed data with sanitized HTML and clean text.
- **logs/execution.log**: Check here for per-URL success/failure reports and specific error details.

---

## 5. Troubleshooting

- **Failed Scrapes**: If a site fails, check `logs/execution.log`. It might be due to a timeout, anti-bot measures, or invalid URL structure.
- **Playwright Errors**: If dynamic sites fail, ensure you ran `playwright install`.
- **Sheets Access**: Ensure the service account email has **Editor** access to the sheet.

---

**End of Guide**