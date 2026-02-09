# Daily AI Tech News Automation

This project is a high-performance, automated system designed to aggregate daily AI and Machine Learning news. It leverages a universal scraping engine to collect data from any specified URL (RSS or HTML-based dynamic sites) and organizes it into localized **Excel** files and cloud-based **Google Sheets**.

---

## [!] Key Features

- **Dynamic CLI Interaction**: Input up to 1000 URLs at runtime or use pre-configured defaults.
- **Universal Scraping Engine**: Automatically detects source types (RSS feed vs. Dynamic Webpage) and extracts relevant content.
- **Granular Execution Control**: Configure article limits per source and optional cloud synchronization.
- **Multi-Format Storage**:
    - **Raw Data**: Captures original scraped content.
    - **Cleaned Data**: Sanitized titles and summaries for better readability.
    - **Google Sheets**: Optional cloud sync with automated setup guides.
- **Local & Cloud Integration**: Seamlessly saves to `.xlsx` files and uploads to Google Sheets.
- **Robust Scheduling**: Integrated `main_scheduler.py` for fully automated daily operations.
- **Advanced Logging**: Categorized failure reasons, per-URL status reporting, and ASCII-only logging for maximum compatibility.

---

## [Architecture] Project Architecture

```
AI_DAILY_TECH_NEWS_AUTOMATION/
+-- src/                          # Core logic and modules
|   +-- detection/                # Source type identification
|   |   +-- source_detector.py    # Detects RSS vs HTML vs Dynamic sites
|   +-- extractors/               # Content extraction logic
|   |   +-- base_extractor.py     # Template for all extractors
|   |   +-- dynamic_extractor.py  # Handles JS-heavy sites using Playwright
|   |   +-- html_extractor.py     # Standard HTML parsing (BS4)
|   |   +-- rss_extractor.py      # RSS/Atom feed parsing
|   +-- scraper/                  # High-level scraping orchestration
|   |   +-- news_scraper.py       # Manages the scraping workflow
|   +-- sheets/                   # Cloud integration
|   |   +-- google_sheets.py      # Google Sheets API operations
|   +-- utils/                    # Shared utilities
|   |   +-- excel_handler.py      # Excel processing (OpenPyXL/Pandas)
|   |   +-- logger.py             # ASCII-standard logging system
|   |   +-- rate_limiter.py       # Prevents IP blocking
|   |   +-- text_cleaner.py       # HTML sanitization
|   |   +-- user_agent_manager.py # Rotating headers for stealth
|   +-- models.py                 # Data schemas
+-- data/                         # Organized output folders
|   +-- raw data/                 # Raw scrapes
|   +-- cleaned/                  # Processed articles
+-- logs/                         # Detailed execution logs
+-- main.py                       # Main interactive CLI entry point
+-- main_scheduler.py             # Daemon for automated daily tasks
+-- requirements.txt              # Project dependencies
+-- USAGE.md                      # Detailed user guide
+-- .gitignore                    # Version control exclusions
```

---

## [Setup] Tech Stack & Dependencies

- **Language**: Python 3.8+
- **Scraping**: `BeautifulSoup4`, `Playwright`, `Trafilatura`, `feedparser`
- **Data**: `Pandas`, `OpenPyXL`
- **Cloud**: `gspread`, `oauth2client`
- **Automation**: `Schedule`

> **Note**: For Playwright to work on HTML-heavy sites, run `playwright install chromium` after installing requirements.

---

## [Installation] Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/monish-exz/ai-daily-tech-news-automation.git
    cd ai-daily-tech-news-automation
    ```

2.  **Run the automated setup script**:
    This script will install all dependencies (including Playwright browsers for dynamic sites) and create necessary directories.
    ```bash
    python setup_project.py
    ```

3.  **Run the scraper**:
    ```bash
    python main.py
    ```

---

## [Status] Logging Standard

The project adheres to the **ASCII-only logging standard**, ensuring logs are readable across all terminal environments. `logs/execution.log` tracks:
- Scrape success/failure per URL.
- Specific error types (e.g., Timeout, Parsing Error, SSL Issues).
- Sync status for Google Sheets.

---

## [Notes] Notes

- **Google Sheets**: Requires a `credentials.json` file in the root directory. Follow the setup guide in `USAGE.md`.
- **Customization**: Easily extendable via the `UniversalScraper` class logic.
