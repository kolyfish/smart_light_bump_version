import requests
import sys
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定
# SERVER_URL = "http://localhost:5000"
SERVER_URL = os.getenv("MISSION_CONTROL_URL", "https://mission-smart-light.onrender.com")
ADMIN_KEY = os.getenv("ADMIN_KEY", "BUMP")

def stop_mission():
    print(f"正在連線至 {SERVER_URL} 解除任務指令...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_KEY}"
    }
    
    payload = {
        "mode": "normal",
        "message": "Standby"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/admin/command", json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ 任務已解除，恢復正常監控模式。")
            print("回應:", response.json())
        else:
            print(f"❌ 解除失敗: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        print("請確認 central_command_server.py 正在運行。")

if __name__ == "__main__":
    stop_mission()
