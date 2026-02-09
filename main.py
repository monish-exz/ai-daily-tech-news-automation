"""
Main entry point for the Universal AI News Scraper.
Implements a dynamic CLI for user interaction.
"""

import logging
import sys
import os
from src.scraper.news_scraper import scrape_all_websites
from src.utils.excel_handler import save_to_excel
from src.sheets.google_sheets import upload_to_google_sheets
from src.utils.logger import setup_logger
from src.utils.text_cleaner import clean_html


GOOGLE_SHEETS_GUIDE = """
[!] Google Sheets Setup Guide:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select an existing one.
3. Enable 'Google Sheets API' and 'Google Drive API' in APIs & Services > Library.
4. Go to APIs & Services > Credentials.
5. Click 'Create Credentials' > 'Service Account'.
6. Follow prompts, then click on the new service account.
7. Go to 'Keys' tab > 'Add Key' > 'Create New Key' > 'JSON'.
8. Download the key, rename it to 'credentials.json', and place it in the project root.
9. SHARE your Google Sheet with the 'client_email' found in 'credentials.json'.
"""


def get_cli_inputs():
    """Interactive CLI to get URLs and configuration."""
    print("\n" + "="*50)
    print("                News Scraper-exz")
    print("="*50 + "\n")
    
    try:
        count_str = input("How many websites do you want to input? (Default 3, Max 1000): ").strip()
        count = int(count_str) if count_str else 3
        if count < 1 or count > 1000:
            print("[!] Count must be between 1 and 1000. Defaulting to 3.")
            count = 3
    except ValueError:
        print("[!] Invalid number. Defaulting to 3.")
        count = 3

    urls = []
    for i in range(1, count + 1):
        url = input(f"Enter URL for Website {i} (leave blank to skip): ").strip()
        if url:
            urls.append(url)
    
    if not urls:
        print("No URLs provided. Defaulting to standard RSS feeds.")
        urls = [
            "https://techcrunch.com/tag/artificial-intelligence/feed/",
            "https://www.technologyreview.com/feed/",
            "https://analyticsindiamag.com/feed/"
        ]
    
    try:
        limit_str = input("How many articles per website should be fetched? (Default 8): ").strip()
        limit = int(limit_str) if limit_str else 8
    except ValueError:
        print("Invalid number. Defaulting to 8.")
        limit = 8
        
    sync_sheets = input("Sync with Google Sheets? (Y/N, Default N): ").strip().upper() == 'Y'
    
    return urls, limit, sync_sheets


def main():
    # Setup logging
    setup_logger()
    logging.info("Dynamic CLI Script started")

    try:
        # Step 1: Get user input via Dynamic CLI
        urls, limit, sync_sheets = get_cli_inputs()
        
        print(f"\n[*] Starting universal scraping for {len(urls)} sources...")
        print("[*] This may take a moment (especially for dynamic sites)...\n")

        from src.scraper.news_scraper import UniversalScraper
        scraper = UniversalScraper()
        
        news_data_raw = []
        failed_urls = []
        
        for url in urls:
            try:
                print(f"[*] Scraping: {url}...")
                results = scraper.scrape_url(url, limit)
                
                if results:
                    # Convert dict format to legacy list format for backward compatibility
                    legacy_results = []
                    for r in results:
                        legacy_results.append([
                            r['title'],
                            r['date'],
                            r['source'],
                            r['link'],
                            r['content']
                        ])
                    news_data_raw.extend(legacy_results)
                    print(f"[+] Found {len(results)} articles.")
                else:
                    failed_urls.append(url)
                    print(f"[!] Failed to scrape: {url}. Check execution log for details.")
                    logging.warning(f"No results for {url}")
            except Exception as e:
                failed_urls.append(url)
                print(f"[!] Critical error for {url}: {str(e)}. Check execution log.")
                logging.error(f"Error scraping {url}: {str(e)}")

        if not news_data_raw:
            print("\n[!] No articles were successfully scraped from any source.")
            print("[!] Please check your internet connection or the provided URLs.")
            return

        if failed_urls:
            print(f"\n[!] Finished with errors. {len(failed_urls)} sources failed. See logs for details.")

        print(f"\n[+] Total articles successfully scraped: {len(news_data_raw)}")

        # Step 3: Save Raw Data to 'raw data' folder
        raw_path = save_to_excel(news_data_raw, subfolder="raw data", filename="daily_ai_news[raw]")
        print(f"[+] Raw data saved locally: {raw_path}")

        # Step 4: Clean Data and Save to 'cleaned' folder
        news_data_cleaned = []
        for row in news_data_raw:
            news_data_cleaned.append([
                clean_html(row[0]), # Title
                row[1],             # Date
                row[2],             # Source
                row[3],             # Link
                clean_html(row[4])  # Summary
            ])
        
        cleaned_path = save_to_excel(news_data_cleaned, subfolder="cleaned", filename="daily_ai_news[cleaned]")
        print(f"[+] Cleaned data saved locally: {cleaned_path}")
        logging.info(f"Saved cleaned data to: {cleaned_path}")

        # Step 5: Optional Google Sheets Sync
        if sync_sheets:
            print("[*] Synchronizing with Google Sheets...")
            try:
                upload_to_google_sheets(news_data_cleaned)
                print("[+] Google Sheets sync complete.")
                logging.info("Uploaded to Google Sheets")
            except Exception as e:
                print(f"[!] Google Sheets sync failed: {str(e)}")
                if "credentials.json" in str(e) or not os.path.exists("credentials.json"):
                    print(GOOGLE_SHEETS_GUIDE)
                else:
                    print("[!] Ensure 'credentials.json' is present and API is enabled.")
                logging.error(f"Sheets sync error: {str(e)}")

        print("\n[-] Workflow complete. Check 'logs/execution.log' for details.")

    except KeyboardInterrupt:
        print("\n[!] Process interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {str(e)}")
        logging.error(f"Main loop error: {str(e)}")

    logging.info("Script finished")


if __name__ == "__main__":
    main()
