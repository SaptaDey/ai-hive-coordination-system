import sqlite3
import uuid
import time
import json

DB_PATH = "hive_memory.db"

def inject_scientific_load():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tasks = [
        ("Visualize Experimental Data Set X", 5),
        ("Create 3D Graph of Neural Patterns", 4),
        ("Perform Statistical Analysis on User Behavior", 5),
        ("Calculate Variance and Standard Deviation", 3),
        ("Document API Endpoints for Reproducibility", 4),
        ("Create Scientific Report for Project Alpha", 5)
    ]
    
    print(f"Injecting {len(tasks)} scientific tasks...")
    
    for desc, priority in tasks:
        task_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO tasks (id, description, assigned_to, status, priority, dependencies, created_at, namespace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, desc, None, "PENDING", priority, "[]", time.time(), "default"))
        
    conn.commit()
    conn.close()
    print("Scientific Injection complete.")

if __name__ == "__main__":
    inject_scientific_load()
