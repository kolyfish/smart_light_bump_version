import asyncio
from plugp100.common.credentials import AuthCredential
from plugp100.new.device_factory import connect, DeviceConnectConfiguration

class TapoController:
    def __init__(self):
        # 使用者提供的憑據
        self.username = "kolyfish2@gmail.com"
        self.password = "WWuu0921"
        self.ip_address = "192.168.100.150"
        
        # 使用 v5.x 推薦的連線配置
        self.credentials = AuthCredential(self.username, self.password)
        self.config = DeviceConnectConfiguration(
            host=self.ip_address,
            credentials=self.credentials,
            device_type="SMART.TAPOBULB"
        )
        import os
        self.simulation_mode = os.getenv("SIMULATION_MODE", "false").lower() == "true"
        # 不再快取 self.device，因為每次 asyncio.run 都會建立新 loop
        # 快取 device 會導致 aiohttp ClientSession Tied 到已關閉的 loop
        
        # 線程鎖：防止多個線程同時嘗試控制裝置 (Race Condition)
        import threading
        self._lock = threading.Lock()

    async def _get_connected_device(self):
        """建立並返回已連線的裝置實體。"""
        try:
            device = await connect(self.config)
            
            # 手動修正 KlapProtocol 類型問題
            client = device.client
            import inspect
            if inspect.isclass(client.protocol) or client.protocol is None:
                from plugp100.protocol.klap import klap_handshake_v2
                from plugp100.protocol.klap.klap_protocol import KlapProtocol
                protocol = KlapProtocol(
                    auth_credential=self.credentials,
                    url=f"http://{self.ip_address}/app",
                    klap_strategy=klap_handshake_v2()
                )
                client._protocol = protocol
            
            await device.update()
            return device
        except Exception as e:
            print(f"[{self.ip_address}] 連線或初始化失敗: {e}")
            raise e

    async def _set_brightness(self, level: int):
        """設定燈泡亮度 (1-100)。"""
        if self.simulation_mode:
            print(f"[模擬模式] 設定亮度為: {level}")
            return
            
        try:
            device = await connect(self.config)
            await device.set_brightness(level)
        except Exception as e:
            print(f"[{self.ip_address}] 設定亮度失敗: {e}")

    async def _set_color_hs(self, hue: int, saturation: int):
        """設定彩色燈泡顏色 (色相/飽和度)。"""
        if self.simulation_mode:
            color_map = {120: "綠色", 60: "黃色", 0: "紅色", 280: "紫色"}
            color_name = color_map.get(hue, f"未知 Hue:{hue}")
            print(f"[模擬模式] 點亮顏色: {color_name}")
            return

        try:
            device = await connect(self.config)
            # 手動修正 KlapProtocol 類型問題
            client = device.client
            import inspect
            if inspect.isclass(client.protocol) or client.protocol is None:
                from plugp100.protocol.klap import klap_handshake_v2
                from plugp100.protocol.klap.klap_protocol import KlapProtocol
                protocol = KlapProtocol(
                    auth_credential=self.credentials,
                    url=f"http://{self.ip_address}/app",
                    klap_strategy=klap_handshake_v2()
                )
                client._protocol = protocol
            
            await device.update()
            
            color_map = {120: "綠色", 60: "黃色", 0: "紅色", 280: "紫色"}
            color_name = color_map.get(hue, f"未知 Hue:{hue}")
            print(f"[{self.ip_address}] 正在切換顏色為: {color_name}")
            
            await device.turn_on()
            # 核心修正：切換顏色時顯式重設亮度為 100 (避免從睡眠待命模式恢復時亮度過低)
            await device.set_brightness(100)
            
            result = await device.set_hue_saturation(hue, saturation)
            
            if result.is_failure():
                from plugp100.new.components.light_component import LightComponent
                await device.get_component(LightComponent).set_hue_saturation(hue, saturation)
                
            print(f"[{self.ip_address}] 顏色切換成功 ({color_name})，亮度已恢復 100%。")
        except Exception as e:
            print(f"[{self.ip_address}] 操控失敗: {e}")

    async def _test_sequence(self):
        """執行一鍵測試序列：漸暗 -> 關閉 -> 變色迴圈 -> 回歸黃色。"""
        try:
            device = await connect(self.config)
            print("開始執行燈光測試序列...")
            
            # 1. 漸暗效果
            for b in [70, 40, 10]:
                await device.set_brightness(b)
                await asyncio.sleep(0.3)
            
            # 2. 暫時關閉
            await device.turn_off()
            await asyncio.sleep(0.5)
            
            # 3. 變色開啟
            await device.turn_on()
            # 快速紅綠黃切換
            for h in [0, 120, 60]:
                await device.set_hue_saturation(h, 100)
                await device.set_brightness(100)
                await asyncio.sleep(0.6)
            
            print("測試序列執行完畢。")
        except Exception as e:
            print(f"測試序列出錯: {e}")

    def turn_on_green(self):
        """觸發警報：轉為綠色。"""
        if self._lock.acquire(blocking=False):
            try:
                asyncio.run(self._set_color_hs(120, 100))
            finally:
                self._lock.release()
        else:
            print("TapoController: 裝置忙線中，跳過綠燈指令")

    def turn_on_red(self):
        """監控中：轉為紅色。"""
        if self._lock.acquire(blocking=False):
            try:
                asyncio.run(self._set_color_hs(0, 100))
            finally:
                self._lock.release()
        else:
            print("TapoController: 裝置忙線中，跳過紅燈指令")

    def turn_on_yellow(self):
        """常態/待機：轉為黃色。"""
        if self._lock.acquire(blocking=False):
            try:
                asyncio.run(self._set_color_hs(60, 100))
            finally:
                self._lock.release()
        else:
            print("TapoController: 裝置忙線中，跳過黃燈指令")

    def turn_on_purple(self):
        """閃崩警報：轉為紫色。"""
        if self._lock.acquire(blocking=False):
            try:
                asyncio.run(self._set_color_hs(280, 100))
            finally:
                self._lock.release()
        else:
            print("TapoController: 裝置忙線中，跳過紫色指令")

    def run_test_sequence(self):
        """執行完整測試序列。"""
        # 測試序列較長，我們願意等待鎖釋放
        with self._lock:
            asyncio.run(self._test_sequence())

    async def _turn_off(self):
        """關閉裝置。"""
        try:
            device = await connect(self.config)
            print(f"[{self.ip_address}] Web 請求：正在執行關閉指令...")
            await device.turn_off()
            print(f"[{self.ip_address}] 裝置已成功關閉。")
        except Exception as e:
            print(f"[{self.ip_address}] 關閉執行失敗: {e}")

    def turn_off(self):
        """手動關閉。"""
        with self._lock:
            asyncio.run(self._turn_off())
    
    async def _set_sleep_standby(self):
        """睡眠待命模式：調暗至 1% 亮度（黃燈），但保持開啟。"""
        try:
            device = await connect(self.config)
            # 手動修正 KlapProtocol 類型問題
            client = device.client
            import inspect
            if inspect.isclass(client.protocol) or client.protocol is None:
                from plugp100.protocol.klap import klap_handshake_v2
                from plugp100.protocol.klap.klap_protocol import KlapProtocol
                protocol = KlapProtocol(
                    auth_credential=self.credentials,
                    url=f"http://{self.ip_address}/app",
                    klap_strategy=klap_handshake_v2()
                )
                client._protocol = protocol
            
            await device.update()
            print(f"[{self.ip_address}] 進入睡眠待命模式：調暗至 1% 亮度（黃燈）")
            
            # 設為黃色
            await device.turn_on()
            result = await device.set_hue_saturation(60, 100)  # 黃色
            if result.is_failure():
                from plugp100.new.components.light_component import LightComponent
                await device.get_component(LightComponent).set_hue_saturation(60, 100)
            
            # 調暗至 1%
            await device.set_brightness(1)
            print(f"[{self.ip_address}] 睡眠待命模式已啟動（亮度 1%）")
        except Exception as e:
            print(f"[{self.ip_address}] 設定睡眠待命模式失敗: {e}")
    
    def set_sleep_standby(self):
        """啟動睡眠待命模式。"""
        with self._lock:
            asyncio.run(self._set_sleep_standby())

    def is_alerting_state(self):
        """檢查目前是否處於警報顏色狀態 (軟體紀錄)。"""
        # 由於 Tapo API 沒有即時 query 顏色狀態 (或是很慢)，我們這裡暫時回傳 False
        # 主要依賴 StockMonitor 的 alarm_active
        return False

if __name__ == "__main__":
    controller = TapoController()
    print("測試紅燈...")
    controller.turn_on_red()
    import time
    time.sleep(3)
    print("測試關閉...")
    controller.turn_off()
