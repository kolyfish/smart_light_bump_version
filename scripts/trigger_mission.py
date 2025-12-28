import requests
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定
SERVER_URL = os.getenv("MISSION_CONTROL_URL", "https://mission-smart-light.onrender.com")
ADMIN_KEY = os.getenv("ADMIN_KEY", "BUMP")

def trigger_mission():
    message = input("請輸入任務簡報文字 (直接按 Enter 使用預設): ") or "執行秘密任務，全體藍燈待命"
    print(f"正在連線至 {SERVER_URL} 發布任務指令...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_KEY}"
    }
    
    payload = {
        "mode": "mission",
        "color": "blue",
        "message": message
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/admin/command", json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ 指令發布成功！")
            print("回應:", response.json())
            print("所有在線燈具應在 5 秒內轉為藍色。")
        else:
            print(f"❌ 發布失敗: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        print("請確認 central_command_server.py 正在運行。")

if __name__ == "__main__":
    trigger_mission()
