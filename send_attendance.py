import os
import logging
import json
import schedule
import time
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from telebot import TeleBot
# from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, PollAnswerHandler

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Set up Telegram bot
bot = TeleBot(BOT_TOKEN)
# updater = Updater(token=BOT_TOKEN, use_context=True)
# dispatcher = updater.dispatcher

# Attendance options
options = ['Group 1', 'Group 2', 'Group 3']

# Configure logging
# logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Function for /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Wassup!")

# User Input handler
@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.reply_to(message, message.text)

# Start bot
bot.infinity_polling()

# # Function to send a poll
@bot.message_handler(commands=['start', 'help'])
def send_attendance_poll(context: CallbackContext):
    bot.send_poll(
        chat_id=CHAT_ID,
        question="Practice for tomorrow",
        options=options,
        allows_multiple_answers=False,
        is_anonymous=False
    )
    logging.info("Attendance poll sent.")

# # Command to manually send a poll
# def send_poll_command(update: Update, context: CallbackContext):
#     send_attendance_poll(context)
#     update.message.reply_text("Attendance poll sent!")

# # Schedule poll at a specific time
# def schedule_poll_command(update: Update, context: CallbackContext):
#     if len(context.args) != 1:
#         update.message.reply_text("Usage: /schedule_poll HH:MM (24-hour format)")
#         return

#     time_pattern = context.args[0]

#     # Validate time format
#     try:
#         schedule.every().day.at(time_pattern).do(send_attendance_poll, context)
#         update.message.reply_text(f"Poll scheduled daily at {time_pattern}.")
#         logging.info(f"Poll scheduled at {time_pattern}.")
#     except:
#         update.message.reply_text("Invalid time format! Use HH:MM (24-hour format).")

# # Receive poll answers
# def retrieve_result(update: Update, context: CallbackContext):
#     poll_answer = update.poll_answer
#     user_id = poll_answer.user.id
#     user_name = f"{poll_answer.user.first_name} {poll_answer.user.last_name or ''}".strip()
#     option_chosen = options[poll_answer.option_ids[0]]

#     logging.info(f"User {user_name} ({user_id}) chose: {option_chosen}")

#     # Send data to Google Sheets
#     send_to_google_sheets(user_name, option_chosen)

# # Send poll data to Google Sheets
# def send_to_google_sheets(user_name, section):
#     try:
#         creds = Credentials.from_service_account_file(
#             GOOGLE_CREDENTIALS_PATH,
#             scopes=["https://www.googleapis.com/auth/spreadsheets"]
#         )
#         client = gspread.authorize(creds)
#         sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("Attendance")

#         # Append the data
#         sheet.append_row([time.strftime("%Y-%m-%d %H:%M:%S"), user_name, section])
#         logging.info("Attendance recorded in Google Sheets.")
#     except Exception as e:
#         logging.error(f"Error sending to Google Sheets: {e}")

# # Register command handlers
# dispatcher.add_handler(CommandHandler("send_poll", send_poll_command))
# dispatcher.add_handler(CommandHandler("schedule_poll", schedule_poll_command, pass_args=True))
# dispatcher.add_handler(PollAnswerHandler(retrieve_result))

# # Start bot
# if __name__ == "__main__":
#     updater.start_polling()
#     logging.info("Bot started. Listening for commands...")

#     while True:
#         schedule.run_pending()
#         time.sleep(1)
