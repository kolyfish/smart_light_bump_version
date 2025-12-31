from flask import Flask, jsonify, request, render_template_string, session, redirect, url_for
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 這是「中央司令部」 - 部署在伺服器上 (BUMP 專屬控制台)
app = Flask(__name__)
# 優先使用 .env 中的金鑰，增加安全性
app.secret_key = os.getenv("SECRET_KEY", "BUMP_FALLBACK_SECRET")

# 安全機制：強制 HTTPS 導向 (Production Only)
@app.before_request
def before_request():
    if not request.is_secure and 'localhost' not in request.url and '127.0.0.1' not in request.url:
        # Render 等雲端服務通常使用 X-Forwarded-Proto 標頭判斷
        if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

# 狀態檔案路徑 (持久化存儲)
STATE_FILE = "config/server_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "mode": "normal",
        "color": "blue",
        "message": "Standby",
        "last_update": "N/A"
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

current_state = load_state()
ADMIN_KEY = os.getenv("ADMIN_KEY", "BUMP")

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BUMP LOGIN</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
    <style>
        body { background: #050505; color: #00f2ff; font-family: 'Orbitron', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .login-box { padding: 30px; border: 1px solid #00f2ff; border-radius: 15px; box-shadow: 0 0 20px rgba(0,242,255,0.2); text-align: center; }
        input { background: #000; border: 1px solid #00f2ff; color: #fff; padding: 10px; margin: 10px 0; width: 200px; text-align: center; border-radius: 5px; outline: none; }
        button { background: #00f2ff; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .error { color: #ff0055; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>IDENTIFY</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="COMMAND KEY" autofocus><br>
            <button type="submit">ACCESS</button>
        </form>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUMP MISSION CONTROL</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #00f2ff; --secondary: #0066ff; --danger: #ff0055; --bg: #050505; --card-bg: rgba(20, 20, 25, 0.8); }
        body { margin: 0; padding: 0; background-color: var(--bg); color: white; font-family: 'Rajdhani', sans-serif; height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .container { width: 90%; max-width: 800px; background: var(--card-bg); backdrop-filter: blur(10px); border: 1px solid rgba(0, 242, 255, 0.3); border-radius: 20px; padding: 40px; box-shadow: 0 0 50px rgba(0, 102, 255, 0.2); position: relative; }
        h1 { font-family: 'Orbitron', sans-serif; text-align: center; letter-spacing: 5px; text-transform: uppercase; margin-bottom: 40px; background: linear-gradient(90deg, #fff, var(--primary), #fff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .status-panel { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; }
        .status-item { background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 12px; text-align: center; }
        .status-value { font-size: 24px; font-weight: 700; font-family: 'Orbitron', sans-serif; }
        .status-value.mission { color: var(--primary); text-shadow: 0 0 15px var(--primary); }
        .controls { display: flex; flex-direction: column; gap: 20px; align-items: center; }
        input[type="text"] { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(0, 242, 255, 0.3); border-radius: 8px; padding: 12px 15px; color: white; font-family: 'Rajdhani', sans-serif; font-size: 18px; width: 100%; box-sizing: border-box; outline: none; }
        .btn-group { display: flex; gap: 20px; }
        button { padding: 15px 40px; font-size: 18px; font-family: 'Orbitron', sans-serif; font-weight: 700; border: none; border-radius: 50px; cursor: pointer; transition: 0.3s; text-transform: uppercase; }
        .btn-trigger { background: linear-gradient(45deg, var(--secondary), var(--primary)); color: #000; box-shadow: 0 0 30px rgba(0, 242, 255, 0.4); }
        .btn-stop { background: transparent; border: 2px solid rgba(255, 255, 255, 0.2); color: white; }
        .logs { margin-top: 30px; background: rgba(0, 0, 0, 0.6); height: 80px; border-radius: 10px; padding: 15px; font-family: monospace; font-size: 12px; overflow-y: auto; color: #0f0; border: 1px solid rgba(255, 255, 255, 0.1); }
        .logout-btn { position: absolute; top: 10px; right: 20px; color: #666; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout-btn">TERMINATE SESSION</a>
        <h1>Mission Control</h1>
        <div class="status-panel">
            <div class="status-item"><div>MODE</div><div class="status-value" id="mode-val">...</div></div>
            <div class="status-item"><div>LAST UPDATE</div><div class="status-value" id="time-val" style="font-size: 18px;">...</div></div>
            <div class="status-item" style="grid-column: span 2;"><div>CURRENT MESSAGE</div><div class="status-value" id="msg-val" style="font-size: 16px; color: var(--primary);">...</div></div>
        </div>
        <div class="controls">
            <input type="text" id="mission-msg" placeholder="ENTER BROADCAST MESSAGE" value="全體注意，這是總部指令">
            <div class="btn-group">
                <button class="btn-trigger" onclick="sendCommand('mission')">ENGAGE</button>
                <button class="btn-stop" onclick="sendCommand('normal')">STAND DOWN</button>
            </div>
        </div>
        <div class="logs" id="log-box">[SYS] Encrypted link established.<br></div>
    </div>
    <script>
        async function fetchStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            document.getElementById('mode-val').innerText = data.mode.toUpperCase();
            document.getElementById('mode-val').className = 'status-value ' + data.mode;
            document.getElementById('time-val').innerText = data.last_update;
            document.getElementById('msg-val').innerText = data.message;
            
            // 初次載入或訊息由其他地方更改時，更新輸入框
            const input = document.getElementById('mission-msg');
            if (document.activeElement !== input) {
                input.value = data.message;
            }
        }

        async function sendCommand(mode) {
            const message = mode === 'mission' ? document.getElementById('mission-msg').value : 'Standby';
            const res = await fetch('/admin/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode, color: mode==='mission'?'blue':'yellow', message })
            });
            if (res.ok) {
                addLog(`[CMD] Successfully set to ${mode}`);
                fetchStatus();
            }
        }

        function addLog(msg) {
            const box = document.getElementById('log-box');
            box.innerHTML += `[${new Date().toLocaleTimeString()}] ${msg}<br>`;
            box.scrollTop = box.scrollHeight;
        }
        setInterval(fetchStatus, 3000);
        fetchStatus();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_KEY:
            session['logged_in'] = True
            session.permanent = True # 保持登入狀態
            return redirect(url_for('home'))
        else:
            import time
            time.sleep(2) # 防守機制：故意延遲 2 秒，防止暴力破解
            error = "INVALID ACCESS KEY"
    
    if not session.get('logged_in'):
        return render_template_string(LOGIN_HTML, error=error)
        
    return render_template_string(DASHBOARD_HTML)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(current_state)

@app.route('/admin/command', methods=['POST'])
def update_status():
    if not session.get('logged_in'):
        # 同樣允許 Header 驗證以便 API 控制 (雖然 Bump 用 Web 介面)
        auth_header = request.headers.get('Authorization')
        if auth_header != f"Bearer {ADMIN_KEY}":
            return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    for key in ['mode', 'color', 'message']:
        if key in data:
            current_state[key] = data[key]
    
    current_state['last_update'] = datetime.now().strftime("%H:%M:%S")
    save_state(current_state)
    return jsonify({"status": "updated", "current_state": current_state})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5010))
    app.run(host='0.0.0.0', port=port)
