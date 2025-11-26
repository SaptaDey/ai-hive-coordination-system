import sqlite3
import uuid
import time

DB_PATH = "hive_memory.db"

def inject_citation_task():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    task_id = str(uuid.uuid4())
    desc = "Cite sources for CRISPR-Cas9 gene editing mechanisms"
    
    print(f"Injecting Citation Task: {desc}")
    
    cursor.execute('''
        INSERT INTO tasks (id, description, assigned_to, status, priority, dependencies, created_at, namespace)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (task_id, desc, None, "PENDING", 5, "[]", time.time(), "default"))
        
    conn.commit()
    conn.close()
    print("Injection complete.")

if __name__ == "__main__":
    inject_citation_task()
