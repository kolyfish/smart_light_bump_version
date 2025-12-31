import datetime
import time
import requests
import yfinance as yf
import statistics
import threading
from abc import ABC, abstractmethod  

class MarketDataProvider(ABC):
    @abstractmethod
    def get_price(self, symbol):
        pass

    @abstractmethod
    def get_name(self, symbol):
        pass

    @abstractmethod
    def is_market_open(self, symbol):
        pass

class YFinanceProvider(MarketDataProvider):
    def get_price(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            # 優先嘗試 fast_info
            try:
                price = ticker.fast_info.get('last_price')
                if price is not None and price > 0:
                    return price
            except Exception:
                pass
            
            # 嘗試 history
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                return hist['Close'].iloc[-1]
            
            # 最後嘗試 5d history
            hist = ticker.history(period="5d")
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except Exception as e:
            print(f"YFinanceProvider Error: {e}")
        return None

    def get_name(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('longName') or info.get('shortName') or symbol
        except Exception:
            return symbol

    def is_market_open(self, symbol):
        now = datetime.datetime.now()
        if '.TW' in symbol.upper() or '.TWO' in symbol.upper():
            if now.weekday() >= 5:
                return False
            current_time = now.time()
            return datetime.time(9, 0) <= current_time <= datetime.time(13, 30)
        else:
            # 美股概略
            if now.weekday() == 5:
                return now.time() <= datetime.time(6, 0)
            if now.weekday() == 6:
                return False
            if now.weekday() == 0:
                return now.time() >= datetime.time(21, 0)
            current_time = now.time()
            return current_time >= datetime.time(21, 0) or current_time <= datetime.time(6, 0)
 
class BinanceProvider(MarketDataProvider):
    def __init__(self):
        self.current_price = None
        self.last_update_time = 0
        self.ws_thread = None
        self.ws_app = None
        self.running = False
        self.symbol = "BTCUSDT" # Default
        self._lock = threading.Lock()
        
    def _start_ws(self, symbol):
        import websocket
        import json
        
        # 轉換 symbol 格式：BTC-USD -> btcusdt
        clean_symbol = symbol.replace("-", "").lower()
        if clean_symbol.endswith("usd") and not clean_symbol.endswith("usdt"):
            clean_symbol = clean_symbol.replace("usd", "usdt")
            
        url = f"wss://stream.binance.com:9443/ws/{clean_symbol}@trade"
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                price = float(data['p'])
                with self._lock:
                    self.current_price = price
                    self.last_update_time = time.time()
            except Exception as e:
                print(f"WS Message Error: {e}")
                
        def on_error(ws, error):
            print(f"Binance WS Error: {error}")
            
        def on_close(ws, close_status_code, close_msg):
            print("Binance WS Closed")
            
        self.ws_app = websocket.WebSocketApp(url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
                                    
        self.ws_app.run_forever()

    def get_price(self, symbol):
        # 檢查是否需要啟動或切換 WS
        target_symbol = symbol.replace("-", "").upper()
        if target_symbol.endswith("USD"):
            target_symbol = target_symbol.replace("USD", "USDT")
            
        if self.symbol != target_symbol or not self.running:
            if self.ws_thread:
                self.running = False
                if self.ws_app: 
                    try:
                        self.ws_app.close()
                    except:
                        pass
            
            self.symbol = target_symbol
            self.running = True
            self.ws_thread = threading.Thread(target=self._start_ws, args=(symbol,), daemon=True)
            self.ws_thread.start()
            # 給它一點時間連線，先用 REST 抓一次
            return self._fetch_rest_price(symbol)

        # 檢查數據新鮮度 (Staleness Check)
        with self._lock:
            now = time.time()
            if self.current_price and (now - self.last_update_time < 5):
                return self.current_price
            
        # 如果數據過期 (超過 5 秒沒更新)，使用 REST 補救
        # print("DEBUG: Data stale, falling back to REST")
        return self._fetch_rest_price(symbol)

    def _fetch_rest_price(self, symbol):
        try:
            clean_symbol = symbol.replace("-", "").upper()
            if clean_symbol.endswith("USD"):
                clean_symbol = clean_symbol.replace("USD", "USDT")
            
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={clean_symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                with self._lock:
                    self.current_price = price
                    self.last_update_time = time.time()
                return price
        except Exception as e:
            print(f"BinanceREST Error: {e}")
        return None

    def get_name(self, symbol):
        return symbol.split("-")[0].upper() + " (Crypto)"

    def is_market_open(self, symbol):
        return True # Crypto 24/7

class TaiwanStockProvider(MarketDataProvider):
    """
    這是一個使用公開 API 的簡單實作。
    實務上可能需要更穩定的數據源如 Fugle。
    這裡先使用 yfinance 作為 fallback 或特定的 TWSE 介面。
    """
    def __init__(self):
        self.yf = YFinanceProvider()

    def get_price(self, symbol):
        # 這裡可以加入更即時的台股 API 抓取邏輯
        return self.yf.get_price(symbol)

    def get_name(self, symbol):
        return self.yf.get_name(symbol)

    def is_market_open(self, symbol):
        return self.yf.is_market_open(symbol)

class MarketDataAgent:
    def __init__(self):
        self.providers = {
            'yf': YFinanceProvider(),
            'binance': BinanceProvider(),
            'tw': TaiwanStockProvider()
        }
        import os
        self.simulation_mode = os.getenv("SIMULATION_MODE", "false").lower() == "true"
        self.price_history = {} # {symbol: [(timestamp, price)]}
        self.lock = threading.Lock()

    def _select_provider(self, symbol):
        symbol = symbol.upper()
        if "-USD" in symbol or "-BTC" in symbol or symbol.endswith("USDT"):
            return self.providers['binance']
        if ".TW" in symbol or ".TWO" in symbol:
            return self.providers['tw']
        return self.providers['yf']

    def get_market_data(self, symbol):
        provider = self._select_provider(symbol)
        price = provider.get_price(symbol)
        name = provider.get_name(symbol)
        is_open = provider.is_market_open(symbol)
        
        cleaned_price = self._clean_data(symbol, price)
        
        return {
            'symbol': symbol,
            'name': name,
            'price': cleaned_price,
            'is_open': is_open,
            'provider': provider.__class__.__name__
        }

    def _clean_data(self, symbol, new_price):
        if new_price is None or new_price <= 0:
            return None
        
        with self.lock:
            if symbol not in self.price_history:
                self.price_history[symbol] = []
                self.price_history[symbol].append((time.time(), new_price))
                return new_price
            
            history = self.price_history[symbol]
            if not history:
                history.append((time.time(), new_price))
                return new_price
            
            last_price = history[-1][1]
            
            # 數據清洗：如果變動超過 50%，視為異常跳變，除非連續出現。模擬模式下跳過清洗。
            if not self.simulation_mode and abs(new_price - last_price) / last_price > 0.5:
                # 檢查是否連續第二次出現類似價格，如果是，可能真的是大變動
                if len(history) >= 2 and abs(new_price - history[-2][1]) / history[-2][1] > 0.5:
                    pass # 連續兩次異常，可能真的是市場變動
                else:
                    print(f"DEBUG: Detected outlier for {symbol}: {last_price} -> {new_price}. Filtering.")
                    return last_price # 回傳舊價格
            
            history.append((time.time(), new_price))
            # 只保留最近 100 筆
            if len(history) > 100:
                history.pop(0)
            
            return new_price

    def detect_flash_crash(self, symbol, current_price):
        """
        閃崩演算法：
        使用最近 5 分鐘的數據，計算 Z-score 或實質跌幅速度。
        """
        with self.lock:
            if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
                return None
            
            history = self.price_history[symbol]
            now = time.time()
            # 取得最近 1 分鐘的數據
            one_min_data = [p for t, p in history if now - t <= 60]
            
            if len(one_min_data) < 3:
                return None
            
            # 實質跌幅檢查 (1 分鐘內跌超過 1.5%)
            price_start = one_min_data[0]
            drop_rate = (price_start - current_price) / price_start
            
            if drop_rate >= 0.015:
                # 進一步計算 Z-score 增加精確度
                prices = [p for t, p in history]
                if len(prices) >= 2:
                    mean = statistics.mean(prices)
                    std = statistics.stdev(prices)
                    if std > 0:
                        z_score = (current_price - mean) / std
                        print(f"DEBUG FlashCrash: Price={current_price}, Mean={mean:.2f}, Std={std:.2f}, Z={z_score:.2f}, Drop={drop_rate*100:.1f}%")
                        if z_score < -2.0: 
                            return drop_rate
            
            return None
