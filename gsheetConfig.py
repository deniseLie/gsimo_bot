import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==== CONFIGURATION ====
SHEET_NAME = "Gsimo Bot Test"
CREDENTIALS_FILE = "credentials.json"  # Path to your service account file

# ==== INIT GOOGLE SHEET ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(credentials)