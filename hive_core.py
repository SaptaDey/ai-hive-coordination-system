import sqlite3
import json
import time
import uuid
import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HiveCore")

class MessageType(Enum):
    TASK_ASSIGNMENT = "TASK_ASSIGNMENT"
    TASK_RESULT = "TASK_RESULT"
    STATUS_UPDATE = "STATUS_UPDATE"
    KNOWLEDGE_SHARE = "KNOWLEDGE_SHARE"
    SYSTEM_ALERT = "SYSTEM_ALERT"

class Message:
    def __init__(self, sender_id: str, receiver_id: str, msg_type: MessageType, content: Dict[str, Any], parent_msg_id: str = None):
        self.id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.msg_type = msg_type
        self.content = content
        self.parent_msg_id = parent_msg_id
        self.timestamp = time.time()

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "msg_type": self.msg_type.value,
            "content": self.content,
            "parent_msg_id": self.parent_msg_id,
            "timestamp": self.timestamp
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        msg = Message(data['sender_id'], data['receiver_id'], MessageType(data['msg_type']), data['content'], data['parent_msg_id'])
        msg.id = data['id']
        msg.timestamp = data['timestamp']
        return msg


class SharedMemory:
    def __init__(self, db_path="hive_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                role TEXT,
                supervisor_id TEXT,
                capabilities TEXT,
                status TEXT DEFAULT 'IDLE',
                session_id TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                description TEXT,
                assigned_to TEXT,
                status TEXT,
                priority INTEGER,
                dependencies TEXT,
                result TEXT,
                created_at REAL,
                completed_at REAL,
                namespace TEXT,
                session_id TEXT,
                progress INTEGER DEFAULT 0,
                output_path TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                action TEXT,
                details TEXT,
                timestamp REAL,
                namespace TEXT,
                session_id TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                session_id TEXT
            )
        ''')
        self.conn.commit()
        self._migrate_schema()

    def _migrate_schema(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN progress INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN output_path TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN session_id TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS system_state (key TEXT PRIMARY KEY, value TEXT, session_id TEXT)")
        except sqlite3.OperationalError:
            pass
        self.conn.commit()

    def register_agent(self, agent_id, role, supervisor_id, capabilities, session_id="default"):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO agents (id, role, supervisor_id, capabilities, status, session_id) VALUES (?, ?, ?, ?, 'IDLE', ?)",
                       (agent_id, role, supervisor_id, json.dumps(capabilities), session_id))
        self.conn.commit()

    def create_task(self, description, priority=1, deps=[], namespace="default", session_id="default"):
        task_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (id, description, assigned_to, status, priority, dependencies, created_at, namespace, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, description, None, "PENDING", priority, json.dumps(deps), time.time(), namespace, session_id))
        self.conn.commit()
        return task_id

    def get_pending_tasks(self, namespace="default", session_id="default"):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = 'PENDING' AND namespace = ? AND session_id = ? ORDER BY priority DESC", (namespace, session_id))
        return cursor.fetchall()

    def assign_task(self, task_id, agent_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET assigned_to = ?, status = 'IN_PROGRESS' WHERE id = ?", (agent_id, task_id))
        self.conn.commit()

    def complete_task(self, task_id, result):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'COMPLETED', result = ?, completed_at = ? WHERE id = ?", (json.dumps(result), time.time(), task_id))
        self.conn.commit()

    def log_action(self, agent_id, action, details, namespace="default", session_id="default"):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO logs (agent_id, action, details, timestamp, namespace, session_id) VALUES (?, ?, ?, ?, ?, ?)", 
                            (agent_id, action, json.dumps(details), time.time(), namespace, session_id))
        self.conn.commit()

    def dump_memory(self, filepath):
        # Backup the database to a file
        with sqlite3.connect(filepath) as backup_conn:
            self.conn.backup(backup_conn)
        logger.info(f"Memory dumped to {filepath}")

    def prune_memory(self, days_to_keep=7):
        cutoff = time.time() - (days_to_keep * 86400)
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff,))
        cursor.execute("DELETE FROM tasks WHERE completed_at < ? AND status = 'COMPLETED'", (cutoff,))
        self.conn.commit()
        logger.info("Memory pruned.")

    def update_task_progress(self, task_id, progress, output_path=None):
        cursor = self.conn.cursor()
        if output_path:
            cursor.execute("UPDATE tasks SET progress = ?, output_path = ? WHERE id = ?", (progress, output_path, task_id))
        else:
            cursor.execute("UPDATE tasks SET progress = ? WHERE id = ?", (progress, task_id))
        self.conn.commit()

    def set_system_state(self, key, value, session_id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO system_state (key, value, session_id) VALUES (?, ?, ?)", (key, value, session_id))
        self.conn.commit()

    def get_system_state(self, key, session_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM system_state WHERE key = ? AND session_id = ?", (key, session_id))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_agents(self, session_id="default"):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, role, capabilities, status FROM agents WHERE session_id = ?", (session_id,))
        return cursor.fetchall()

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, agent_id: str, callback: Callable):
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    def publish(self, message: Message):
        # Direct delivery
        if message.receiver_id in self.subscribers:
            for callback in self.subscribers[message.receiver_id]:
                callback(message)
        self.process_message(message)

    def process_message(self, message: Message):
        # Override in subclasses
        pass

class BaseAgent:
    def __init__(self, name: str, role: str, shared_memory: SharedMemory, message_bus: MessageBus, supervisor_id: str = None, session_id: str = "default"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.memory = shared_memory
        self.bus = message_bus
        self.supervisor_id = supervisor_id
        self.session_id = session_id
        self.subordinates = []
        self.capabilities = []
        
        # Register self
        self.memory.register_agent(self.id, self.role, self.supervisor_id, self.capabilities, self.session_id)
        self.bus.subscribe(self.id, self.receive_message)
        
        logger.info(f"Agent {self.name} ({self.role}) initialized. ID: {self.id} Session: {self.session_id}")

    def receive_message(self, message: Message):
        logger.info(f"{self.name} received {message.msg_type.value} from {message.sender_id}")
        self.process_message(message)

    def process_message(self, message: Message):
        # Override in subclasses
        pass

    def send_message(self, receiver_id: str, msg_type: MessageType, content: Dict[str, Any]):
        msg = Message(self.id, receiver_id, msg_type, content)
        self.bus.publish(msg)

    def log(self, action: str, details: Any):
        self.memory.log_action(self.id, action, details, session_id=self.session_id)
