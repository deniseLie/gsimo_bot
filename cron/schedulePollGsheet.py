import gspread
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from gsheetConfig import client, SHEET_NAME
from gspread_formatting import get_effective_format, format_cell_range, CellFormat, Color

# ==== ENV ====
load_dotenv()
SB_CHAT_ID = os.getenv("CHAT_ID")
SB_TOPIC_ID = os.getenv("TOPIC_ID")

HIGHLIGHT_COLOR = Color(red=0.8, green=1, blue=0.8)  # Light green

# Create or open the sheet 1
def get_sheet1():
    try:
        return client.open(SHEET_NAME).worksheet("Scheduled")
    except gspread.SpreadsheetNotFound:
        sheet = client.create(SHEET_NAME).sheet1
        sheet.append_row(["ID", "Chat ID", "Topic ID", "Question", "Options", "Scheduled Time"])
        return sheet

# ==== GET DUE POLLS ====
def get_due_polls():
    now = datetime.now()
    sheet = get_sheet1()
    records = sheet.get_all_records()

    due = []
    for i, row in enumerate(records, start=2):
        try:
            send_time = datetime.fromisoformat(row["Scheduled Time"])
            print("send time ", send_time)
            
        except Exception as e:
            print(f"Error parsing time in row: {row} — {e}")

        # Skip if background color is already set
        fmt = get_effective_format(sheet, f"A{i}")  # Get the format of cell A{i} (e.g., A2, A3, ...)
        bg = fmt.backgroundColor if fmt else None   # Get the background color if the format exists
        if bg and not (bg.red == 1.0 and bg.green == 1.0 and bg.blue == 1.0): # If colored, skipped
            print("Skip cuz colored")
            continue
            
        if send_time <= now:
            row["_row_index"] = i  # track row number for formatting
            due.append(row)
            print('Due Poll', row)
    return due

# ==== CHECK DUE POLLS AND SEND ====
def check_due_polls(bot):
    print("I'm checking!")
    due_rows = get_due_polls()

    for row in due_rows:
        chat_id = row["Chat ID"]
        topic_id = row["Topic ID"]
        question = row["Question"]
        options = json.loads(row["Options"])
        sheet_row_index = row["_row_index"]

        bot.send_poll(chat_id=chat_id, 
                      message_thread_id=topic_id,
                      question=question, 
                      options=options, 
                      is_anonymous=False
                    )
        
        # Highlight the row (set background color)
        highlight_row(sheet_row_index)
    
# ==== HIGHLIGHT USED ROW ====
def highlight_row(sheet_row_index):
    sheet = get_sheet1()

    format_cell_range(
            sheet,
            f"A{sheet_row_index}:F{sheet_row_index}",
            CellFormat(backgroundColor=HIGHLIGHT_COLOR)
        )