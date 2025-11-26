import sqlite3
import uuid
import time
import json

DB_PATH = "hive_memory.db"

def inject_load():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tasks = [
        ("Analyze Massive Dataset A", 5),
        ("Analyze Massive Dataset B", 5),
        ("Analyze Massive Dataset C", 5),
        ("Design Microservices Architecture", 4),
        ("Implement Auth Service", 3),
        ("Implement Payment Service", 3),
        ("Implement User Service", 3),
        ("Test Auth Service", 2),
        ("Test Payment Service", 2),
        ("Test User Service", 2),
        ("Research Quantum Algorithms", 5),
        ("Research Blockchain Integration", 5),
        ("Optimize Database Queries", 4),
        ("Refactor Legacy Codebase", 3),
        ("Security Audit", 5)
    ]
    
    print(f"Injecting {len(tasks)} new tasks to trigger Auto-Scaling...")
    
    for desc, priority in tasks:
        task_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO tasks (id, description, assigned_to, status, priority, dependencies, created_at, namespace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, desc, None, "PENDING", priority, "[]", time.time(), "default"))
        
    conn.commit()
    conn.close()
    print("Injection complete.")

if __name__ == "__main__":
    inject_load()
