import time

# 模擬 StockMonitor 的部分行為
class MockTapo:
    def turn_on_purple(self):
        print("💡 [硬體] 紫燈已亮起 (Purple Light ON)")

class MockMonitor:
    def __init__(self):
        self.data_agent = MarketDataAgent()
        self.data_agent.simulation_mode = True # 跳過 50% 過濾
        self.tapo = MockTapo()
        self.last_stock_name = "測試股"

    def add_log(self, msg):
        print(f"📝 [日誌] {msg}")

    def speak(self, msg):
        print(f"🗣️ [語音] {msg}")

    def run_test(self):
        symbol = "TEST"
        # 模擬平穩數據
        prices = [100.1, 99.9, 100.2, 99.8, 100.0, 100.1]
        for p in prices:
            self.data_agent._clean_data(symbol, p)
            time.sleep(0.1)
        
        # 模擬閃崩
        crash_price = 90.0
        self.data_agent._clean_data(symbol, crash_price)
        
        drop_rate = self.data_agent.detect_flash_crash(symbol, crash_price)
        if drop_rate:
            self.add_log(f"⚠️ 偵測到閃崩！實質跌幅 {drop_rate*100:.1f}%")
            self.tapo.turn_on_purple()
            self.speak(f"警告，{self.last_stock_name} 偵測到恐慌性閃崩，目前跌幅百分之 {drop_rate*100:.1f}。")
        else:
            print("❌ 未觸發閃崩 (檢查 Z-score 設定)")

m = MockMonitor()
m.run_test()
