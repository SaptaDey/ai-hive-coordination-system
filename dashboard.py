import sqlite3
import os
import json
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
DB_PATH = "hive_memory.db"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Hive Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; margin: 0; padding: 20px; }
        h1 { color: #61dafb; border-bottom: 2px solid #333; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background-color: #2d2d2d; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h2 { color: #ff9800; margin-top: 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #444; }
        th { color: #9e9e9e; }
        .status-IDLE { color: #8bc34a; }
        .status-BUSY { color: #ffc107; }
        .status-PENDING { color: #9e9e9e; }
        .status-IN_PROGRESS { color: #2196f3; }
        .status-COMPLETED { color: #4caf50; }
        .status-FAILED { color: #f44336; }
        .log-entry { font-family: monospace; font-size: 0.9em; border-bottom: 1px solid #333; padding: 5px 0; }
        .timestamp { color: #888; margin-right: 10px; }
        .agent-id { color: #00bcd4; font-weight: bold; }
        .action { color: #e91e63; }
        
        /* New Styles */
        .tab-nav { margin-bottom: 20px; }
        .tab-btn { background: #333; color: #fff; border: none; padding: 10px 20px; cursor: pointer; border-radius: 4px; margin-right: 10px; }
        .tab-btn.active { background: #61dafb; color: #000; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .progress-bar { background: #444; height: 10px; border-radius: 5px; overflow: hidden; width: 100px; display: inline-block; vertical-align: middle; margin-right: 5px; }
        .progress-fill { background: #4caf50; height: 100%; width: 0%; transition: width 0.5s; }
        
        .control-btn { padding: 5px 15px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }
        .btn-pause { background: #ff9800; color: #000; }
        .btn-resume { background: #4caf50; color: #fff; }
        
        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; }
        .modal-content { background: #2d2d2d; margin: 5% auto; padding: 20px; width: 80%; max-height: 80vh; overflow: auto; border-radius: 8px; position: relative; }
        .close-btn { position: absolute; top: 10px; right: 10px; color: #fff; cursor: pointer; font-size: 24px; }
        .output-frame { width: 100%; height: 500px; border: none; background: #fff; }
    </style>
</head>
<body>
    <div class="tab-nav">
        <button id="btn-live" class="tab-btn active" onclick="switchTab('live')">Live View</button>
        <button id="btn-history" class="tab-btn" onclick="switchTab('history')">History</button>
    </div>

    <!-- LIVE VIEW -->
    <div id="live" class="tab-content active">
        <h1>
            <span>👑 AI Hive Matrix <small id="session-display" style="font-size: 0.5em; color: #888;"></small></span>
            <div id="controls">
                <span id="system-status" style="font-size: 0.6em; margin-right: 10px;">RUNNING</span>
                <button id="btn-control" class="control-btn btn-pause" onclick="toggleSystem()">PAUSE</button>
            </div>
        </h1>
        
        <div class="container">
            <div class="card">
                <h2>🐝 Active Agents</h2>
                <table id="agent-table">
                    <thead><tr><th>ID</th><th>Role</th><th>Status</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>📋 Task Queue</h2>
                <table id="task-table">
                    <thead><tr><th>Description</th><th>Status</th><th>Progress</th><th>Output</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h2>zmq_LOGS</h2>
            <div id="log-container"></div>
        </div>
    </div>

    <!-- HISTORY VIEW -->
    <div id="history" class="tab-content">
        <h1>📜 Session History</h1>
        <div class="card">
            <table id="history-table">
                <thead><tr><th>Session ID</th><th>Tasks</th><th>Start Time</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <!-- OUTPUT MODAL -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <h2 id="modal-title">Task Output</h2>
            <div id="modal-body"></div>
        </div>
    </div>

    <script>
        let currentStatus = "RUNNING";

        function switchTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tab).classList.add('active');
            document.getElementById('btn-' + tab).classList.add('active');
            if(tab === 'history') loadHistory();
        }

        function updateDashboard() {
            if(!document.getElementById('live').classList.contains('active')) return;

            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('session-display').innerText = `Session: ${data.session_id || 'N/A'}`;
                    
                    // Update System Status
                    currentStatus = data.system_status;
                    const statusEl = document.getElementById('system-status');
                    const btnEl = document.getElementById('btn-control');
                    statusEl.innerText = currentStatus;
                    if(currentStatus === "PAUSED") {
                        statusEl.style.color = "orange";
                        btnEl.innerText = "RESUME";
                        btnEl.className = "control-btn btn-resume";
                    } else {
                        statusEl.style.color = "#4caf50";
                        btnEl.innerText = "PAUSE";
                        btnEl.className = "control-btn btn-pause";
                    }

                    // Agents
                    const agentTable = document.querySelector('#agent-table tbody');
                    agentTable.innerHTML = '';
                    data.agents.forEach(agent => {
                        const row = `<tr>
                            <td class="agent-id">${agent[0].substring(0, 8)}...</td>
                            <td>${agent[1]}</td>
                            <td class="status-${agent[2]}">${agent[2]}</td>
                        </tr>`;
                        agentTable.innerHTML += row;
                    });

                    // Tasks
                    const taskTable = document.querySelector('#task-table tbody');
                    taskTable.innerHTML = '';
                    data.tasks.forEach(t => {
                        const progress = t[4] || 0;
                        let outputBtn = '-';
                        if(t[5]) {
                            outputBtn = `<button onclick="viewOutput('${t[5]}')">View</button>`;
                        }
                        
                        const row = `<tr>
                            <td>${t[1]}</td>
                            <td class="status-${t[3]}">${t[3]}</td>
                            <td>
                                <div class="progress-bar"><div class="progress-fill" style="width:${progress}%"></div></div>
                                ${progress}%
                            </td>
                            <td>${outputBtn}</td>
                        </tr>`;
                        taskTable.innerHTML += row;
                    });

                    // Logs
                    const logContainer = document.getElementById('log-container');
                    logContainer.innerHTML = '';
                    data.logs.forEach(log => {
                        const date = new Date(log[4] * 1000).toLocaleTimeString();
                        const entry = `<div class="log-entry">
                            <span class="timestamp">[${date}]</span>
                            <span class="agent-id">${log[1].substring(0, 8)}</span>
                            <span class="action">${log[2]}</span>: ${log[3]}
                        </div>`;
                        logContainer.innerHTML += entry;
                    });
                });
        }

        function toggleSystem() {
            const action = currentStatus === "RUNNING" ? "pause" : "resume";
            fetch('/api/control', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action})
            }).then(() => updateDashboard());
        }

        function loadHistory() {
            fetch('/api/history')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.querySelector('#history-table tbody');
                    tbody.innerHTML = '';
                    data.forEach(h => {
                        const date = new Date(h.start_time * 1000).toLocaleString();
                        tbody.innerHTML += `<tr><td>${h.session_id}</td><td>${h.task_count}</td><td>${date}</td></tr>`;
                    });
                });
        }

        function viewOutput(path) {
            const modal = document.getElementById('modal');
            const body = document.getElementById('modal-body');
            // Convert local path to static URL if possible, or just show text
            // For this demo, we assume it's in static/outputs
            const filename = path.split(/[\\/]/).pop();
            const url = `/static/outputs/${filename}`;
            
            if(filename.endsWith('.svg')) {
                body.innerHTML = `<iframe src="${url}" class="output-frame"></iframe>`;
            } else {
                body.innerText = `Output saved to: ${path}`;
            }
            modal.style.display = 'block';
        }

        function closeModal() {
            document.getElementById('modal').style.display = 'none';
        }

        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def get_current_session():
    try:
        with open("current_session.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

@app.route('/api/data')
def get_data():
    session_id = get_current_session()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if session_id:
        c.execute("SELECT id, role, status FROM agents WHERE session_id = ?", (session_id,))
        agents = c.fetchall()
        
        # Added progress and output_path to query
        c.execute("SELECT id, description, assigned_to, status, progress, output_path FROM tasks WHERE session_id = ? ORDER BY created_at DESC", (session_id,))
        tasks = c.fetchall()
        
        c.execute("SELECT id, agent_id, action, details, timestamp FROM logs WHERE session_id = ? ORDER BY timestamp DESC LIMIT 20", (session_id,))
        logs = c.fetchall()
        
        # Get System Status
        c.execute("SELECT value FROM system_state WHERE key = 'status' AND session_id = ?", (session_id,))
        row = c.fetchone()
        system_status = row[0] if row else "RUNNING"
    else:
        agents = []
        tasks = []
        logs = []
        system_status = "OFFLINE"
    
    conn.close()
    return jsonify({"agents": agents, "tasks": tasks, "logs": logs, "session_id": session_id, "system_status": system_status})

@app.route('/api/history')
def get_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Get distinct sessions
    c.execute("SELECT DISTINCT session_id FROM tasks")
    sessions = [row[0] for row in c.fetchall()]
    history = []
    for sess in sessions:
        c.execute("SELECT COUNT(*) FROM tasks WHERE session_id = ?", (sess,))
        task_count = c.fetchone()[0]
        c.execute("SELECT MIN(created_at) FROM tasks WHERE session_id = ?", (sess,))
        start_time = c.fetchone()[0]
        history.append({"session_id": sess, "task_count": task_count, "start_time": start_time})
    conn.close()
    return jsonify(history)

@app.route('/api/control', methods=['POST'])
def control_system():
    action = request.json.get('action')
    session_id = get_current_session()
    if not session_id: return jsonify({"error": "No active session"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if action == "pause":
        c.execute("INSERT OR REPLACE INTO system_state (key, value, session_id) VALUES ('status', 'PAUSED', ?)", (session_id,))
    elif action == "resume":
        c.execute("INSERT OR REPLACE INTO system_state (key, value, session_id) VALUES ('status', 'RUNNING', ?)", (session_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

import webbrowser
import threading

if __name__ == '__main__':
    print("Starting Dashboard on http://localhost:5000")
    print("To view in Antigravity Internal Browser, visit:")
    print("http://localhost:41959/?url=http://localhost:5000")
    # Ensure static folder exists for outputs
    if not os.path.exists("static/outputs"):
        os.makedirs("static/outputs")
    app.run(debug=True, port=5000)
