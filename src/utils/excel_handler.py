from openpyxl import Workbook
import os


# This function saves news data into an Excel file
def save_to_excel(news_data, subfolder="normal", filename="daily_ai_news"):
    # Create subfolder path
    base_dir = os.path.join("data", subfolder)
    os.makedirs(base_dir, exist_ok=True)

    # Excel file path
    file_path = os.path.join(base_dir, f"{filename}.xlsx")

    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "AI News"

    # Add column headers
    ws.append(["Title", "Date", "Source", "Link", "Summary"])

    # Add each news row to Excel
    for row in news_data:
        ws.append(row)

    # Auto-adjust column widths for better visibility
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        # Cap width at 100 for very long summaries
        adjusted_width = min(max_length + 2, 100)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save the Excel file
    wb.save(file_path)

    return file_path
