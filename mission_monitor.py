import sys
import os
import time
import threading
from datetime import datetime

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_monitor import StockMonitor
from mission_listener import MissionListener

class MissionMonitor(StockMonitor):
    def __init__(self, shared_config, tapo_controller):
        super().__init__(shared_config, tapo_controller)
        self.mission_listener = MissionListener()
        self.in_mission_mode = False

    def run(self):
        print("MissionMonitor (BUMP VERSION) 已啟動。")
        self.add_log("=== 正在運行 BUMP 特別版 (支援中央任務控制) ===")
        
        try:
            self.tapo.turn_on_yellow()
        except Exception as e:
            print(f"初始設定黃燈失敗: {e}")

        while self.running:
            try:
                # --- [新增功能] 優先檢查中央任務指令 ---
                if self.mission_listener.is_mission_active():
                    if not self.in_mission_mode:
                        self.add_log("🔵 接獲中央指令：出任務！切換至藍燈待命模式")
                        self.speak("接獲中央指令，任務開始。全體藍燈待命。")
                        self.in_mission_mode = True
                    
                    # 強制藍燈 (覆蓋所有原有邏輯)
                    self.device_off = False
                    self.tapo.set_color("blue", 100) # 假設 TapoController 有通用的 set_color 或新增對應方法
                    # 若 TapoController 沒有 set_color("blue")，可能需要擴充它，這裡先假設用 set_hue_sat 
                    # 藍色 Hue 約 240, Sat 100
                    try:
                        self.tapo.bulb.set_hsv(240, 100, 100) 
                    except:
                        pass
                        
                    time.sleep(2)
                    continue
                else:
                    if self.in_mission_mode:
                        self.add_log("任務結束，恢復正常監控。")
                        self.speak("任務解除，恢復監控。")
                        self.in_mission_mode = False
                        self.tapo.turn_on_yellow()

                # --- 以下為原有的 StockMonitor 邏輯 (複製過來或調用父類邏輯有點難，因為父類是死循環) ---
                # 為了避免複製 400 行代碼導致難維護，這裡我們採用一種「插入式」寫法
                # 但因為父類 run() 是一個 While Loop，我們無法簡單插入。
                # 為了確保功能完全一致，我還是將核心 Loop 複製過來，但您可以考慮 Refactor 原本的 Code 變成 step() 函式
                
                # ... (為了展示清晰，我這裡直接貼上原有邏輯的簡化版，實際運作建議 Refactor 原檔) ...
                
                config = self.shared_config.get_config()
                symbol = config['symbol']
                target = config['target_price']
                stop_loss = config.get('stop_loss_price', 0.0)
                
                # 狀態重置邏輯
                if not hasattr(self, '_last_symbol') or self._last_symbol != symbol:
                    self.alert_mode = None
                    self.last_stock_name = "監控中..."
                    self.last_stock_price = None
                    self._price_history = []
                    self._last_symbol = symbol
                
                if not hasattr(self, '_last_target') or self._last_target != target:
                    self.alert_mode = None
                    self._last_target = target

                self.fetch_market_index()

                if not self.is_crypto(symbol) and not self.is_market_open(symbol):
                    # self.add_log("台股目前休市中，監控暫緩。") 
                    time.sleep(60)
                    continue

                # 數據抓取
                now_ts = time.time()
                current_price = None
                
                if self.mock_current_price is not None:
                    current_price = self.mock_current_price
                    self.data_agent._clean_data(symbol, current_price)
                else:
                    market_data = self.data_agent.get_market_data(symbol)
                    current_price = market_data['price']

                if current_price is None:
                    time.sleep(10)
                    continue

                if self.test_mode_until > time.time():
                    self.last_stock_price = current_price
                    self.last_update_time = datetime.now().strftime("%H:%M:%S")
                    time.sleep(1)
                    continue

                self.last_stock_price = current_price
                self.last_update_time = datetime.now().strftime("%H:%M:%S")
                market_data = self.data_agent.get_market_data(symbol) # Re-fetch name if needed but usually cached
                self.last_stock_name = market_data.get('name', symbol)

                # 閃崩
                drop_rate = self.data_agent.detect_flash_crash(symbol, current_price)
                if drop_rate:
                    self.add_log(f"⚠️ 偵測到閃崩！實質跌幅 {drop_rate*100:.1f}%")
                    self.device_off = False
                    self.tapo.turn_on_purple()
                    self.speak(f"警告，閃崩發生。")
                    time.sleep(5)

                # 警報判定
                if self.alert_mode is None:
                    if current_price < target:
                        self.alert_mode = 'above'
                    else:
                        self.alert_mode = 'below'

                is_alert_hit = False
                is_stop_loss_hit = False

                if stop_loss > 0 and current_price <= stop_loss:
                    is_stop_loss_hit = True

                if self.alert_mode == 'above' and current_price >= target:
                    is_alert_hit = True
                elif self.alert_mode == 'below' and current_price <= target:
                    is_alert_hit = True
                
                if is_stop_loss_hit:
                    now = time.time()
                    if now - self.last_alert_time > self.cooldown_seconds:
                        self.add_log(f"🆘 觸發停損警報")
                        self.device_off = False
                        self.tapo.turn_on_red()
                        if not self.alarm_active:
                            self.alarm_active = True
                            self.alarm_thread = threading.Thread(
                                target=self._continuous_alarm_loop,
                                args=(symbol, current_price, stop_loss, True),
                                daemon=True
                            )
                            self.alarm_thread.start()
                        self.last_alert_time = now
                        
                elif is_alert_hit:
                    now = time.time()
                    if now - self.last_alert_time > self.cooldown_seconds:
                        self.add_log(f"!!! 觸發警報: 達標 !!!")
                        self.device_off = False
                        self.tapo.turn_on_green()
                        if not self.alarm_active:
                            self.alarm_active = True
                            self.alarm_thread = threading.Thread(
                                target=self._continuous_alarm_loop,
                                args=(symbol, current_price, target, False),
                                daemon=True
                            )
                            self.alarm_thread.start()
                        self.last_alert_time = now
                else:
                    if not self.device_off and not self.alarm_active:
                        self.tapo.turn_on_yellow()
                    
                    # 簡易日誌
                    if not hasattr(self, '_log_counter'): self._log_counter = 0
                    self._log_counter += 1
                    if self._log_counter >= 20 or self.last_stock_price != current_price:
                        self.add_log(f"{symbol}: {current_price:.2f} (監控中)")
                        self._log_counter = 0

                sleep_time = 1 if self.simulation_mode else 10
                if self.is_crypto(symbol):
                    sleep_time = 1 if self.simulation_mode else 0.5
                time.sleep(sleep_time)

            except Exception as e:
                print(f"監控迴圈出錯: {e}")
                time.sleep(1)
