import sqlite3
import time
from nostr_bot.config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS timestamps
                 (event_id TEXT PRIMARY KEY,
                  initial_reply_id TEXT,
                  ots_data TEXT,
                  upgraded INTEGER DEFAULT 0,
                  last_upgrade_attempt INTEGER,
                  created_at INTEGER)''')
    conn.commit()
    conn.close()

def save_timestamp(event_id, initial_reply_id, ots_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = int(time.time())
    c.execute('''INSERT OR REPLACE INTO timestamps
                 (event_id, initial_reply_id, ots_data, upgraded, last_upgrade_attempt, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (event_id, initial_reply_id, ots_data, 0, now, now))
    conn.commit()
    conn.close()

def get_pending_upgrades():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT event_id, initial_reply_id, ots_data FROM timestamps WHERE upgraded = 0')
    rows = c.fetchall()
    conn.close()
    return rows

def mark_as_upgraded(event_id, upgraded_ots_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE timestamps SET upgraded = 1, ots_data = ? WHERE event_id = ?',
              (upgraded_ots_data, event_id))
    conn.commit()
    conn.close()

def update_last_attempt(event_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = int(time.time())
    c.execute('UPDATE timestamps SET last_upgrade_attempt = ? WHERE event_id = ?',
              (now, event_id))
    conn.commit()
    conn.close()
