import requests
import time
from typing import Dict, Any

class MissionListener:
    """
    監聽中央司令部的指令
    """
    def __init__(self, server_url: str = None, interval: int = 5):
        import os
        # 強制從環境變數讀取，若無則預設為雲端網址
        self.server_url = server_url or os.getenv("MISSION_CONTROL_URL", "https://mission-smart-light.onrender.com")
        print(f"📡 任務監控連線至: {self.server_url}")
        self.check_interval = interval
        self.last_check = 0
        self.current_orders = {"mode": "normal"}
        self.is_connected = False
        self.connection_status = "offline" # 新增：connected, waking, offline

    def check_orders(self) -> Dict[str, Any]:
        """
        向中央伺服器查詢當前指令
        """
        now = time.time()
        # 避免太頻繁發送請求 (Cooldown)
        if now - self.last_check < self.check_interval:
            return self.current_orders

        try:
            # 增加 timeout 到 10s，觀察是否正在起床
            response = requests.get(f"{self.server_url}/status", timeout=10)
            if response.status_code == 200:
                new_orders = response.json()
                if new_orders.get("mode") != self.current_orders.get("mode"):
                    print(f"🔔 指令變動偵測: {self.current_orders.get('mode')} -> {new_orders.get('mode')}")
                self.current_orders = new_orders
                self.last_check = now
                self.is_connected = True
                self.connection_status = "connected"
        except requests.Timeout:
            # 超時通常代表伺服器正在「起床」 (Render 睡眠機制)
            self.is_connected = False
            self.connection_status = "waking"
        except requests.RequestException as e:
            # 拒絕連線等其他錯誤代表真的離線
            self.is_connected = False
            self.connection_status = "offline"
            if now - getattr(self, '_last_error_log', 0) > 60:
                print(f"⚠️ 無法連接中央司令部 ({self.server_url}): {e}")
                self._last_error_log = now
            
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
