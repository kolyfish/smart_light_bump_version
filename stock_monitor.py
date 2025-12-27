import time
import threading
import yfinance as yf
import subprocess
from datetime import datetime
from market_data_agent import MarketDataAgent

class StockMonitor(threading.Thread):
    def __init__(self, shared_config, tapo_controller):
        super().__init__()
        self.shared_config = shared_config
        self.tapo = tapo_controller
        self.running = True
        self.daemon = True
        import os
        self.simulation_mode = os.getenv("SIMULATION_MODE", "false").lower() == "true"
        self.last_alert_time = 0
        self.cooldown_seconds = 300  # 5 分鐘
        self.test_mode_until = 0     # 新增：測試模式暫停時間戳記
        self.log_messages = [] # 新增：日誌緩存
        self.max_logs = 50     # 最多保留 50 條日誌
        
        # 數據緩存
        self.last_stock_price = None
        self.last_stock_name = "監控中..."
        self.last_market_index = None
        self.last_market_change = None
        self.last_update_time = "尚未更新"
        self.device_off = False  # 追蹤硬體是否被使用者手動關閉
        self.alert_mode = None   # 'above' 或 'below'，自動判定
        self._price_history = [] # 儲存最近幾分鐘的價格，偵測閃崩
        self.alarm_active = False  # 警報是否正在響起（持續播報中）
        self.alarm_thread = None   # 警報播報執行緒
        self.mock_current_price = None  # 用於自動化測試模擬數據
        self.data_agent = MarketDataAgent() # 新增：行情監控代理
        
        # 初始化 TTS 元件
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        except Exception as e:
            print(f"TTS 初始化失敗 (將改用系統原生語音): {e}")
            self.engine = None

    def is_crypto(self, symbol):
        """判斷是否為虛擬貨幣。"""
        return "-USD" in symbol.upper() or "-BTC" in symbol.upper() or symbol.upper().endswith("USDT")

    def is_market_open(self, symbol=None):
        """判斷市場是否在交易時間。委派給 MarketDataAgent。模擬模式下恆為真。"""
        if self.simulation_mode:
            return True
            
        if not symbol:
            config = self.shared_config.get_config()
            symbol = config['symbol']
        return self.data_agent._select_provider(symbol).is_market_open(symbol)

    def get_market_status_text(self):
        """取得市場狀態的文字描述。"""
        config = self.shared_config.get_config()
        symbol = config.get('symbol', '2330.TW')
        
        is_open = self.is_market_open(symbol)
        
        if self.is_crypto(symbol):
            return "虛擬貨幣 24/7 交易中 🟢"
            
        if '.TW' in symbol.upper() or '.TWO' in symbol.upper():
            return "台股交易中 🟢" if is_open else "台股收盤/未開盤 🔴"
        else:
            return "美股交易中 🟢" if is_open else "美股收盤/未開盤 🔴"

    def fetch_market_index(self):
        """抓取台股大盤指數 (^TWII)，優先使用 fast_info，失敗則使用 history。"""
        try:
            twii = yf.Ticker("^TWII")
            info = twii.fast_info
            price = info.get('last_price')
            
            if price is None:
                # 嘗試使用 history
                hist = twii.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            
            self.last_market_index = price
            
            # 獲取今日漲跌 (如果有的話)
            prev_close = info.get('previous_close')
            if price and prev_close:
                self.last_market_change = price - prev_close
        except Exception as e:
            print(f"抓取大盤指數失敗: {e}")

    def speak(self, text):
        """朗讀文字，優先使用 pyttsx3，失敗則調用 Mac 原生 say 指令。"""
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                print(f"pyttsx3 朗讀出錯: {e}")
        
        # Mac 原生 fallback
        try:
            subprocess.run(["say", text])
        except Exception as e:
            print(f"原生語音指令執行失敗: {e}")

    def add_log(self, message):
        """將日誌加入緩存，供 Web 端讀取。"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry) # 同步保存在終端機顯示
        self.log_messages.append(log_entry)
        if len(self.log_messages) > self.max_logs:
            self.log_messages.pop(0)

    def trigger_demo_alert(self):
        """執行全功能示範：依序展示紅、黃、綠燈 + 語音說明。"""
        import time
        self.device_off = False # 演示時恢復通訊
        self.add_log("開始執行全功能演示...")
        
        try:
            # 1. 紅燈 - 警示狀態
            self.add_log("演示：紅燈（警示/停損）")
            self.tapo.turn_on_red()
            self.speak("紅燈，代表停損警示或系統異常。")
            time.sleep(3)
            
            # 2. 黃燈 - 監控中
            self.add_log("演示：黃燈（常態監控）")
            self.tapo.turn_on_yellow()
            self.speak("黃燈，代表系統正常監控中。")
            time.sleep(3)
            
            # 3. 綠燈 - 達標提醒
            self.add_log("演示：綠燈（目標達成）")
            self.tapo.turn_on_green()
            self.speak("綠燈，代表股價已達到您設定的目標價格。")
            time.sleep(3)
            
            # 4. 回到黃燈
            self.add_log("演示完成，恢復監控狀態")
            self.tapo.turn_on_yellow()
            self.speak("演示完成，系統已恢復正常監控。")
            
        except Exception as e:
            self.add_log(f"演示過程出錯: {e}")
        
        return True

    def _continuous_alarm_loop(self, symbol, current_price, target_price, is_stop_loss=False):
        """持續播報警報直到使用者按下停止按鈕"""
        import time
        
        # 準備播報內容
        if self.is_crypto(symbol):
            crypto_name = symbol.split("-")[0]
            spaced_symbol = " ".join(list(crypto_name))
            if is_stop_loss:
                alert_msg = f"緊急警報！虛擬貨幣 {spaced_symbol} 目前價格 {current_price:.2f} 美元，已跌破停損價 {target_price:.2f} 美元。請立即停損。"
            else:
                alert_msg = f"緊急警報！虛擬貨幣 {spaced_symbol} 目前價格 {current_price:.2f} 美元，已達到您設定的目標價格 {target_price:.2f} 美元。請立即查看。"
        else:
            spaced_symbol = " ".join(list(symbol.split(".")[0]))
            if is_stop_loss:
                alert_msg = f"緊急警報！股票代號 {spaced_symbol} 目前價格 {current_price:.1f}，已跌破停損價 {target_price:.1f}。請立即停損。"
            else:
                alert_msg = f"緊急警報！股票代號 {spaced_symbol} 目前價格 {current_price:.1f}，已達到您設定的目標價格 {target_price:.1f}。請立即查看。"
        
        self.add_log("🔔 開始持續警報播報...")
        
        # 持續播報直到停止
        while self.alarm_active:
            self.speak(alert_msg)
            time.sleep(10)  # 每10秒播報一次
            
        self.add_log("🔕 警報已停止")

    def stop_alarm(self):
        """停止警報播報（像鬧鐘的停止按鈕）"""
        if self.alarm_active:
            self.alarm_active = False
            self.add_log("使用者已停止警報播報")
            # 恢復黃燈監控狀態
            if not self.device_off:
                self.tapo.turn_on_yellow()
            return True
        return False

    def run(self):
        print("StockMonitor 已啟動。")
        # 初始狀態：顯示黃色，表示待機/監控中 (使用者要求的常態色)
        try:
            self.tapo.turn_on_yellow()
        except Exception as e: # E722 is not applicable here
            print(f"初始設定黃燈失敗: {e}")

        while self.running:
            try:
                config = self.shared_config.get_config()
                symbol = config['symbol']
                target = config['target_price']
                stop_loss = config.get('stop_loss_price', 0.0)
                
                # 如果代號或目標價變更，重置警報模式與價格緩存
                if not hasattr(self, '_last_symbol') or self._last_symbol != symbol:
                    self.alert_mode = None
                    self.last_stock_name = "監控中..."
                    self.last_stock_price = None  # 同時清除舊價格
                    self._price_history = []      # 清除舊股票的價格歷史，防止誤判閃崩
                    self._last_symbol = symbol
                
                if not hasattr(self, '_last_target') or self._last_target != target:
                    self.alert_mode = None
                    self._last_target = target

                # 無論是否休市都更新一次大盤（休市時顯示最後價格）
                self.fetch_market_index()

                # 如果是台股且休市，則降低檢查頻率
                if not self.is_crypto(symbol) and not self.is_market_open(symbol):
                    self.add_log("台股目前休市中，監控暫緩。")
                    time.sleep(60)
                    continue

                # 獲取監控個股數據
                try:
                    now_ts = time.time()
                    current_price = None
                    market_data = {}

                    # 如果有模擬數據（用於自動化測試），優先使用並跳過實體抓取
                    if self.mock_current_price is not None:
                        current_price = self.mock_current_price
                        self.add_log(f"系統：正在使用模擬數據測試現價 {current_price:.2f}")
                        self.data_agent._clean_data(symbol, current_price)
                        market_data = {'name': symbol, 'price': current_price}
                    else:
                        market_data = self.data_agent.get_market_data(symbol)
                        current_price = market_data['price']

                    if current_price is None:
                        self.add_log(f"無法獲取 {symbol} 股價 (市場休市或 API 異常)")
                        time.sleep(10)
                        continue

                    # 如果測試模式啟用中，則暫停自動燈號控制
                    if self.test_mode_until > time.time():
                        # 僅更新數據，不操作 Tapo
                        self.last_stock_price = current_price
                        self.last_update_time = datetime.now().strftime("%H:%M:%S")
                        time.sleep(1)
                        continue

                    self.last_stock_price = current_price
                    self.last_update_time = datetime.now().strftime("%H:%M:%S")
                    self.last_stock_name = market_data.get('name', symbol)

                    # --- 閃崩偵測 (Purple Light) ---
                    drop_rate = self.data_agent.detect_flash_crash(symbol, current_price)
                    if drop_rate:
                        self.add_log(f"⚠️ 偵測到閃崩！實質跌幅 {drop_rate*100:.1f}%")
                        self.device_off = False # 強制喚醒
                        self.tapo.turn_on_purple()
                        self.speak(f"警告，{self.last_stock_name} 偵測到恐慌性閃崩，目前跌幅百分之 {drop_rate*100:.1f}。")
                        time.sleep(5)

                    # --- 數據異常診斷 (Red Light part 1) ---
                    # 如果能跑到這代表抓到資料了

                    # 自動判定警報模式 (第一次抓到價格，或設定變更後)
                    if self.alert_mode is None:
                        if current_price < target:
                            self.alert_mode = 'above' # 目前低於目標，監控「漲破」
                            self.add_log(f"警報模式：設定為「等待觸價」 {target} (現價 {current_price:.2f})")
                        else:
                            self.alert_mode = 'below' # 目前高於目標，監控「跌破」
                            self.add_log(f"警報模式：設定為「等待觸價」 {target} (現價 {current_price:.2f})")

                    # 檢查警報是否達成
                    is_alert_hit = False
                    is_stop_loss_hit = False

                    # --- 停損監控 (Red Light part 2) ---
                    if stop_loss > 0 and current_price <= stop_loss:
                        is_stop_loss_hit = True

                    if self.alert_mode == 'above' and current_price >= target:
                        is_alert_hit = True
                    elif self.alert_mode == 'below' and current_price <= target:
                        is_alert_hit = True
                    
                    if is_stop_loss_hit:
                        now = time.time()
                        # 停損也共用冷卻時間，避免無限連環爆
                        if now - self.last_alert_time > self.cooldown_seconds:
                            self.add_log(f"🆘 觸發停損警報: {symbol} 跌破停損價 {stop_loss} ({current_price:.2f})")
                            self.device_off = False
                            self.tapo.turn_on_red()
                            
                            # 啟動持續警報播報 (帶入 is_stop_loss=True)
                            if not self.alarm_active:
                                self.alarm_active = True
                                self.alarm_thread = threading.Thread(
                                    target=self._continuous_alarm_loop,
                                    args=(symbol, current_price, stop_loss, True),
                                    daemon=True
                                )
                                self.alarm_thread.start()

                            self.last_alert_time = now # 更新冷卻時間
                            
                    elif is_alert_hit:
                        now = time.time()
                        if now - self.last_alert_time > self.cooldown_seconds:
                            self.add_log(f"!!! 觸發警報: {symbol} 已達標 ({current_price:.2f}) !!!")
                            self.device_off = False # 強制喚醒
                            self.tapo.turn_on_green()  # 直接亮綠燈，不管是否在睡眠模式
                            
                            # 啟動持續警報播報
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
                        # 未達標時，若裝置未關閉（非睡眠模式）且無持續警報中，才維持黃燈
                        if not self.device_off and not self.alarm_active:
                            self.tapo.turn_on_yellow()
                        # 降低日誌頻率：只有當價格變動，或每隔 20 次迴圈 (約 10秒) 才顯示一次
                        if not hasattr(self, '_log_counter'): self._log_counter = 0
                        self._log_counter += 1
                        
                        should_log = False
                        if self._log_counter >= 20:
                            should_log = True
                            self._log_counter = 0
                        elif self.last_stock_price != current_price:
                            should_log = True
                            self._log_counter = 0 # 重置計數

                        if should_log:
                            self.add_log(f"{symbol}: {current_price:.2f} (目標 {target} | 停損 {stop_loss} | 監控中)")

                except Exception as e:
                    self.add_log(f"數據抓取或警報診斷異常: {e}")
                    # --- 異常診斷 (Red Light part 3) ---
                    if not self.device_off:
                        self.tapo.turn_on_red()
                        self.add_log("系統診斷：無法取得數據，切換為紅燈警示。")
                
                # 決定下次檢查的時間間隔
                # Hybrid Architecture Optimization:
                # Crypto (Websockets) -> 本地記憶體讀取，可以極快 (0.5秒)
                # Stock (REST) -> 避免 Rate Limit，維持 10秒
                if self.is_crypto(symbol):
                    sleep_time = 1 if self.simulation_mode else 0.5
                else:
                    sleep_time = 1 if self.simulation_mode else 10
                
                time.sleep(sleep_time)

            except Exception as e:
                print(f"監控迴圈出錯: {e}")
                time.sleep(1)

    def stop(self):
        self.running = False
