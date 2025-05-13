import sqlite3
from datetime import datetime

DB_PATH = "polls.db"

# Function to init database
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_polls (
                id INTEGER PRIMARY KEY,
                chat_id TEXT,
                question TEXT,
                options TEXT,
                send_time TEXT        
            )          
        """)
        conn.commit()

# Function to add the row (poll)
def add_poll(chat_id, user_poll_config):
    question, options, send_time = user_poll_config

    print("Adding poll to ", chat_id, " with details of", 
        "\nquestion = ", question,
        "\noptions = ", options,
        "\nsend_time = ", send_time
    )
    # with sqlite3.connect(DB_PATH) as conn:
    #     conn.execute("""
    #         INSERT INTO scheduled_polls (chat_id, question, options, send_time)
    #         VALUES (?, ?, ?, ?)
    #     """, (chat_id, question, json.dumps(options), send_time))
    #     conn.commit()

# Function to get all poll send now
def get_due_polls():
    now = datetime.now().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT id, chat_id, question, options FROM scheduled_polls
            WHERE send_time <= ?
        """, (now,))
        return cursor.fetchall()

# Function to remove the poll
def remove_poll(poll_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM scheduled_polls WHERE id = ?", (poll_id,))
        conn.commit()

# Function to check due polls
def check_due_polls():
    for poll in get_due_polls():
        poll_id, chat_id, question, options = poll # Get poll detail
        options = json.loads(options)
        bot.send_poll(chat_id=chat_id, 
                      question=question, 
                      options=options, 
                      is_anonymous=False
        )
        remove_poll(poll_id) # remove when poll send