from flask import Flask, jsonify, request, render_template_string
import threading
import os

# 這是「中央司令部」 - 部署在伺服器上
app = Flask(__name__)

# 全局狀態
current_state = {
    "mode": "normal",
    "color": "blue",
    "message": "Standby",
    "last_update": "N/A"
}

ADMIN_KEY = os.getenv("ADMIN_KEY", "BUMP_VERSION_SUPER_SECRET_KEY")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUMP MISSION CONTROL</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00f2ff;
            --secondary: #0066ff;
            --danger: #ff0055;
            --bg: #050505;
            --card-bg: rgba(20, 20, 25, 0.8);
        }

        body {
            margin: 0;
            padding: 0;
            background-color: var(--bg);
            color: white;
            font-family: 'Rajdhani', sans-serif;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(0, 102, 255, 0.1) 0%, transparent 80%),
                linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
                linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            background-size: 100% 100%, 100% 2px, 3px 100%;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .container {
            width: 90%;
            max-width: 800px;
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 0 50px rgba(0, 102, 255, 0.2), inset 0 0 20px rgba(0, 242, 255, 0.1);
            position: relative;
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            text-align: center;
            letter-spacing: 5px;
            text-transform: uppercase;
            margin-bottom: 40px;
            background: linear-gradient(90deg, #fff, var(--primary), #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0, 242, 255, 0.5);
        }

        .status-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 40px;
        }

        .status-item {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }

        .status-label {
            font-size: 14px;
            color: #aaa;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .status-value {
            font-size: 24px;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
        }

        .status-value.mission { color: var(--primary); }
        .status-value.normal { color: #fff; }

        .controls {
            display: flex;
            gap: 20px;
            justify-content: center;
        }

        button {
            padding: 15px 40px;
            font-size: 18px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }

        .btn-trigger {
            background: linear-gradient(45deg, var(--secondary), var(--primary));
            color: #000;
            box-shadow: 0 0 30px rgba(0, 242, 255, 0.4);
        }

        .btn-trigger:hover {
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 0 50px rgba(0, 242, 255, 0.6);
        }

        .btn-stop {
            background: transparent;
            border: 2px solid rgba(255, 255, 255, 0.2);
            color: white;
        }

        .btn-stop:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: #fff;
            transform: translateY(-5px);
        }

        .logs {
            margin-top: 40px;
            background: rgba(0, 0, 0, 0.6);
            height: 100px;
            border-radius: 10px;
            padding: 15px;
            font-family: monospace;
            font-size: 12px;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: #0f0;
        }

        .cyber-line {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
            animation: scan 3s linear infinite;
        }

        @keyframes scan {
            0% { transform: translateY(0); opacity: 0; }
            50% { opacity: 1; }
            100% { transform: translateY(480px); opacity: 0; }
        }

        .loading-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loader">
        <h2 style="font-family: 'Orbitron';">送信中...</h2>
    </div>

    <div class="container">
        <div class="cyber-line"></div>
        <h1>Command Center</h1>
        
        <div class="status-panel">
            <div class="status-item">
                <div class="status-label">Current Mode</div>
                <div class="status-value" id="mode-val">Loading...</div>
            </div>
            <div class="status-item">
                <div class="status-label">System Status</div>
                <div class="status-value" id="status-val">Online</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn-trigger" onclick="sendCommand('mission', 'blue', 'EXECUTE_ORDER_66')">發動任務</button>
            <button class="btn-stop" onclick="sendCommand('normal', 'yellow', 'Standby')">解除任務</button>
        </div>

        <div class="logs" id="log-box">
            [SYS] Initializing command link...<br>
            [SYS] Connected to core network.<br>
        </div>
    </div>

    <script>
        const ADMIN_KEY = "{{ admin_key }}";

        async function fetchStatus() {
            try {
                const res = await fetch('/status');
                const data = await res.json();
                document.getElementById('mode-val').innerText = data.mode.toUpperCase();
                document.getElementById('mode-val').className = 'status-value ' + data.mode;
            } catch (e) {}
        }

        async function sendCommand(mode, color, message) {
            document.getElementById('loader').style.display = 'flex';
            try {
                const res = await fetch('/admin/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + ADMIN_KEY
                    },
                    body: JSON.stringify({ mode, color, message })
                });
                
                if (res.ok) {
                    addLog(`[CMD] Mode set to ${mode.toUpperCase()}`);
                    await fetchStatus();
                } else {
                    addLog(`[ERR] Authorization Failed`);
                }
            } catch (e) {
                addLog(`[ERR] Network error`);
            }
            document.getElementById('loader').style.display = 'none';
        }

        function addLog(msg) {
            const box = document.getElementById('log-box');
            const time = new Date().toLocaleTimeString();
            box.innerHTML += `[${time}] ${msg}<br>`;
            box.scrollTop = box.scrollHeight;
        }

        setInterval(fetchStatus, 3000);
        fetchStatus();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML, admin_key=ADMIN_KEY)

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(current_state)

@app.route('/admin/command', methods=['POST'])
def update_status():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_KEY}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if 'mode' in data:
        current_state['mode'] = data['mode']
    if 'color' in data:
        current_state['color'] = data['color']
    if 'message' in data:
        current_state['message'] = data['message']
    
    from datetime import datetime
    current_state['last_update'] = datetime.now().strftime("%H:%M:%S")
        
    return jsonify({"status": "updated", "current_state": current_state})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
