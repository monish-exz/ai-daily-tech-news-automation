# Import required functions from project modules
from src.scraper.news_scraper import scrape_all_websites
from src.utils.excel_handler import save_to_excel
from src.sheets.google_sheets import upload_to_google_sheets
from src.utils.logger import setup_logger

import logging
import schedule
import time


# This function runs the complete news automation process
def job():
    logging.info("Scheduled job started")

    try:
        # Scrape AI news articles
        news_data = scrape_all_websites()
        logging.info(f"Scraped {len(news_data)} articles")

        # Save data to Excel
        save_to_excel(news_data)
        logging.info("Saved data to Excel")

        # Upload data to Google Sheets
        upload_to_google_sheets(news_data)
        logging.info("Uploaded data to Google Sheets")

    except Exception as e:
        logging.error(str(e))

    logging.info("Scheduled job finished")


# Entry point for scheduled execution
if __name__ == "__main__":
    # Setup logging once
    setup_logger()
    logging.info("Scheduler started")

    # Schedule the job to run every day at 9:00 AM
    schedule.every().day.at("09:00").do(job)

    # Keep the script running to check scheduled time
    while True:
        schedule.run_pending()  # Runs job if time matches
        time.sleep(60)          # Wait for 1 minute
