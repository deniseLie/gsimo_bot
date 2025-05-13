import os
from dotenv import load_dotenv
from telebot import TeleBot
from .schedulePollGsheet import check_due_polls

# ===== ENV =====
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== SETUP TELEGRAM BOT =====
bot = TeleBot(BOT_TOKEN)

def run_cron_job():
    print("Running scheduled poll check")
    check_due_polls(bot)

if __name__ == "__main__":
    run_cron_job()
