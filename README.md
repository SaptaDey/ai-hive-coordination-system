# AI Hive Coordination System

![AI Hive Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![License](https://img.shields.io/badge/License-MIT-blue)

A robust, multi-agent orchestration framework designed to simulate complex workflows, scientific research, and crisis response scenarios. Built within the Google Hivemind IDE context, this system demonstrates advanced agent coordination, fault tolerance, and specialized worker capabilities.

## 🐝 Overview

The AI Hive is a centralized coordination system where a "Queen" agent orchestrates a swarm of specialized worker agents to complete complex tasks. It features a shared memory architecture, an event-driven message bus, and a real-time monitoring dashboard.

### Key Features

*   **Multi-Agent Coordination**: Centralized "Queen" agent manages task assignment, load balancing, and auto-scaling.
*   **Specialized Workers**:
    *   `CoderAgent`: Implements software solutions.
    *   `ResearcherAgent`: Gathers information and insights.
    *   `VisualizationAgent`: Generates scientific visualizations.
    *   `StatisticianAgent`: Performs statistical analysis.
    *   `CitationAgent`: Manages references with strict verification (Vancouver style).
    *   `DocumentationAgent`: Ensures scientific reproducibility.
*   **Fault Tolerance**: Robust error handling with simulated agent failures and automatic task recovery.
*   **Real-Time Dashboard**: Flask-based web interface for monitoring agent status, task queues, and system logs.
*   **Scenario Runner**: Built-in engine to execute complex scenarios like "Alien Signal Decoding", "Global Pandemic Response", and "Tech Startup Sprint".

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   `pip`

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/ai-hive-coordination-system.git
    cd ai-hive-coordination-system
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  **Start the Hive Core**:
    ```bash
    python main.py
    ```
    This initializes the Queen, the Message Bus, and starts the simulation loop.

2.  **Launch the Dashboard**:
    In a separate terminal:
    ```bash
    python dashboard.py
    ```
    Access the dashboard at `http://localhost:5000`.

3.  **Run Scenarios**:
    Inject specific scenarios to test the system:
    ```bash
    python scenario_runner.py alien      # Alien Signal Decoding
    python scenario_runner.py pandemic   # Global Pandemic Response
    python scenario_runner.py startup    # Tech Startup Sprint
    ```

## 📂 Project Structure

*   `main.py`: Entry point for the Hive Core simulation.
*   `hive_core.py`: Core infrastructure (SharedMemory, MessageBus, BaseAgent).
*   `queen.py`: Logic for the Queen Agent (Orchestrator).
*   `workers.py`: Definitions for all specialized Worker Agents.
*   `dashboard.py`: Flask application for the monitoring dashboard.
*   `scenario_runner.py`: Script to inject complex testing scenarios.
*   `templates/`: HTML templates for the dashboard.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed as part of the Google Antigravity Advanced Agentic Coding initiative.*
