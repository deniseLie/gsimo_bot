import os
import threading
import schedule
import time
import re
from dotenv import load_dotenv
from telebot import TeleBot, types
from datetime import datetime
from schedulePollGsheet import add_poll, check_due_polls

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Set up Telegram Bot
bot = TeleBot(BOT_TOKEN)

user_poll_config = {}

# Get Topic Info
# @bot.message_handler(func=lambda message: True)
# def get_topic_info(message):
#     print("Chat ID:", message.chat.id)
#     print("Topic ID:", message.message_thread_id)

# Schedule Poll Handler 
@bot.message_handler(commands=['schedule_poll'])
def schedule_poll(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please enter scheduled date and time (e.g. 2025-05-12 08:00)")
    bot.register_next_step_handler(message, handle_schedule_time)
    

# Function to schedule poll
def handle_schedule_time(message):
    chat_id= message.chat.id
    input_text = message.text.strip()

    # Regex pattern: 2025-05-12 08:00
    if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", input_text):
        bot.send_message(chat_id, "❌ Format looks wrong. Use this format: `YYYY-MM-DD HH:MM` (e.g., 2025-05-12 08:00)")
        return bot.register_next_step_handler(message, handle_schedule_time)

    # Try to parse input into datetime object
    try: 
        target_datetime = datetime.strptime(input_text, "%Y-%m-%d %H:%M")
        user_poll_config[chat_id] = {
            "question": "Practice tomorrow!",
            "options": ["Alto 1", "Alto 2", "Prime", "Bass", "Contrabass", "Guitarron", "Not coming (rmb to inform @varidhig)"],
            "time": target_datetime
        }

        # Markup settings
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✏️ Change Question", callback_data="change_question"))
        markup.add(types.InlineKeyboardButton("✏️ Change Options", callback_data="change_options"))
        markup.add(types.InlineKeyboardButton("✏️ Change Timing", callback_data="change_timing"))
        markup.add(types.InlineKeyboardButton("✅ Confirm", callback_data="confirm_poll"))
        
        bot.send_message(chat_id, format_poll_summary(chat_id), reply_markup=markup) # send summary (assume only for attendance)
        
    except ValueError:
        # If input is not in the correct format, ask the user to retry
        bot.send_message(chat_id, "❌ Invalid format. Please enter the date and time in the format: YYYY-MM-DD HH:MM.")
        bot.register_next_step_handler(message, handle_schedule_time)

# Function to format poll summary
def format_poll_summary(chat_id):
    poll = user_poll_config[chat_id]
    options_text = "\n".join(f"- {opt}" for opt in poll["options"])
    time_text = poll["time"].strftime("%Y-%m-%d %H:%M")
    return (
        f"🗳 **Poll Summary**\n\n"
        f"*Question:* {poll['question']}\n"
        f"*Options:*\n{options_text}\n"
        f"*Scheduled Time:* {time_text}"
    )

# Callback handler poll question and options
@bot.callback_query_handler(func=lambda call: True)
def handle_poll_callbacks(call):
    chat_id = call.message.chat.id
    if call.data == "change_question":
        bot.send_message(chat_id, "Please send me the new question")
        bot.register_next_step_handler(call.message, handle_new_question)

    elif call.data == "change_options":
        bot.send_message(chat_id, "Please send new options separated by commas (e.g. Alto, Prime, Bass).")
        bot.register_next_step_handler(call.message, handle_new_options)

    elif call.data == "confirm_poll":
        print("Poll confirmed")
        add_poll(user_poll_config[chat_id])
        bot.send_message(chat_id, "✅ Poll scheduled!")

# Function to change new question
def handle_new_question(message):
    chat_id = message.chat.id
    user_poll_config[chat_id]["question"] = message.text
    schedule_poll(message)  # Re-show summary

# Function to handle new option
def handle_new_options(message):
    chat_id = message.chat.id
    options = [opt.strip() for opt in message.text.split(",") if opt.strip()]
    if len(options) < 2:
        bot.send_message(chat_id, "❌ Please provide at least two options.")
        return schedule_poll(message)
    user_poll_config[chat_id]["options"] = options
    schedule_poll(message)  # Re-show summary

# ======= SCHEDULER =======
# Background scheduler loop
def run_scheduler():

    # Schedule the poll check every minute
    schedule.every(1).minutes.do(lambda: check_due_polls(bot)) 

    while True:

        # Get the current time and the next scheduled time
        next_run_timestamp = schedule.next_run().timestamp()
        current_run_timestamp = time.time() # current in seconds

        # calculate the time difference to the next scheduled run
        time_diff = (next_run_timestamp - current_run_timestamp)
        print("time_diff ", time_diff)

        # Sleep if time_diff is positive, otherwise run immediately
        if time_diff > 0:
            time.sleep(time_diff)

        # Run the scheduled tasks 
        print("Running pending scheduled")
        schedule.run_pending()    
        
# Start scheduler in a seperate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Start bot polling loop
bot.infinity_polling()