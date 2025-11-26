import sqlite3
import uuid
import time
import sys

DB_PATH = "hive_memory.db"

def get_current_session():
    try:
        with open("current_session.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: Hive not running (current_session.txt not found).")
        sys.exit(1)

def inject_tasks(tasks, scenario_name):
    session_id = get_current_session()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\n=== INJECTING SCENARIO: {scenario_name} ===")
    print(f"Session ID: {session_id}")
    print(f"Injecting {len(tasks)} tasks...")
    
    for desc, priority in tasks:
        task_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO tasks (id, description, assigned_to, status, priority, dependencies, created_at, namespace, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, desc, None, "PENDING", priority, "[]", time.time(), scenario_name, session_id))
        
    conn.commit()
    conn.close()
    print("Injection complete. Monitor the Dashboard to see the Hive react.")

def scenario_alien_signal():
    tasks = [
        ("Research unknown radio signal from Sector 7G", 5),
        ("Analyze signal frequency and modulation patterns", 5),
        ("Visualize signal spectrogram and waveform", 4),
        ("Code decryption algorithm for signal", 5),
        ("Test decryption algorithm on sample data", 4),
        ("Document initial findings and hypothesis", 3),
        ("Cite astronomical references for signal type", 3),
        ("Research linguistic patterns in signal", 4),
        ("Analyze potential mathematical constructs", 5),
        ("Visualize 3D source triangulation", 4)
    ]
    inject_tasks(tasks, "Alien_Signal_Decoding")

def scenario_pandemic_response():
    tasks = [
        ("Research viral transmission vectors", 5),
        ("Analyze infection rate data from Region A", 5),
        ("Analyze infection rate data from Region B", 5),
        ("Analyze infection rate data from Region C", 5),
        ("Visualize global spread heatmap", 5),
        ("Perform statistical modeling of R0 value", 5),
        ("Document public health guidelines", 5),
        ("Cite epidemiological studies", 5),
        ("Code contact tracing application backend", 4),
        ("Design contact tracing app UI", 3),
        ("Test contact tracing app security", 5)
    ]
    inject_tasks(tasks, "Pandemic_Response")

def scenario_startup_sprint():
    tasks = []
    # High volume of coding/testing
    for i in range(10):
        tasks.append((f"Design Microservice {i}", 3))
        tasks.append((f"Code Microservice {i} Implementation", 4))
        tasks.append((f"Test Microservice {i} API", 4))
    
    tasks.append(("Document System Architecture", 5))
    tasks.append(("Visualize System Topology", 3))
    inject_tasks(tasks, "Startup_Sprint")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scenario_runner.py [alien|pandemic|startup]")
    else:
        mode = sys.argv[1]
        if mode == "alien": scenario_alien_signal()
        elif mode == "pandemic": scenario_pandemic_response()
        elif mode == "startup": scenario_startup_sprint()
        else: print("Unknown scenario")
