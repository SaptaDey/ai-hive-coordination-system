import time
import threading
from typing import List, Dict
from hive_core import BaseAgent, Message, MessageType, SharedMemory, MessageBus
from cognitive_models import NeuralCortex
from workers import ArchitectAgent, CoderAgent, TesterAgent, AnalystAgent, ResearcherAgent, VisualizationAgent, StatisticianAgent, DocumentationAgent, CitationAgent

class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, shared_memory, message_bus, supervisor_id, session_id="default") -> BaseAgent:
        if agent_type == "ARCHITECT":
            return ArchitectAgent("Architect-" + str(int(time.time())), "ARCHITECT", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "CODER":
            return CoderAgent("Coder-" + str(int(time.time())), "CODER", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "TESTER":
            return TesterAgent("Tester-" + str(int(time.time())), "TESTER", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "ANALYST":
            return AnalystAgent("Analyst-" + str(int(time.time())), "ANALYST", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "RESEARCHER":
            return ResearcherAgent("Researcher-" + str(int(time.time())), "RESEARCHER", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "VISUALIZER":
            return VisualizationAgent("Visualizer-" + str(int(time.time())), "VISUALIZER", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "STATISTICIAN":
            return StatisticianAgent("Statistician-" + str(int(time.time())), "STATISTICIAN", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "DOCUMENTER":
            return DocumentationAgent("Documenter-" + str(int(time.time())), "DOCUMENTER", shared_memory, message_bus, supervisor_id, session_id)
        elif agent_type == "CITATION_MANAGER":
            return CitationAgent("CitationMgr-" + str(int(time.time())), "CITATION_MANAGER", shared_memory, message_bus, supervisor_id, session_id)
        return None

class QueenAgent(BaseAgent):
    def __init__(self, name: str, shared_memory: SharedMemory, message_bus: MessageBus, session_id: str = "default"):
        super().__init__(name, "QUEEN", shared_memory, message_bus, None, session_id)
        self.cortex = NeuralCortex()
        self.active_workers: Dict[str, BaseAgent] = {}
        self.task_queue = []
        self.running = True
        
        # Start management loop
        self.thread = threading.Thread(target=self.management_loop)
        self.thread.start()

    def management_loop(self):
        while self.running:
            self.check_pending_tasks()
            self.optimize_resources()
            time.sleep(2)

    def check_pending_tasks(self):
        # Fetch pending tasks from Shared Memory for THIS session
        tasks = self.memory.get_pending_tasks(session_id=self.session_id)
        if not tasks:
            return

        # Use Cortex to decide coordination mode
        complexity_score = min(len(tasks), 10) # Simple proxy for complexity
        mode = self.cortex.coordination.predict_mode("HIGH" if complexity_score > 5 else "LOW", len(tasks))
        
        self.log("DECISION", f"Selected Coordination Mode: {mode}")

        for task_row in tasks:
            task = {
                "id": task_row[0],
                "description": task_row[1],
                "priority": task_row[4]
            }
            self.assign_task(task)

    def assign_task(self, task):
        # Find suitable idle agent
        best_agent = None
        for agent_id, agent in self.active_workers.items():
            # Check status in DB
            rows = self.memory.get_all_agents(session_id=self.session_id)
            status = next((r[2] for r in rows if r[0] == agent_id), "UNKNOWN")
            
            if status == "IDLE":
                # Simple matching logic
                desc = task['description'].lower()
                if "code" in desc and isinstance(agent, CoderAgent): best_agent = agent
                elif "test" in desc and isinstance(agent, TesterAgent): best_agent = agent
                elif "design" in desc and isinstance(agent, ArchitectAgent): best_agent = agent
                elif "analyze" in desc and isinstance(agent, AnalystAgent): best_agent = agent
                elif "research" in desc and isinstance(agent, ResearcherAgent): best_agent = agent
                elif "visual" in desc and isinstance(agent, VisualizationAgent): best_agent = agent
                elif "statistic" in desc and isinstance(agent, StatisticianAgent): best_agent = agent
                elif "document" in desc and isinstance(agent, DocumentationAgent): best_agent = agent
                elif ("cite" in desc or "refer" in desc) and isinstance(agent, CitationAgent): best_agent = agent
                
                if best_agent: break

        if best_agent:
            self.memory.assign_task(task['id'], best_agent.id)
            self.send_message(best_agent.id, MessageType.TASK_ASSIGNMENT, task)
            self.log("ASSIGNMENT", f"Assigned task {task['id']} to {best_agent.name}")
        else:
            # No agent found -> Auto-Scale
            self.log("RESOURCE", "No suitable agent found. Attempting to spawn new agent.")
            self.spawn_agent_for_task(task)

    def spawn_agent_for_task(self, task):
        agent_type = "CODER" # Default
        desc = task['description'].lower()
        
        if "design" in desc: agent_type = "ARCHITECT"
        elif "test" in desc: agent_type = "TESTER"
        elif "analyze" in desc: agent_type = "ANALYST"
        elif "research" in desc: agent_type = "RESEARCHER"
        elif "visual" in desc: agent_type = "VISUALIZER"
        elif "statistic" in desc: agent_type = "STATISTICIAN"
        elif "document" in desc: agent_type = "DOCUMENTER"
        elif "cite" in desc or "refer" in desc: agent_type = "CITATION_MANAGER"

        # Check limits (Heuristic: Max 50 agents now that we have more types)
        if len(self.active_workers) < 50:
            new_agent = AgentFactory.create_agent(agent_type, self.memory, self.bus, self.id, self.session_id)
            self.active_workers[new_agent.id] = new_agent
            self.subordinates.append(new_agent.id)
            self.log("SPAWN", f"Spawned new {agent_type}: {new_agent.name}")
            # Immediate assignment
            self.memory.assign_task(task['id'], new_agent.id)
            self.send_message(new_agent.id, MessageType.TASK_ASSIGNMENT, task)
        else:
            self.log("WARNING", "Max agent limit reached. Task queued.")

    def optimize_resources(self):
        # Check for idle agents to decommission (simple logic)
        pass

    def process_message(self, message: Message):
        if message.msg_type == MessageType.TASK_RESULT:
            self.memory.complete_task(message.content['task_id'], message.content['result'])
            self.log("COMPLETION", f"Task {message.content['task_id']} completed by {message.sender_id}")

    def stop(self):
        self.log("SYSTEM", "Initiating Hive Shutdown...")
        self.running = False
        
        # Terminate all workers
        for agent_id, agent in self.active_workers.items():
            self.memory.update_agent_status(agent_id, "TERMINATED")
            # In a real system, we'd send a kill signal. Here we just mark them.
            
        self.log("SYSTEM", "Hive Shutdown Complete.")
        self.thread.join()
