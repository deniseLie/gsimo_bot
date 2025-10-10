import gspread
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from gsheetConfig import gc, SHEET_NAME
from gspread_formatting import get_effective_format, format_cell_range, CellFormat, Color

HIGHLIGHT_COLOR = Color(red=0.8, green=1, blue=0.8)  # Light green

# Create or open the sheet 1
def get_sheet1():
    try:
        sheet = gc.open(SHEET_NAME)
        print("Title:", sheet.title)
        print("Worksheets:", [ws.title for ws in sheet.worksheets()])

        return sheet.worksheet("Scheduled")
    
    except gspread.SpreadsheetNotFound:
        # Spreadsheet doesn't exist, create it
        print("Spreadsheet doesn't exist")

    #     sheet = gc.create(SHEET_NAME)
    #     ws = sheet.sheet1
    #     ws.update_title("Scheduled")  # Rename default "Sheet1" to "Scheduled"
    #     ws.append_row(["ID", "Chat ID", "Topic ID", "Question", "Options", "Scheduled Time"])
    #     return ws
    
    except gspread.exceptions.WorksheetNotFound:
        # Spreadsheet exists but "Scheduled" worksheet doesn't — create it
        print("worksheet doesn't exist")

        ws = sheet.add_worksheet(title="Scheduled", rows="100", cols="10")
        ws.append_row(["ID", "Chat ID", "Topic ID", "Question", "Options", "Scheduled Time"])
        return ws

# ==== GET DUE POLLS ====
def get_due_polls():
    now_sgt = datetime.now(ZoneInfo("Asia/Singapore"))
    sheet = get_sheet1()
    records = sheet.get_all_records()
    # print("Records : ", records)
    print("now ", now_sgt)

    due = []
    for i, row in enumerate(records, start=2):
        try:
            if(row["Scheduled Time"]):
                scheduled_time_str = row["Scheduled Time"]
                send_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")
                send_time = send_time.replace(tzinfo=ZoneInfo("Asia/Singapore"))
                print("send time ", send_time)
            
        except Exception as e:
            print(f"Error parsing time in row: {row} — {e}")

        # Skip if background color is already set
        fmt = get_effective_format(sheet, f"A{i}")  # Get the format of cell A{i} (e.g., A2, A3, ...)
        bg = fmt.backgroundColor if fmt else None   # Get the background color if the format exists
        if bg and not (bg.red == 1.0 and bg.green == 1.0 and bg.blue == 1.0): # If colored, skipped
            print("Skip cuz colored")
            continue
            
        if send_time <= now_sgt:
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

        try: 
            bot.send_poll(chat_id=chat_id, 
                        message_thread_id=topic_id,
                        question=question, 
                        options=options, 
                        is_anonymous=False
                        )
                
            # Highlight the row (set background color)
            highlight_row(sheet_row_index)
        except Exception as e:
            print("send poll fail to chat_id : ", chat_id)
        
        
    
# ==== HIGHLIGHT USED ROW ====
def highlight_row(sheet_row_index):
    sheet = get_sheet1()

    format_cell_range(
            sheet,
            f"A{sheet_row_index}:F{sheet_row_index}",
            CellFormat(backgroundColor=HIGHLIGHT_COLOR)
        )