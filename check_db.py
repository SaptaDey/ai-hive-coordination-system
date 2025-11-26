import sqlite3
import os

if not os.path.exists("current_session.txt"):
    print("current_session.txt not found")
    exit()

with open("current_session.txt", "r") as f:
    session_id = f.read().strip()

print(f"Checking DB for Session ID: {session_id}")

conn = sqlite3.connect("hive_memory.db")
c = conn.cursor()

c.execute("SELECT count(*) FROM agents WHERE session_id = ?", (session_id,))
print(f"Agents count: {c.fetchone()[0]}")

c.execute("SELECT count(*) FROM tasks WHERE session_id = ?", (session_id,))
print(f"Tasks count: {c.fetchone()[0]}")

c.execute("SELECT * FROM tasks WHERE session_id = ? LIMIT 1", (session_id,))
print(f"Sample Task: {c.fetchone()}")

conn.close()
