import os
import gspread
import json
from google.oauth2.service_account import Credentials
# from oauth2client.service_account import ServiceAccountCredentials, Credentials

# ==== CONFIGURATION ====
SHEET_NAME = "Gsimo Telebot Database"
credentials_str = os.getenv("google_api_credentials.json")  # default fallback for local dev
credentials_dict = json.loads(credentials_str, strict=False)

# Local Test
# with open("gcredential.json", "r") as f:
#     credentials_dict = json.load(f)

# LOG
# print("Looking for credentials:", credentials_dict)
# print("Exists?", os.path.exists(CREDENTIALS))

# ==== INIT GOOGLE SHEET ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# json_key = json.loads(CREDENTIALS, strict=False)
# credentials = Credentials.from_service_account_file(CREDENTIALS, scopes=scope)
credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
# print('this is my credentials : ', credentials)

gc = gspread.authorize(credentials)

# print('this is my google c: ', gc)
# List all spreadsheets the service account has access to
# try:
#     files = gc.openall()
#     print("✅ Accessible spreadsheets:")
#     for f in files:
#         print("-", f.title)
# except Exception as e:
#     print("❌ Could not list spreadsheets:", e)