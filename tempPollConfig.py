import gspread
import json
from datetime import datetime
from gsheetConfig import client, SHEET_NAME

# Create or open the sheet 2
def get_sheet2():
    try:
        return client.open(SHEET_NAME).worksheet("Temp Msg")
    except gspread.SpreadsheetNotFound:
        sheet = client.create(SHEET_NAME).worksheet("Temp Msg")
        sheet.append_row(["chat_id", "Question", "Options", "Scheduled Time"])
        return sheet

# ==== GET TEMP POLL CONFIG ====
def get_user_poll_config(chat_id):
    sheet = get_sheet2()
    records = sheet.get_all_records()

    for row in records:
        if int(row['chat_id']) == chat_id:
            return {
                "question": row["Question"],
                "options": json.loads(row["Options"]),
                "time": datetime.strptime(row["Scheduled Time"], "%Y-%m-%d %H:%M:%S")
            }
    return None

# ==== UPDATE TEMP POLL CONFIG ====
def update_user_poll_config(chat_id, question=None, options=None, time=None):
    sheet = get_sheet2()
    records = sheet.get_all_records()
    
    # Find existing config row
    for i, row in enumerate(records, start=2):  # row 2 onwards
        if int(row['chat_id']) == chat_id:
            print("Found chatId : ", chat_id)
            
            if question: sheet.update_cell(i, 2, question)
            if options:  sheet.update_cell(i, 3, json.dumps(options))
            if time:     sheet.update_cell(i, 4, time.strftime("%Y-%m-%d %H:%M:%S"))
            return

    # Insert new row if not found
    sheet.append_row([
        chat_id,
        question or "",
        json.dumps(options) if options else "[]",
        time.strftime("%Y-%m-%d %H:%M:%S") if time else ""
    ])

# ==== DELETE TEMP POLL CONFIG ====
def delete_user_poll_config(chat_id):
    sheet = get_sheet2()
    records = sheet.get_all_records()

    for i, row in enumerate(records, start=2):
        if int(row['chat_id']) == chat_id:
            sheet.delete_rows(i)
            break