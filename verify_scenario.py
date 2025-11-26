import sqlite3
import time

DB_PATH = "hive_memory.db"

def check_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n=== ALIEN SIGNAL SCENARIO STATUS ===")
    cursor.execute("SELECT description, assigned_to, status FROM tasks WHERE namespace='Alien_Signal_Decoding'")
    tasks = cursor.fetchall()
    for t in tasks:
        print(f"Task: {t[0][:40]}... | Agent: {t[1]} | Status: {t[2]}")
        
    print("\n=== RECENT LOGS ===")
    cursor.execute("SELECT action, details FROM logs ORDER BY timestamp DESC LIMIT 5")
    for l in cursor.fetchall():
        print(f"{l[0]}: {l[1]}")
        
    conn.close()

if __name__ == "__main__":
    check_status()
