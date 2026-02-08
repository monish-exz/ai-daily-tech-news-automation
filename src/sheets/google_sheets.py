"""
Google Sheets integration for the universal scraper.
Updates the 'Daily AI News' sheet with the latest data.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import logging

def upload_to_google_sheets(news_data):
    """
    Uploads news data to Google Sheets using bulk operations.
    """
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("Google API 'credentials.json' not found in root directory.")

    # Required permissions for Google Sheets & Drive
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Load service account credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    # Authorize Google Sheets client
    client = gspread.authorize(creds)

    try:
        # Open the Google Sheet
        workbook = client.open("Daily AI News")
        sheet = workbook.sheet1

        # Clear old data before adding new data
        sheet.clear()

        # Add header row
        headers = ["Title", "Date", "Source", "Link", "Summary"]
        sheet.append_row(headers)

        # Bulk append rows for efficiency
        if news_data:
            sheet.append_rows(news_data)

    except Exception as e:
        logging.error(f"Failed to upload to Google Sheets: {str(e)}")
        raise
