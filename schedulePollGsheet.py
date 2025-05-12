import gspread
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# ==== ENV ====
load_dotenv()
SB_CHAT_ID = os.getenv("CHAT_ID")
SB_TOPIC_ID = os.getenv("TOPIC_ID")

# ==== CONFIGURATION ====
SHEET_NAME = "Gsimo Bot Test"
CREDENTIALS_FILE = "credentials.json"  # Path to your service account file

# ==== INIT GOOGLE SHEET ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(credentials)

# Create or open the sheet
def get_sheet():
    try:
        return client.open(SHEET_NAME).sheet1
    except gspread.SpreadsheetNotFound:
        sheet = client.create(SHEET_NAME).sheet1
        sheet.append_row(["ID", "Chat ID", "Topic ID", "Question", "Options", "Send Time"])
        return sheet
    
# ==== ADD POLL ====
def add_poll(poll_config):
    sheet = get_sheet()
    question = poll_config["question"]
    options = json.dumps(poll_config["options"])
    send_time = poll_config["time"].isoformat()
    
    next_id = len(sheet.get_all_values())
    sheet.append_row([next_id, str(SB_CHAT_ID), str(SB_TOPIC_ID), question, options, send_time])
    print(f"Poll added to Google Sheet (row {next_id})")

# ==== GET DUE POLLS ====
def get_due_polls():
    now = datetime.now()
    sheet = get_sheet()
    rows = sheet.get_all_records()

    due = []
    for row in rows:
        try:
            send_time = datetime.fromisoformat(row["Send Time"])
            if send_time <= now:
                due.append(row)
                print('Due Poll', row)
        except Exception as e:
            print(f"Error parsing time in row: {row} — {e}")
    return due

# ==== REMOVE POLL (by ID) ====
def remove_poll(poll_id):
    sheet = get_sheet()
    all_values = sheet.get_all_values()
    for i, row in enumerate(all_values):
        if i == 0:
            continue  # Skip header
        if row[0] == str(poll_id):
            sheet.delete_rows(i + 1)
            print(f"Removed poll ID {poll_id}")
            break

# ==== CHECK DUE POLLS AND SEND ====
def check_due_polls(bot):
    print("I'm checking!")
    for row in get_due_polls():
        chat_id = row["Chat ID"]
        topic_id = row["Topic ID"]
        question = row["Question"]
        options = json.loads(row["Options"])
        poll_id = row["ID"]

        bot.send_poll(chat_id=chat_id, 
                      message_thread_id=topic_id,
                      question=question, 
                      options=options, 
                      is_anonymous=False
                    )
        # remove_poll(poll_id)