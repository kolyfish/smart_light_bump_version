import requests
import time
from typing import Dict, Any

class MissionListener:
    """
    監聽中央司令部的指令
    """
    def __init__(self, server_url: str = "http://localhost:5000", interval: int = 5):
        self.server_url = server_url
        self.check_interval = interval
        self.last_check = 0
        self.current_orders = {"mode": "normal"}

    def check_orders(self) -> Dict[str, Any]:
        """
        向中央伺服器查詢當前指令
        """
        now = time.time()
        # 避免太頻繁發送請求 (Cooldown)
        if now - self.last_check < self.check_interval:
            return self.current_orders

        try:
            response = requests.get(f"{self.server_url}/status", timeout=2)
            if response.status_code == 200:
                self.current_orders = response.json()
                self.last_check = now
        except requests.RequestException:
            # 如果連不上伺服器，預設保持原本狀態，不要崩潰
            # print("⚠️ 無法連接中央司令部，保持靜默模式...")
            pass
            
        return self.current_orders

    def is_mission_active(self) -> bool:
        """快速檢查是否要出任務"""
        orders = self.check_orders()
        return orders.get("mode") == "mission"

if __name__ == "__main__":
    # 測試程式
    listener = MissionListener()
    while True:
        orders = listener.check_orders()
        print(f"目前指令: {orders}")
        if listener.is_mission_active():
            print("🔵🔵🔵 出任務中！全體藍燈！ 🔵🔵🔵")
        else:
            print("...待命中 (一般股票監控)")
        time.sleep(2)
