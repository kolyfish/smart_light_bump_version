import requests
import sys

# SERVER_URL = "http://localhost:5000"
SERVER_URL = "https://mission-smart-light.onrender.com"
ADMIN_KEY = "BUMP_VERSION_SUPER_SECRET_KEY"

def trigger_mission():
    print(f"正在連線至 {SERVER_URL} 發布任務指令...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_KEY}"
    }
    
    payload = {
        "mode": "mission",
        "color": "blue",
        "message": "EXECUTE_ORDER_66"
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
