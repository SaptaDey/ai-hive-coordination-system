import time
import threading
import subprocess
import sys
import os
import signal
import atexit
import uuid
from hive_core import SharedMemory, MessageBus
from queen import QueenAgent

LOCK_FILE = "hive.lock"
DB_FILE = "hive_memory.db"

def cleanup(queen, memory, lock_file):
    print("\n[SYSTEM] Initiating Graceful Shutdown...")
    if queen:
        queen.stop()
    
    if memory:
        print("[SYSTEM] Dumping memory...")
        memory.dump_memory(f"memory_dump_{int(time.time())}.db")
        memory.prune_memory()
        
    if os.path.exists(lock_file):
        os.remove(lock_file)
    print("[SYSTEM] Hive Shutdown Complete. Bye! 🐝")

def run_simulation():
    # 1. Lock File Check
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            # Check if process exists (Windows specific)
            # This is a simple check; for robust cross-platform, psutil is better but we stick to stdlib
            try:
                os.kill(pid, 0)
                print(f"[ERROR] Hive is already running (PID: {pid}). Please stop it first.")
                sys.exit(1)
            except OSError:
                print("[SYSTEM] Stale lock file found. Overwriting.")
        except ValueError:
            print("[SYSTEM] Corrupt lock file found. Overwriting.")

    # Create Lock File
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

    # 2. Session Management
    session_id = str(uuid.uuid4())
    project_name = f"Project-Hive-{int(time.time())}"
    print(f"Initializing AI Hive System...")
    print(f"Project: {project_name}")
    print(f"Session ID: {session_id}")
    
    with open("current_session.txt", "w") as f:
        f.write(session_id)
    
    # Setup Infrastructure
    memory = SharedMemory(DB_FILE)
    bus = MessageBus()
    
    # Initialize Queen with Session ID
    queen = QueenAgent("Queen-Alpha", memory, bus, session_id=session_id)
    print("Queen Agent Online.")
    
    # Register Cleanup
    def signal_handler(sig, frame):
        cleanup(queen, memory, LOCK_FILE)
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup, queen, memory, LOCK_FILE)
    
    # Simulate Task Injection
    tasks = [
        "Design System Architecture for Web App",
        "Research Competitor Features",
        "Implement User Authentication Module",
        "Write Unit Tests for Auth Module",
        "Analyze Database Performance",
        "Design Frontend Layout",
        "Implement Dashboard UI",
        "Test Dashboard Responsiveness",
        "Research AI Integration Strategies",
        "Optimize API Latency"
    ]
    
    print(f"Injecting {len(tasks)} tasks...")
    
    for i, task_desc in enumerate(tasks):
        memory.create_task(task_desc, priority=1, session_id=session_id)
        time.sleep(0.5) # Stagger injection slightly
        
    print("Tasks injected. Monitoring system...")
    print("NOTE: Run 'python dashboard.py' to view the Hive Matrix in your browser.")
    
    try:
        while True:
            # Keep main thread alive
            time.sleep(1)
    except KeyboardInterrupt:
        # Handled by signal_handler
        pass

if __name__ == "__main__":
    run_simulation()
