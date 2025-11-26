import time
import random
import json
import os
from hive_core import BaseAgent, Message, MessageType

class WorkerAgent(BaseAgent):
    def process_message(self, message: Message):
        if message.msg_type == MessageType.TASK_ASSIGNMENT:
            self.handle_task(message)

    def handle_task(self, message: Message):
        task = message.content
        self.log("TASK_STARTED", f"Started task: {task['description']}")
        
        # Check for global pause
        while self.memory.get_system_state("status", self.session_id) == "PAUSED":
            time.sleep(1)
        
        try:
            # Simulate work with progress
            result_data = self.perform_work(task)
            
            # If perform_work returns a dict with output_path, use it
            output_path = None
            if isinstance(result_data, dict) and "output_path" in result_data:
                output_path = result_data["output_path"]
                result = result_data["status"]
            else:
                result = str(result_data)

            self.memory.complete_task(task['id'], result)
            if output_path:
                self.memory.update_task_progress(task['id'], 100, output_path)
            else:
                self.memory.update_task_progress(task['id'], 100)
                
            self.send_message(message.sender_id, MessageType.TASK_RESULT, {
                "task_id": task['id'],
                "status": "COMPLETED",
                "result": result
            })
            self.log("TASK_COMPLETED", f"Completed task: {task['description']}")
        except Exception as e:
            self.log("TASK_FAILED", f"Failed task: {str(e)}")
            self.send_message(message.sender_id, MessageType.TASK_RESULT, {
                "task_id": task['id'],
                "status": "FAILED",
                "error": str(e)
            })

    def perform_work(self, task):
        # Default implementation
        duration = random.uniform(2.0, 5.0)
        steps = 5
        for i in range(steps):
            time.sleep(duration / steps)
            progress = int(((i + 1) / steps) * 100)
            self.memory.update_task_progress(task['id'], progress)
        return f"Executed {task['description']}"

class ArchitectAgent(WorkerAgent):
    def perform_work(self, task):
        super().perform_work(task)
        return f"Designed architecture for {task['description']}"

class CoderAgent(WorkerAgent):
    def perform_work(self, task):
        super().perform_work(task)
        if random.random() < 0.1: raise Exception("Syntax Error in generated code")
        return f"Wrote code for {task['description']}"

class TesterAgent(WorkerAgent):
    def perform_work(self, task):
        super().perform_work(task)
        return f"Tested {task['description']} - All tests passed"

class AnalystAgent(WorkerAgent):
    def perform_work(self, task):
        super().perform_work(task)
        return f"Analyzed requirements for {task['description']}"

class ResearcherAgent(WorkerAgent):
    def perform_work(self, task):
        super().perform_work(task)
        if random.random() < 0.1: raise Exception("Source unavailable")
        return f"Gathered insights on {task['description']}"

class VisualizationAgent(WorkerAgent):
    def perform_work(self, task):
        # Simulate rendering with progress
        duration = random.uniform(2.0, 5.0)
        steps = 5
        for i in range(steps):
            time.sleep(duration / steps)
            progress = int(((i + 1) / steps) * 100)
            self.memory.update_task_progress(task['id'], progress)
            
        if random.random() < 0.1: raise Exception("Rendering artifact")
        
        # Generate dummy artifact
        filename = f"plot_{task['id']}.svg"
        output_dir = "static/outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filepath = os.path.join(output_dir, filename)
        
        # Create a simple SVG
        color = random.choice(["red", "green", "blue", "orange", "purple"])
        svg_content = f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#eee" />
            <circle cx="100" cy="100" r="80" fill="{color}" />
            <text x="100" y="100" font-family="Arial" font-size="20" text-anchor="middle" fill="white">{task['description'][:10]}</text>
        </svg>'''
        
        with open(filepath, "w") as f:
            f.write(svg_content)
            
        return {"status": "Visualized Data", "output_path": filepath}

class StatisticianAgent(WorkerAgent):
    def perform_work(self, task):
        super().perform_work(task)
        if random.random() < 0.1: raise Exception("Statistical anomaly")
        return f"Performed statistical analysis on {task['description']}"

class DocumentationAgent(WorkerAgent):
    def perform_work(self, task):
        super().perform_work(task)
        return f"Created reproducible documentation for {task['description']} (Coordinated with CitationAgent)"

class CitationAgent(WorkerAgent):
    def perform_work(self, task):
        # Strict Verification Protocol
        steps = [
            "1. SEARCH: Querying external databases (PubMed/Scholar)...",
            "2. RETRIEVE: Fetching full text for verification...",
            "3. VERIFY: Checking authors, title, journal, DOI...",
            "4. FORMAT: Formatting in Vancouver style...",
            "5. LINK: Attaching source URL..."
        ]
        
        duration = random.uniform(2.0, 5.0)
        for i, step in enumerate(steps):
            time.sleep(duration / len(steps))
            progress = int(((i + 1) / len(steps)) * 100)
            self.memory.update_task_progress(task['id'], progress)
            
        if random.random() < 0.1: raise Exception("Verification failed: Source not found")
        # Simulated Vancouver Citation
        citation = f"Author AA, Author BB. Study on {task['description']}. J Sci Res. 2024;1(1):1-10. doi:10.1234/example"
        return "\n".join(steps) + f"\nRESULT: {citation}"
