from flask import Flask, jsonify, request
import threading

# 這是「中央司令部」 - 部署在伺服器上 (如 Heroku, Render, 或你家的一台固定 IP 電腦)

app = Flask(__name__)

# 全局狀態 (存放在記憶體中，重啟會重置)
# mode: 'normal' (正常運作), 'mission' (出任務 - 藍燈), 'party' (開趴)
current_state = {
    "mode": "normal",
    "color": "blue",  # 當 mode == mission 時的顏色
    "message": "Standby"
}

# 簡單的安全驗證 (實際生產環境請用更強的驗證)
ADMIN_KEY = "BUMP_VERSION_SUPER_SECRET_KEY"

@app.route('/')
def home():
    return "Bump Version Command Center Online."

@app.route('/status', methods=['GET'])
def get_status():
    """所有客戶端 (燈具) 都會不斷呼叫這個 API"""
    return jsonify(current_state)

@app.route('/admin/command', methods=['POST'])
def update_status():
    """只有你能呼叫這個 API 下達指令"""
    # 驗證密鑰
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_KEY}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    
    # 更新狀態
    if 'mode' in data:
        current_state['mode'] = data['mode']
    if 'color' in data:
        current_state['color'] = data['color']
    if 'message' in data:
        current_state['message'] = data['message']
        
    return jsonify({"status": "updated", "current_state": current_state})

if __name__ == '__main__':
    # 為了方便測試，跑在 0.0.0.0
    print("🚀 中央司令部啟動... 等待指令")
    app.run(host='0.0.0.0', port=5000)
